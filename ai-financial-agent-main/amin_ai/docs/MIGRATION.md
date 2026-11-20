# Migration Guide: Code Organization

This document explains the new project structure and how the original files have been reorganized.

## What Changed

The original flat file structure has been reorganized into a clean, modular architecture with clear separation of concerns.

### Original Files → New Location

| Original File | New Location | Purpose |
|---|---|---|
| `agentic_chatbot_rag_tools.py` | Split into multiple files | |
| → LLM & embeddings config | `app/config.py` | Centralized LLM configuration |
| → Tool definitions | `app/core/tools.py` | All available tools |
| → PDF ingestion | `app/rag/document_loader.py` | Document loading & indexing |
| → Retriever logic | `app/rag/retriever.py` | Vector store retrieval |
| `agentic_chatbot_rag.py` | `app/rag/document_loader.py` | PDF loading (merged) |
| `chatbot_workflow.py` | Split into multiple files | |
| → State definition | `app/workflow/state.py` | AgentState TypedDict |
| → Graph & nodes | `app/workflow/graph.py` | LangGraph workflow |
| `app_ui.py` | `app/ui/app.py` | Streamlit application |
| `main.py` | `main.py` (updated) | Entry point |

## Directory Structure

```
app/
├── __init__.py
├── config.py                    # LLM & embeddings singleton
├── core/
│   ├── __init__.py
│   └── tools.py                 # All tool definitions
├── rag/
│   ├── __init__.py
│   ├── document_loader.py       # ingest_rag_document()
│   └── retriever.py             # get_retriever()
├── workflow/
│   ├── __init__.py
│   ├── state.py                 # AgentState definition
│   └── graph.py                 # chat_node(), build_graph(), chatbot
└── ui/
    ├── __init__.py
    └── app.py                   # Streamlit UI
```

## Benefits

1. **Separation of Concerns**: Each module has a clear, single responsibility
2. **Reusability**: Components can be imported and used independently
3. **Maintainability**: Easier to locate and update specific functionality
4. **Scalability**: Simple to add new tools, features, or interfaces
5. **Testing**: Each module can be tested in isolation
6. **Documentation**: Clear module purposes and dependencies

## Data Storage

All data now goes in the `data/` directory:
- `data/uploads/` - User-uploaded PDFs
- `data/faiss_db/` - FAISS vector store index
- `data/chatbot.db` - LangGraph SQLite checkpoints

This directory should be in `.gitignore` to avoid committing large files.

## Importing from the New Structure

### Old Way (Not recommended)
```python
from agentic_chatbot_rag_tools import rag_tool, calculator
from agentic_chatbot_rag import ingest_rag_document
from chatbot_workflow import chatbot
from app_ui import # (couldn't reuse)
```

### New Way
```python
# Import tools
from src.core.tools import rag_tool, calculator, tools

# Import RAG functions
from src.rag import ingest_rag_document, get_retriever

# Import workflow
from app.workflow import chatbot, AgentState, get_all_threads

# Import UI (if needed programmatically)
from app.ui.app import # (reserved for Streamlit)
```

## Running the Application

### Streamlit UI (Recommended)
```bash
streamlit run app/ui/app.py
```

### As Python Script
```bash
python main.py
```

### Python REPL/Jupyter
```python
from src.workflow import chatbot
from langchain_core.messages import HumanMessage

response = chatbot.invoke(
    {"messages": [HumanMessage(content="What is 2+2?")]},
    config={"configurable": {"thread_id": "test"}}
)
```

## Next Steps

1. ✅ Review the new structure
2. ✅ Test the Streamlit UI: `streamlit run app/ui/app.py`
3. ✅ Check that all imports work: `python -c "from src.workflow import chatbot; print('OK')"`
4. Update `.gitignore` to include:
   ```
   data/
   .venv/
   __pycache__/
   *.pyc
   .env
   ```
5. (Optional) Delete old files: `agentic_chatbot_rag_tools.py`, `agentic_chatbot_rag.py`, `chatbot_workflow.py`, `app_ui.py`

## Troubleshooting

### Import Errors
Make sure you're running from the project root directory and have installed the package:
```bash
pip install -e .
```

### FAISS Database Not Found
The first run will need to ingest a PDF through the UI or programmatically:
```python
from src.rag import ingest_rag_document
ingest_rag_document("path/to/document.pdf")
```

### Missing Environment Variables
Create a `.env` file in the project root with required keys:
```
OPENROUTER_API_KEY=your_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
TAVILY_API_KEY=your_key_here
OPENWEATHER_API_KEY=your_key_here
```

## Questions?

Refer to `STRUCTURE.md` for detailed module documentation.
