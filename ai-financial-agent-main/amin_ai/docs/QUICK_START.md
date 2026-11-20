# Quick Reference - New Project Structure

## 🎯 Quick Start

```bash
# Run the Streamlit UI
uv run streamlit run app/ui/streamlit_app.py

# Or test imports
python -c "from src.workflow import chatbot; print('✓ Setup complete')"
```

## 📁 New Directory Layout

```
amin_ai/
├── app/                          Application source code (organized)
│   ├── config.py                 LLM & embeddings setup
│   ├── core/tools.py             All available tools
│   ├── rag/                      RAG functionality
│   │   ├── document_loader.py   PDF ingestion
│   │   └── retriever.py         Vector store queries
│   ├── workflow/                 LangGraph agent
│   │   ├── state.py             State definition
│   │   └── graph.py             Agent graph
│   └── ui/app.py                Streamlit UI
├── data/                         Data storage (git-ignored)
│   ├── uploads/                 PDFs
│   ├── faiss_db/                Vector store
│   └── chatbot.db               Checkpoints
├── main.py                       Entry point
├── pyproject.toml                Dependencies
├── STRUCTURE.md                  📖 Full documentation
└── MIGRATION.md                  Migration guide
```

## 🔧 How to Use

### As a User (Streamlit)
```bash
uv run streamlit run app/ui/streamlit_app.py
```
- Upload PDFs
- Chat with the agent
- Manage threads

### As a Developer
```python
from src.workflow import chatbot
from src.rag import ingest_rag_document
from src.core.tools import tools

# Your code here
```

### Add to .gitignore
```
data/
__pycache__/
*.pyc
.env
```

## 📚 Key Modules

| Module | Location | Purpose |
|--------|----------|---------|
| Config | `app/config.py` | LLM initialization |
| Tools | `app/core/tools.py` | Search, calculator, weather, stocks, RAG |
| RAG | `app/rag/` | Document indexing & retrieval |
| Workflow | `app/workflow/` | Agent graph definition |
| UI | `app/ui/app.py` | Streamlit interface |

## 🚀 Next Steps

1. **Update .gitignore** to exclude `data/` directory
2. **(Optional) Delete old files** if migration is complete:
   - `agentic_chatbot_rag_tools.py`
   - `agentic_chatbot_rag.py`
   - `chatbot_workflow.py`
   - `app_ui.py`
3. **Test**: `uv run streamlit run app/ui/streamlit_app.py`
4. **Read**: `STRUCTURE.md` for detailed documentation

## ✨ Benefits

- ✅ Clear separation of concerns
- ✅ Reusable components
- ✅ Easier to maintain and extend
- ✅ Simple to add new tools
- ✅ Better for testing
- ✅ Professional structure

## 📖 Full Documentation

See:
- `STRUCTURE.md` - Detailed module documentation
- `MIGRATION.md` - Explanation of changes
