# RAG & LLM Connection Guide

## Error: "list index out of range"

### Root Causes
This error occurs during PDF indexing when:

1. **Empty PDF** - The PDF file has no extractable text
2. **Corrupted PDF** - PyPDFLoader cannot parse the file structure  
3. **Scanned Images Only** - PDF contains images but no OCR (text layer)
4. **Text Extraction Failure** - The PDF's text encoding is incompatible

### Solutions

#### Before Upload
- ✅ Ensure the PDF has a **text layer** (not just scanned images)
- ✅ Try opening the PDF in a text editor or copying text from it
- ✅ Verify the file is not corrupted

#### During Processing
- The improved error messages now tell you exactly what went wrong
- Check logs: `logger.error()` statements in `app/rag/document_loader.py`

#### In Code
```python
# Now handles these cases gracefully:
- No pages extracted → ValueError
- No chunks created → ValueError  
- Embedding failures → ValueError with context
```

---

## How RAG & LLM Work Together

### 1. **Document Indexing Phase** (happens once per PDF)
```
┌─────────────────────┐
│   Your PDF (CVM.pdf)│
└──────────┬──────────┘
           │
           ↓
    ┌──────────────────────┐
    │ PyPDFLoader          │  ← Extracts text from pages
    │ splits into 1000 ch. │  ← Creates overlapping chunks
    └──────────┬───────────┘
               │
               ↓
    ┌──────────────────────┐
    │ OpenAI Embeddings    │  ← Converts text→vectors
    │ (API call)           │  ← 1536-dim vectors
    └──────────┬───────────┘
               │
               ↓
    ┌──────────────────────┐
    │ FAISS Vector DB      │  ← Stores vectors on disk
    │ (data/faiss_db)      │  ← Fast similarity search
    └──────────────────────┘
```

### 2. **Question Answering Phase** (happens per user query)
```
┌──────────────────────────┐
│ User: "What is X?"       │
└────────────┬─────────────┘
             │
             ↓
   ┌─────────────────────────┐
   │ rag_tool(query)         │
   │ 1. Convert Q to vector  │
   │ 2. Search FAISS (k=4)   │
   │ 3. Return top 4 chunks  │
   └────────────┬────────────┘
                │
                ↓
   ┌─────────────────────────────────────┐
   │ Combine: [System Msg + Context]     │
   │         + [4 PDF Chunks]            │
   │         + [Original Question]       │
   └────────────┬────────────────────────┘
                │
                ↓
    ┌──────────────────────────────────────┐
    │ LLM (OpenRouter API)                 │
    │ Reads context + question             │
    │ Generates grounded answer            │
    └──────────────────────────────────────┘
```

### 3. **Tool Routing in LangGraph**
```
User Message
     │
     ↓
LLM: "I need to search the PDF" ──→ Calls rag_tool()
     ├─→ search_tool() - web search
     ├─→ calculator - math
     ├─→ get_stock_price - stocks
     └─→ get_current_weather - weather
     │
     ↓
Tool executes & returns result
     │
     ↓
LLM sees result: "Document 1: Page 5: ..."
     │
     ↓
LLM formulates final answer
```

---

## Key Points

### Does RAG Connect to LLM?
**YES**, through the `rag_tool` in your workflow:
- [app/core/tools.py](../app/core/tools.py#L19) - `rag_tool` function
- [app/workflow/graph.py](../app/workflow/graph.py#L111) - Tool execution node

### When Does LLM Use RAG?
The LLM automatically chooses the right tool based on your **System Message**:
```python
"Use rag_tool for uploaded PDF questions, "
"search_tool for current information, "
"calculator for mathematics..."
```

The LLM decides: "This question is about the PDF → I'll call rag_tool"

### What About Embeddings?
- **Indexing**: Your text → OpenAI embeddings API → 1536-dim vectors
- **Retrieval**: Question → Same embeddings API → Find similar vectors
- **Cost**: Embeddings have per-token cost (see OpenRouter pricing)

---

## Debugging Tips

### Enable Detailed Logging
```python
# In streamlit_app.py, after indexing:
logger.info(f"Document indexed successfully")
```

### Test PDF Locally
```python
from langchain_community.document_loaders import PyPDFLoader
loader = PyPDFLoader("path/to/CVM.pdf")
docs = loader.load()
print(f"Loaded {len(docs)} pages")
for doc in docs:
    print(f"Page {doc.metadata['page']}: {len(doc.page_content)} chars")
```

### Check Vector DB
```python
from app.rag.retriever import get_retriever
retriever = get_retriever()
results = retriever.invoke("test query")
print(f"Found {len(results)} results")
```

---

## Architecture Summary

| Component | Role | File |
|-----------|------|------|
| **PyPDFLoader** | Extract text from PDF | `document_loader.py` |
| **TextSplitter** | Create overlapping chunks | `document_loader.py` |
| **Embeddings** | Convert text→vectors | `config.py` (OpenAI) |
| **FAISS** | Store & search vectors | `document_loader.py` |
| **rag_tool** | Retrieve chunks for LLM | `core/tools.py` |
| **LangGraph** | Route to tools | `workflow/graph.py` |
| **LLM** | Generate answer from context | `workflow/graph.py` |

