"""UI configuration and styling."""

import streamlit as st


CSS_STYLES = """
<style>

/* =========================================================================
   SIDEBAR
   ========================================================================= */

section[data-testid="stSidebar"] {
    width: 200px !important;
    min-width: 230px !important;
    max-width: 290px !important;
}

/* =========================================================================
   SIDEBAR INNER CONTAINER
   ========================================================================= */

section[data-testid="stSidebar"] > div {
    padding: 8px 10px 10px 10px !important;
}

/* =========================================================================
   SIDEBAR BRAND / LOGO (top-left, ChatGPT-style)
   ========================================================================= */

.sidebar-brand {
    display: flex !important;
    align-items: center !important;
    gap: 9px !important;
    width: 100% !important;
    padding: 6px 6px 14px 4px !important;
    margin: 0 !important;
    text-align: left !important;
}

.sidebar-brand-mark {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    flex-shrink: 0 !important;
    width: 28px !important;
    height: 28px !important;
    border-radius: 8px !important;
    background: linear-gradient(
        135deg,
        #6366f1 0%,
        #8b5cf6 100%
    ) !important;
    color: #fff !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    line-height: 1 !important;
}

.sidebar-brand-name {
    font-size: 15px !important;
    font-weight: 600 !important;
    letter-spacing: -0.2px !important;
    line-height: 1 !important;
    color: inherit !important;
}

/* =========================================================================
   REMOVE DEFAULT STREAMLIT GAPS
   ========================================================================= */

section[data-testid="stSidebar"]
[data-testid="stVerticalBlock"] {
    gap: 0 !important;
}

section[data-testid="stSidebar"]
[data-testid="stVerticalBlock"] > div {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
}

/* =========================================================================
   NEW CHAT
   ========================================================================= */

.new-chat {
    width: 100% !important;
    margin: 0 0 8px 0 !important;
    padding: 0 !important;
    text-align: left;
}

.new-chat button {
    width: 100% !important;
    height: 40px !important;
    min-height: 40px !important;
    margin: 0 !important;
    padding: 0 11px !important;
    border-radius: 9px !important;
    border: 1px solid rgba(255, 255, 255, 0.14) !important;
    background: transparent !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    text-align: left !important;
    justify-content: flex-start !important;
    align-items: center !important;
    transition: background 0.15s ease, border-color 0.15s ease !important;
}

.new-chat button:hover {
    background: rgba(255, 255, 255, 0.07) !important;
    border-color: rgba(255, 255, 255, 0.22) !important;
}

.new-chat button > div {
    width: 100% !important;
    display: flex !important;
    justify-content: flex-start !important;
    align-items: center !important;
    text-align: left !important;
}

.new-chat button p {
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    text-align: left !important;
}

/* =========================================================================
   SECTION TITLE
   ========================================================================= */

.sidebar-section-title {
    padding: 14px 8px 7px 8px !important;
    margin-bottom: 20px;
    font-size: 14px;
    font-weight: 700;
    font-style: italic;
    color: #8e8e8e;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    text-align: left !important;
}

/* =========================================================================
   CHAT LIST
   ========================================================================= */

.chat-list {
    width: 100%;
    margin: 0 !important;
    padding: 0 !important;
}

/* =========================================================================
   THREAD WRAPPER
   ========================================================================= */

.thread-normal,
.thread-active {
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1 !important;
    text-align: left !important;
}

/* =========================================================================
   STREAMLIT BUTTON CONTAINER
   ========================================================================= */

section[data-testid="stSidebar"] .stButton {
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    text-align: left !important;
}

section[data-testid="stSidebar"] .stButton > div {
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    text-align: left !important;
}

/* =========================================================================
   THREAD BUTTON
   ========================================================================= */

.thread-normal button,
.thread-active button {
    width: 100% !important;
    min-height: 36px !important;
    height: 36px !important;
    margin: 0 !important;
    border-radius: 8px !important;
    border: none !important;
    box-shadow: none !important;
    font-size: 13px !important;
    font-weight: 400 !important;
    text-align: left !important;
    justify-content: flex-start !important;
    align-items: center !important;
    display: flex !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    line-height: 24px !important;
    transition: background 0.12s ease !important;
}

/* =========================================================================
   THREAD INNER CONTENT
   ========================================================================= */

.thread-normal button > div,
.thread-active button > div {
    width: 100% !important;
    display: flex !important;
    justify-content: flex-start !important;
    align-items: start !important;
    margin: 0 !important;
    padding: 0 !important;
    text-align: left !important;
}

/* =========================================================================
   THREAD TEXT
   ========================================================================= */

.thread-normal button p,
.thread-active button p {
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    text-align: left !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

/* =========================================================================
   NORMAL THREAD
   ========================================================================= */

.thread-normal button {
    background: transparent !important;
    color: inherit !important;
}

/* =========================================================================
   NORMAL THREAD HOVER
   ========================================================================= */

.thread-normal button:hover {
    background: rgba(255, 255, 255, 0.07) !important;
}

/* =========================================================================
   ACTIVE THREAD
   ========================================================================= */

.thread-active button {
    background: rgba(255, 255, 255, 0.11) !important;
    color: inherit !important;
    font-weight: 500 !important;
}

/* =========================================================================
   ACTIVE THREAD HOVER
   ========================================================================= */

.thread-active button:hover {
    background: rgba(255, 255, 255, 0.15) !important;
}

/* =========================================================================
   EMPTY CONVERSATIONS
   ========================================================================= */

.empty-conversations {
    padding: 8px 8px;
    color: #777;
    font-size: 12px;
    line-height: 1.5;
    text-align: left;
}

/* =========================================================================
   CLEAR CHAT
   ========================================================================= */

.clear-chat {
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
}

.clear-chat button {
    width: 100% !important;
    min-height: 36px !important;
    height: 36px !important;
    margin: 0 !important;
    padding: 5px 10px !important;
    border: none !important;
    background: transparent !important;
    border-radius: 8px !important;
    text-align: left !important;
    justify-content: flex-start !important;
    font-size: 13px !important;
    box-shadow: none !important;
}

.clear-chat button:hover {
    background: rgba(255, 255, 255, 0.07) !important;
}

.clear-chat button > div {
    width: 100% !important;
    justify-content: flex-start !important;
    text-align: left !important;
}

.clear-chat button p {
    width: 100% !important;
    margin: 0 !important;
    text-align: left !important;
}

/* =========================================================================
   DOCUMENT
   ========================================================================= */

.document-card {
    margin: 2px 5px;
    padding: 9px 10px;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.08);
    font-size: 12px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* =========================================================================
   SYSTEM STATUS
   ========================================================================= */

.system-status {
    padding: 6px 8px;
    font-size: 12px;
    color: #888;
    text-align: left;
}

/* =========================================================================
   SIDEBAR FOOTER
   ========================================================================= */

.sidebar-footer {
    padding: 12px 8px 5px 8px;
    margin-top: 10px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    color: #777;
    font-size: 11px;
    line-height: 1.5;
    text-align: left;
}

/* =========================================================================
   DIVIDERS
   ========================================================================= */

section[data-testid="stSidebar"] hr {
    margin: 9px 0 !important;
    border-color: rgba(255, 255, 255, 0.08) !important;
}

/* =========================================================================
   REMOVE FOCUS
   ========================================================================= */

section[data-testid="stSidebar"] button:focus {
    box-shadow: none !important;
}

/* =========================================================================
   MAIN HEADER
   ========================================================================= */

.askx-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 8px;
    margin-bottom: 6px;
}

/* =========================================================================
   ASKX ICON
   ========================================================================= */

.askx-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    width: 42px;
    height: 42px;
    border-radius: 11px;
    background: linear-gradient(
        135deg,
        #6366f1 0%,
        #8b5cf6 100%
    );
    color: #fff;
    font-size: 20px;
    font-weight: 700;
    line-height: 1;
}

/* =========================================================================
   ASKX TITLE
   ========================================================================= */

.askx-title {
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: -0.8px;
    line-height: 1.1;
}

/* =========================================================================
   MAIN SUBTITLE
   ========================================================================= */

.main-subtitle {
    color: #888;
    font-size: 14px;
    margin-bottom: 1rem;
    margin-left: 0;
}

/* =========================================================================
   CHAT
   ========================================================================= */

[data-testid="stChatMessage"] {
    border-radius: 12px;
}

/* =========================================================================
   CHAT INPUT
   ========================================================================= */

[data-testid="stChatInput"] {
    border-radius: 14px;
}

/* =========================================================================
   MOBILE
   ========================================================================= */

@media (max-width: 768px) {
    section[data-testid="stSidebar"] {
        width: 280px !important;
        min-width: 280px !important;
        max-width: 280px !important;
    }
}

</style>
"""


def setup_page():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="AskX",
        page_icon="✨",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(CSS_STYLES, unsafe_allow_html=True)
