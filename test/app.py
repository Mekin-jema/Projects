import streamlit as st
from main import ask_agent

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Mekin AI Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 0;
    }

    .subtitle {
        color: #9CA3AF;
        font-size: 17px;
        margin-top: 5px;
    }

    .status-card {
        padding: 15px;
        border-radius: 12px;
        background-color: #161B22;
        border: 1px solid #30363D;
        margin-bottom: 15px;
    }

    .footer {
        text-align: center;
        color: #6B7280;
        font-size: 13px;
        margin-top: 50px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🤖 Mekin AI Agent</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "LangChain + OpenRouter + Streamlit"
    "</div>",
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Configuration")

    st.success("Agent Online")

    st.markdown("---")

    st.subheader("Model")

    st.write("OpenRouter")

    st.write("`openai/gpt-4.1-mini`")

    st.markdown("---")

    st.subheader("Tools")

    st.write("🧮 Calculator")

    st.write("🕐 Time Tool")

    st.write("🔍 Tavily Search")

    st.markdown("---")

    if st.button("Clear Chat", use_container_width=True):

        st.session_state.messages = []

        st.rerun()


# ============================================================
# CHAT HISTORY
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


# ============================================================
# DISPLAY PREVIOUS MESSAGES
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# ============================================================
# USER INPUT
# ============================================================

question = st.chat_input(
    "Ask me anything..."
)


# ============================================================
# PROCESS QUESTION
# ============================================================

if question:

    # Add user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):

        st.markdown(question)

    # Generate response
    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:

                answer = ask_agent(question)

                st.markdown(answer)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

            except Exception as error:

                st.error(
                    f"An error occurred: {error}"
                )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="footer">'
    "Built with LangChain • OpenRouter • Streamlit"
    "</div>",
    unsafe_allow_html=True,
)
