"""Streamlit UI for the AskX AI Chatbot."""

# ============================================================================
# SSL
# ============================================================================

import sys
from pathlib import Path

import truststore
truststore.inject_into_ssl()


# ============================================================================
# PROJECT PATH
# ============================================================================

project_root = Path(__file__).resolve().parents[2]

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


# ============================================================================
# STREAMLIT & CORE IMPORTS
# ============================================================================

import streamlit as st

from app import (
    get_logger,
    ProductionAgent,
    MetricsCollector,
    ResponseCache,
    SecurityPipeline,
    get_settings,
)

# ============================================================================
# UI MODULES
# ============================================================================

from app.ui.config import setup_page
from app.ui.session import initialize_session_state
from app.ui.sidebar import render_sidebar
from app.ui.messages import render_main_header, render_footer, render_previous_messages, render_user_message
from app.ui.pdf_handler import handle_pdf_upload
from app.ui.chat import handle_chat_message


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

setup_page()


# ============================================================================
# SHARED APPLICATION COMPONENTS
# ============================================================================

@st.cache_resource
def get_app_components():
    """Create shared production components once per Streamlit process."""

    settings = get_settings()

    return (
        SecurityPipeline(),
        ResponseCache(ttl_seconds=settings.cache_ttl_seconds),
        MetricsCollector(),
        ProductionAgent(),
        get_logger("streamlit-ui"),
    )


security, cache, metrics, agent, logger = get_app_components()


# ============================================================================
# INITIALIZE SESSION STATE
# ============================================================================

initialize_session_state()


# ============================================================================
# RENDER SIDEBAR
# ============================================================================

render_sidebar(cache)


# ============================================================================
# MAIN HEADER
# ============================================================================

render_main_header()


# ============================================================================
# DISPLAY PREVIOUS MESSAGES
# ============================================================================

render_previous_messages(st.session_state.messages)


# ============================================================================
# CHAT INPUT
# ============================================================================

prompt_data = st.chat_input(
    "Message AskX...",
    accept_file="multiple",
    file_type=["pdf"],
)


# ============================================================================
# HANDLE USER MESSAGE
# ============================================================================

if prompt_data:
    
    # Extract prompt and files
    if hasattr(prompt_data, "text"):
        prompt = prompt_data.text or ""
        uploaded_files = prompt_data.files or []
    else:
        # Compatibility with older Streamlit versions
        prompt = str(prompt_data)
        uploaded_files = []
    
    # Handle PDF uploads
    if uploaded_files:
        pdf_processed = handle_pdf_upload(uploaded_files)
    else:
        pdf_processed = False
    
    # If only PDF uploaded, don't continue
    if not prompt.strip():
        if uploaded_files:
            st.info(
                "Your PDF is ready. "
                "Ask me a question about it."
            )
        st.stop()
    
    # Handle chat message
    handle_chat_message(
        prompt,
        uploaded_files if uploaded_files else None,
        security,
        cache,
        metrics,
    )


# ============================================================================
# FOOTER
# ============================================================================

render_footer()