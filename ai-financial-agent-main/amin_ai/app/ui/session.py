"""Session state management."""

import uuid
import streamlit as st


def initialize_session_state():
    """Initialize all session state variables."""
    
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "last_request_at" not in st.session_state:
        st.session_state.last_request_at = 0.0
    
    if "document_hash" not in st.session_state:
        st.session_state.document_hash = None
    
    if "document_name" not in st.session_state:
        st.session_state.document_name = None


def new_chat():
    """Start a new chat conversation."""
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.document_hash = None
    st.session_state.document_name = None
    st.rerun()


def clear_chat():
    """Clear current chat messages."""
    st.session_state.messages = []
    st.rerun()
