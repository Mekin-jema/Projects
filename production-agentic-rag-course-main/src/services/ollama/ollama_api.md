If you mean the **Ollama HTTP API endpoints**, the main ones are exposed by Ollama at:

```text
http://localhost:11434
```

### Main Ollama endpoints

| Endpoint        | Method | Use case                        |
| --------------- | ------ | ------------------------------- |
| `/api/generate` | POST   | Generate text from a prompt     |
| `/api/chat`     | POST   | Chat/conversation with messages |
| `/api/embed`    | POST   | Generate embeddings             |
| `/api/tags`     | GET    | List installed models           |
| `/api/show`     | POST   | Get model information           |
| `/api/pull`     | POST   | Download a model                |
| `/api/push`     | POST   | Upload a model                  |
| `/api/create`   | POST   | Create a custom model           |
| `/api/delete`   | DELETE | Delete a model                  |
| `/api/copy`     | POST   | Copy a model                    |
| `/api/ps`       | GET    | Show currently loaded models    |
| `/api/version`  | GET    | Get Ollama version              |

### 1. `/api/generate`

This is the one you're currently using.

```python
requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "llama3.2:1b",
        "prompt": "What is RAG?",
        "stream": False
    }
)
```

Use it for **single-prompt generation**.

---

### 2. `/api/chat`

For conversations:

```python
requests.post(
    "http://localhost:11434/api/chat",
    json={
        "model": "llama3.2:1b",
        "messages": [
            {
                "role": "user",
                "content": "What is RAG?"
            }
        ],
        "stream": False
    }
)
```

Use this when you have:

```text
system → user → assistant → user → assistant
```

---

### 3. `/api/embed`

Very important for your **RAG project**.

```python
response = requests.post(
    "http://localhost:11434/api/embed",
    json={
        "model": "nomic-embed-text",
        "input": "What is hybrid search?"
    }
)

print(response.json())
```

This produces vectors:

```text
Text
 ↓
Embedding model
 ↓
[0.021, -0.183, 0.442, ...]
 ↓
OpenSearch
```

You can then use those vectors for semantic search.

---

### 4. `/api/tags`

See your installed models:

```bash
curl http://localhost:11434/api/tags
```

Python:

```python
response = requests.get(
    "http://localhost:11434/api/tags"
)

print(response.json())
```

---

### 5. `/api/show`

Get information about a model:

```bash
curl http://localhost:11434/api/show \
  -d '{"model":"llama3.2:1b"}'
```

Useful for checking model details, parameters, template, etc.

---

### 6. `/api/ps`

See models currently loaded in memory:

```bash
curl http://localhost:11434/api/ps
```

Useful when you're running multiple models and want to see what's currently active.

---

### 7. `/api/pull`

Download a model:

```bash
curl http://localhost:11434/api/pull \
  -d '{"model":"llama3.2:1b"}'
```

Equivalent to:

```bash
ollama pull llama3.2:1b
```

---

### 8. `/api/delete`

Delete a model:

```bash
curl -X DELETE http://localhost:11434/api/delete \
  -d '{"model":"llama3.2:1b"}'
```

Equivalent to:

```bash
ollama rm llama3.2:1b
```

---

### For your Agentic RAG project

The endpoints I'd focus on are:

```text
/api/chat
     ↓
Conversation

/api/generate
     ↓
Generation / routing / classification

/api/embed
     ↓
Embeddings
     ↓
OpenSearch
     ↓
RAG
```

So your architecture could be:

```text
                 Ollama
                   │
        ┌──────────┼──────────┐
        ↓          ↓          ↓
    /api/chat  /api/generate /api/embed
        │          │          │
        ↓          ↓          ↓
      Chat       Agent       RAG
                  Router    Embeddings
                              │
                              ↓
                          OpenSearch
```

**One distinction that's important:** `/api/generate` and `/api/chat` are for **LLM generation**, while `/api/embed` is for **embedding/vector generation**. They serve different parts of a RAG system.
