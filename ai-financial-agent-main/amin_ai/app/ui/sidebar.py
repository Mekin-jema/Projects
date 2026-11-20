"""Sidebar navigation and thread management."""

import asyncio
import streamlit as st
from app.ui.helpers import load_thread_messages, thread_title
from app.ui.session import new_chat, clear_chat
from app.workflow import get_all_threads
from app.monitoring import get_logger
from app.cache import ResponseCache


logger = get_logger("streamlit-ui")


def render_brand():
    """Render the sidebar brand/logo."""
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
         Your AI assistant for tools, RAG, memory, and web search.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_new_chat_button():
    """Render the 'New chat' button."""
    st.markdown(
        '<div class="new-chat">',
        unsafe_allow_html=True,
    )
    
    if st.button(
        "✎  New chat",
        key="new_chat_button",
        use_container_width=True,
    ):
        new_chat()
    
    st.markdown("</div>", unsafe_allow_html=True)


def render_thread_list():
    """Render the list of conversation threads."""
    
    # Load threads
    try:
        thread_ids = asyncio.run(get_all_threads())
    except Exception as error:
        logger.warning(
            "Could not load conversations",
            extra={"extra_data": {"error": str(error)}},
        )
        thread_ids = []
    
    # Add current thread if new
    if st.session_state.thread_id not in thread_ids:
        thread_ids.append(st.session_state.thread_id)
    
    # Reverse for newest first
    ordered_thread_ids = list(reversed(thread_ids))
    
    # Render threads
    if ordered_thread_ids:
        st.markdown(
            '<div class="chat-list">',
            unsafe_allow_html=True,
        )
        
        for thread_id in ordered_thread_ids:
            # Load messages
            if thread_id == st.session_state.thread_id:
                thread_messages = st.session_state.messages
            else:
                thread_messages = load_thread_messages(thread_id)
            
            # Generate title
            title = thread_title(thread_messages, thread_id)
            
            # Check if active
            is_active = thread_id == st.session_state.thread_id
            css_class = "thread-active" if is_active else "thread-normal"
            
            # Render thread
            st.markdown(
                f'<div class="{css_class}">',
                unsafe_allow_html=True,
            )
            
            if st.button(
                f"💬  {title}",
                key=f"thread_{thread_id}",
                use_container_width=True,
            ):
                if thread_id != st.session_state.thread_id:
                    st.session_state.thread_id = thread_id
                    st.session_state.messages = thread_messages
                    st.session_state.document_hash = None
                    st.session_state.document_name = None
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            """
<div class="empty-conversations">
    Your conversations will appear here.
</div>
""",
            unsafe_allow_html=True,
        )


def render_document_card():
    """Render the current document card if one is loaded."""
    if st.session_state.document_name:
        st.markdown(
            """
<div class="sidebar-section-title">
    Current document
</div>
""",
            unsafe_allow_html=True,
        )
        
        st.markdown(
            f"""
<div class="document-card">
    📄 {st.session_state.document_name}
</div>
""",
            unsafe_allow_html=True,
        )


def render_system_status(cache: ResponseCache):
    """Render system status information."""
    st.markdown(
        """
<div class="sidebar-section-title">
    System
</div>
""",
        unsafe_allow_html=True,
    )
    
    try:
        st.markdown(
            f"""
<div class="system-status">
    ⚡ Cache hit rate · {cache.stats['hit_rate']}
</div>
""",
            unsafe_allow_html=True,
        )
    except Exception:
        pass


def render_sidebar(cache: ResponseCache):
    """Render the complete sidebar."""
    with st.sidebar:
        # Brand
        render_brand()
        
        # New chat button
        render_new_chat_button()
        
        # Chats title
        st.markdown(
            """
<div class="sidebar-section-title">
    Chats
</div>
""",
            unsafe_allow_html=True,
        )
        
        # Thread list
        render_thread_list()
        
        # Bottom section
        st.divider()
        
        # Clear chat
        st.markdown(
            '<div class="clear-chat">',
            unsafe_allow_html=True,
        )
        
        if st.button(
            "🗑  Clear current chat",
            key="clear_chat_button",
            use_container_width=True,
        ):
            clear_chat()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Document card
        render_document_card()
        
        # System status
        render_system_status(cache)
        
        # Footer
        st.markdown(
            """
<div class="sidebar-footer">
    AskX · Agentic AI Assistant
</div>
""",
            unsafe_allow_html=True,
        )
