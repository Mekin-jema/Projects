"""Helper functions for the UI."""

import asyncio
from langchain_core.messages import HumanMessage
from app.monitoring import get_logger
from app.workflow import get_thread_messages


logger = get_logger("streamlit-ui")


def load_thread_messages(thread_id):
    """Load one conversation from the SQLite checkpoint store."""
    try:
        return asyncio.run(get_thread_messages(thread_id))
    except Exception as error:
        logger.warning(
            "Could not load thread",
            extra={"extra_data": {"error": str(error)}},
        )
        return []


def thread_title(messages, thread_id=None):
    """Create a clean readable title from the first user message."""
    for message in messages:
        if isinstance(message, HumanMessage) and message.content:
            title = " ".join(str(message.content).split()).strip()
            
            if len(title) <= 45:
                return title
            
            shortened = title[:45].rsplit(" ", 1)[0]
            return shortened + "..."
    
    return "New chat"
