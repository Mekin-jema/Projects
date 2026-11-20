"""API-facing wrapper around the unified chatbot workflow."""

from app.workflow import get_chatbot


class ProductionAgent:
    """Invoke the shared tool-enabled workflow for API requests."""

    def invoke(self, message: str, thread_id: str = "default") -> dict:
        """Process a message and return the API-compatible response payload."""
        result = get_chatbot.invoke(
            {"messages": [{"type": "human", "content": message}]},
            config={"configurable": {"thread_id": thread_id}},
        )
        return {
            "response": result["messages"][-1].content,
            "model_used": result.get("model_used", "unknown"),
            "error": result.get("error"),
        }
