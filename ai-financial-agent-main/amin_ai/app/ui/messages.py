"""Message display components."""

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage


def render_previous_messages(messages: list):
    """Render all previous messages in the chat."""
    for message in messages:
        if isinstance(message, HumanMessage):
            with st.chat_message("user", avatar="👤"):
                st.markdown(message.content)
        elif isinstance(message, AIMessage):
            with st.chat_message("assistant", avatar="✨"):
                st.markdown(message.content)


def render_user_message(content: str, uploaded_files: list = None):
    """Render a new user message."""
    with st.chat_message("user", avatar="👤"):
        st.markdown(content)
        
        if uploaded_files:
            for file in uploaded_files:
                st.caption(f"📄 {file.name}")


def render_main_header():
    """Render the main page header."""
    st.markdown(
        """
        <div style="
            margin-top: -59px;
            margin-bottom: 8px;
            font-size: 2.15rem;
            font-weight: 700;
            letter-spacing: -0.8px;
        ">
            ✨ AskX
        </div>

        <div class="main-subtitle">
            Your Agentic AI assistant with tools, RAG,
            memory, web search, calculations, weather,
            and more.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer():
    """Render the page footer."""
    st.divider()
    st.caption(
        "Powered by LangChain • LangGraph • Streamlit"
    )
