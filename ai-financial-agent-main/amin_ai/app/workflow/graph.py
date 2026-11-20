"""Unified LangGraph workflow for tools, retries, and conversation memory."""

from pathlib import Path
from contextlib import asynccontextmanager

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from app.config import get_settings
from app.core import tools
from app.workflow.state import AgentState


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

DB_PATH = Path("data/chatbot.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# System message
# ---------------------------------------------------------------------------

SYSTEM_MESSAGE = SystemMessage(
    content=(
        "You are a helpful Agentic Chatbot with access to several tools.\n\n"
        "Use rag_tool for uploaded PDF questions, "
        "search_tool for current information, "
        "calculator for mathematics, "
        "get_stock_price for stock prices, and "
        "get_current_weather for current weather.\n\n"
        "Answer general questions directly.\n"
        "Do not invent information from uploaded documents.\n"
        "When a PDF is uploaded, use rag_tool when the question "
        "requires information from that document."
    )
)


# ---------------------------------------------------------------------------
# Build graph
# ---------------------------------------------------------------------------

def create_graph():
    """Create the LangGraph workflow."""

    settings = get_settings()

    # -----------------------------------------------------------------------
    # Primary model
    # -----------------------------------------------------------------------

    primary_llm = ChatOpenAI(
        model=settings.primary_model,
        temperature=0,
        timeout=30,
        max_retries=0,
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
    ).bind_tools(tools)

    # -----------------------------------------------------------------------
    # Fallback model
    # -----------------------------------------------------------------------

    fallback_llm = ChatOpenAI(
        model=settings.fallback_model,
        temperature=0,
        timeout=30,
        max_retries=0,
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
    ).bind_tools(tools)

    # -----------------------------------------------------------------------
    # Process message
    # -----------------------------------------------------------------------

    def process_message(state: AgentState) -> dict:
        """Process a message using the primary model."""

        try:
            response = primary_llm.invoke(
                [
                    SYSTEM_MESSAGE,
                    *state["messages"],
                ]
            )

            return {
                "messages": [response],
                "error": None,
                "model_used": "primary",
            }

        except Exception as error:
            return {
                "error": str(error),
                "retry_count": state.get("retry_count", 0) + 1,
                "model_used": "",
            }

    # -----------------------------------------------------------------------
    # Tools
    # -----------------------------------------------------------------------

    tool_node = ToolNode(tools)

    def execute_tools(state: AgentState) -> dict:
        """Execute tool calls requested by the model."""

        return tool_node.invoke(state)

    # -----------------------------------------------------------------------
    # Fallback
    # -----------------------------------------------------------------------

    def try_fallback(state: AgentState) -> dict:
        """Use the fallback model after primary model failure."""

        try:
            response = fallback_llm.invoke(
                [
                    SYSTEM_MESSAGE,
                    *state["messages"],
                ]
            )

            return {
                "messages": [response],
                "error": None,
                "model_used": "fallback",
            }

        except Exception as error:
            return {
                "error": str(error),
                "model_used": "",
            }

    # -----------------------------------------------------------------------
    # Error handler
    # -----------------------------------------------------------------------

    def handle_error(state: AgentState) -> dict:
        """Return a stable response when all model attempts fail."""

        return {
            "messages": [
                AIMessage(
                    content=(
                        "I'm sorry, I'm having trouble processing your "
                        "request right now. Please try again in a moment."
                    )
                )
            ],
            "error": None,
            "model_used": "error_handler",
        }

    # -----------------------------------------------------------------------
    # Routing
    # -----------------------------------------------------------------------

    def route_after_process(state: AgentState) -> str:

        # Primary model failed
        if state.get("error") is not None:

            if state.get("retry_count", 0) < settings.max_retries:
                return "fallback"

            return "error"

        # Model requested a tool
        if getattr(state["messages"][-1], "tool_calls", None):
            return "tools"

        # Normal answer
        return "done"

    def route_after_fallback(state: AgentState) -> str:

        if state.get("error") is None:
            return "done"

        return "error"

    # -----------------------------------------------------------------------
    # Graph
    # -----------------------------------------------------------------------

    graph = StateGraph(AgentState)

    graph.add_node(
        "process",
        process_message,
    )

    graph.add_node(
        "tools",
        execute_tools,
    )

    graph.add_node(
        "fallback",
        try_fallback,
    )

    graph.add_node(
        "error",
        handle_error,
    )

    # START -> process
    graph.add_edge(
        START,
        "process",
    )

    # process -> tools / fallback / END / error
    graph.add_conditional_edges(
        "process",
        route_after_process,
        {
            "tools": "tools",
            "done": END,
            "fallback": "fallback",
            "error": "error",
        },
    )

    # tools -> process
    graph.add_edge(
        "tools",
        "process",
    )

    # fallback -> END / error
    graph.add_conditional_edges(
        "fallback",
        route_after_fallback,
        {
            "done": END,
            "error": "error",
        },
    )

    # error -> END
    graph.add_edge(
        "error",
        END,
    )

    return graph


# ---------------------------------------------------------------------------
# Async chatbot context manager
# ---------------------------------------------------------------------------

@asynccontextmanager
async def get_chatbot():
    """
    Create the async SQLite checkpointer and compile the graph.

    AsyncSqliteSaver is required because the Streamlit UI uses
    chatbot.astream_events().
    """

    graph = create_graph()

    async with AsyncSqliteSaver.from_conn_string(
        str(DB_PATH)
    ) as checkpoint:

        await checkpoint.setup()

        chatbot = graph.compile(
            checkpointer=checkpoint
        )

        yield chatbot


# ---------------------------------------------------------------------------
# Thread helpers
# ---------------------------------------------------------------------------

async def get_all_threads():
    """
    Return all thread IDs, with the most recently active
    thread at the top.
    """

    async with AsyncSqliteSaver.from_conn_string(
        str(DB_PATH)
    ) as checkpoint:

        await checkpoint.setup()

        cursor = await checkpoint.conn.execute("""
            SELECT
                thread_id,
                MAX(rowid) AS latest_row
            FROM checkpoints
            GROUP BY thread_id
            ORDER BY latest_row DESC;
        """)

        rows = await cursor.fetchall()

        return [row[0] for row in rows]


async def get_thread_messages(thread_id: str):
    """Return the persisted messages for a thread, or an empty list."""
    graph = create_graph()

    async with AsyncSqliteSaver.from_conn_string(
        str(DB_PATH)
    ) as checkpoint:

        await checkpoint.setup()

        compiled_graph = graph.compile(
            checkpointer=checkpoint
        )

        snapshot = await compiled_graph.aget_state(
            {
                "configurable": {
                    "thread_id": thread_id
                }
            }
        )

        return snapshot.values.get("messages", [])