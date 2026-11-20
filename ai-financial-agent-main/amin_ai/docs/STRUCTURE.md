# Amin AI - Agentic Chatbot with RAG

A sophisticated AI chatbot powered by LangChain and LangGraph with Retrieval-Augmented Generation (RAG) capabilities.

## Project Structure

```
amin_ai/
├── app/                          # Main application code
│   ├── __init__.py
│   ├── config.py                 # Settings, LLM, and embeddings configuration
│   │
│   ├── core/                     # Core functionality
│   │   ├── __init__.py
│   │   └── tools.py              # Tool definitions (search, calculator, weather, stocks, RAG)
│   │
│   ├── rag/                      # Retrieval-Augmented Generation
│   │   ├── __init__.py
│   │   ├── document_loader.py    # PDF ingestion and indexing
│   │   └── retriever.py          # Vector store retrieval
│   │
│   ├── workflow/                 # LangGraph workflow
│   │   ├── __init__.py
│   │   ├── state.py              # AgentState and data types
│   │   └── graph.py              # Agent graph and nodes
│   │
│   └── ui/                       # User interfaces
│       ├── __init__.py
│       └── app.py                # Streamlit application
│
├── data/                         # Data storage (git-ignored)
│   ├── uploads/                  # User-uploaded PDFs
│   ├── faiss_db/                 # FAISS vector store
│   └── README.md
│
├── main.py                       # Entry point
├── pyproject.toml                # Project configuration
├── README.md                     # This file
└── LICENSE
```

## Features

- **🤖 Agentic AI**: Multi-turn conversations with tool use
- **📄 RAG (RAG)**: Upload and query PDF documents
- **🌐 Web Search**: Real-time web search using Tavily
- **🧮 Calculator**: Complex mathematical expressions
- **📈 Stock Prices**: Real-time stock market data
- **🌤️ Weather**: Current weather information by location
- **💾 Persistent Memory**: SQLite-based conversation checkpoints
- **🎨 Streamlit UI**: User-friendly web interface

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd amin_ai
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

Required API Keys:
- `OPENROUTER_API_KEY` - For LLM and embeddings
- `OPENROUTER_BASE_URL` - OpenRouter API base URL
- `TAVILY_API_KEY` - For web search
- `OPENWEATHER_API_KEY` - For weather information

## Usage

### Run the Streamlit UI

```bash
uv run streamlit run app/ui/streamlit_app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

### Use as a Python Module

```python
from src.workflow import chatbot
from langchain_core.messages import HumanMessage

# Invoke the chatbot
response = chatbot.invoke(
    {"messages": [HumanMessage(content="What's the weather in London?")]},
    config={"configurable": {"thread_id": "user-123"}}
)

print(response["messages"][-1].content)
```

## Module Overview

### `app/config.py`
Centralized configuration for LLM and embeddings. Initializes:
- OpenRouter ChatOpenAI (gpt-4.1-mini)
- OpenAI embeddings (text-embedding-3-small)

### `app/core/tools.py`
Tool definitions available to the agent:
- `rag_tool`: Query uploaded PDFs
- `search_tool`: Web search
- `calculator`: Math calculations
- `get_stock_price`: Stock market data
- `get_current_weather`: Weather information

### `app/rag/`
Handles document indexing and retrieval:
- `ingest_rag_document()`: Load and index PDFs
- `get_retriever()`: Retrieve relevant document chunks

### `app/workflow/`
LangGraph workflow orchestration:
- `AgentState`: Shared message, error, retry, and model state definition
- `chat_node`: LLM reasoning node
- `build_graph()`: Construct the agent graph

### `app/ui/app.py`
Streamlit interface for:
- PDF upload and indexing
- Chat with the agent
- Thread management
- Conversation history

## Development

### Project Dependencies
- `langchain` - LLM framework
- `langgraph` - Workflow orchestration
- `streamlit` - Web UI
- `faiss-cpu` - Vector store
- `python-dotenv` - Environment variables

### Adding New Tools

1. Create a tool function in `app/core/tools.py`:
```python
@tool
def my_tool(query: str) -> str:
    """Tool description."""
    # Implementation
    return result
```

2. Add it to the `tools` list at the bottom of the file.

3. Update the system message in `app/workflow/graph.py` with usage instructions.

## License

See LICENSE file for details.

## Support

For issues or questions, please open an issue in the repository.
