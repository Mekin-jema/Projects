import os
import truststore

# ============================================================
# SYSTEM SSL CERTIFICATE
# ============================================================

# Use the Windows/system certificate store.
# Important for corporate networks and SSL inspection.
truststore.inject_into_ssl()


# ============================================================
# IMPORTS
# ============================================================

from dotenv import load_dotenv

from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv(
    "OPENROUTER_BASE_URL",
    "https://openrouter.ai/api/v1",
)
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


# ============================================================
# VALIDATE ENVIRONMENT
# ============================================================

if not OPENROUTER_API_KEY:
    raise ValueError(
        "OPENROUTER_API_KEY is missing. "
        "Add it to your .env file."
    )


# ============================================================
# CUSTOM TOOLS
# ============================================================

@tool
def calculator(expression: str) -> str:
    """
    Calculate a mathematical expression.

    Example:
    25 * 4
    100 / 5
    2 ** 10
    """

    try:
        # Simple calculator for basic mathematical expressions.
        allowed_characters = "0123456789+-*/().% "

        if not all(
            character in allowed_characters
            for character in expression
        ):
            return "Invalid mathematical expression."

        result = eval(expression, {"__builtins__": {}}, {})

        return str(result)

    except Exception as error:
        return f"Calculation error: {error}"


@tool
def get_current_time(city: str) -> str:
    """
    Return a simple response about the requested city.

    This is a placeholder tool for demonstrating
    how custom LangChain tools work.
    """

    return (
        f"Current time lookup requested for {city}. "
        "Connect this tool to a real time API for live data."
    )


# Initialize Tavily search tool if API key is provided
search_tool = TavilySearchResults(
    api_key=TAVILY_API_KEY,
    max_results=3,
)


# ============================================================
# TOOL LIST
# ============================================================

tools = [
    calculator,
    get_current_time,
    search_tool,
]


# ============================================================
# REACT PROMPT
# ============================================================

prompt_template = """You are a helpful AI assistant.

You have access to the following tools:

{tools}

To answer the user's question, you MUST strictly use the following format. Do not output anything else:

Question: the input question you must answer
Thought: you must always think about what to do. If no tool is needed to answer the question, you MUST write: "Thought: I can answer this directly without tools." followed immediately by a "Final Answer: [your response]".
Action: the action to take, must be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (Thought/Action/Action Input/Observation can repeat)
Thought: I now know the final answer
Final Answer: the final answer to the user

Begin!

Question: {input}
Thought: {agent_scratchpad}"""

prompt = PromptTemplate.from_template(prompt_template)


# ============================================================
# LLM
# ============================================================

llm = ChatOpenAI(
    model="openai/gpt-4.1-mini",
    api_key=OPENROUTER_API_KEY,
    base_url=OPENROUTER_BASE_URL,
    temperature=0,
    max_tokens=500,
)


# ============================================================
# CREATE AGENT
# ============================================================

agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt,
)


# ============================================================
# AGENT EXECUTOR
# ============================================================

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=5,
)


# ============================================================
# PUBLIC FUNCTION FOR STREAMLIT
# ============================================================

def ask_agent(question: str) -> str:
    """
    Send a question to the LangChain agent.
    """

    response = agent_executor.invoke(
        {
            "input": question
        }
    )

    return response["output"]


# ============================================================
# TERMINAL TEST
# ============================================================

if __name__ == "__main__":
    question = input("Ask the AI: ")
    answer = ask_agent(question)
    print("\nFinal Answer:")
    print(answer)
