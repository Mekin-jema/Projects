# Production LLM and RAG API

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![FastAPI: 0.110+](https://img.shields.io/badge/FastAPI-0.110%2B-green.svg)](https://fastapi.tiangolo.com/)

Amin AI is a LangChain and LangGraph chatbot with a FastAPI backend and Streamlit interface. It supports tool calling, PDF question answering, persistent conversation threads, response caching, security filtering, and request metrics.

## Features

- Stateful LangGraph conversations with SQLite checkpoints
- PDF ingestion and retrieval using FAISS
- Web search, calculator, stock price, and weather tools
- Prompt-injection detection and input sanitization
- PII masking for inputs and generated responses
- Harmful-output filtering
- In-memory response caching with TTL
- Structured logging, request timing, and metrics
- Primary-model and fallback-model handling

## Requirements

- Python 3.12 or later
- An OpenRouter API key
- Optional Tavily and OpenWeather API keys for their tools

## Setup

Install dependencies with `uv`:

```bash
uv sync
```

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your-openrouter-key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
PRIMARY_MODEL=openai/gpt-4o-mini
FALLBACK_MODEL=openai/gpt-4o-mini
TAVILY_API_KEY=your-tavily-key
OPENWEATHER_API_KEY=your-openweather-key
```

## Run The Applications

Start the FastAPI backend:

```bash
uv run uvicorn main:app --reload
```

The API provides:

- `POST /chat` for secured chat requests
- `POST /chat/stream` for SSE streaming responses from the agent
- `GET /health` for service health
- `GET /metrics` for request metrics
- `GET /cache/stats` for cache statistics

Start the Streamlit interface:

```bash
uv run streamlit run app/ui/streamlit_app.py
```

The UI uses the same security, caching, monitoring, fallback, and thread-aware workflow as the API. PDFs uploaded through the UI are stored in `data/uploads/` and indexed in `data/faiss_db/`.

## Project Structure

```text
amin_ai/
├── app/
│   ├── main.py              # FastAPI application
│   ├── agent.py             # API wrapper for the unified workflow
│   ├── config.py            # Settings, LLM, and embedding configuration
│   ├── security.py          # Input and output security pipeline
│   ├── cache.py             # TTL response cache
│   ├── monitoring.py        # Logging, metrics, and request timing
│   ├── models.py            # API request and response models
│   ├── core/tools.py        # Agent tools
│   ├── rag/                 # PDF ingestion and retrieval
│   ├── workflow/            # AgentState and unified LangGraph
│   └── ui/streamlit_app.py  # Streamlit interface
├── data/                    # Runtime uploads, FAISS index, and checkpoints
├── docs/                    # Detailed structure and migration notes
├── tests/                   # Automated tests
├── main.py                  # Root FastAPI entrypoint
└── pyproject.toml           # Project metadata and dependencies
```

## Development

Run the tests with:

```bash
uv run pytest -q
```

The shared workflow state is defined in `app/workflow/state.py` as `AgentState`. The graph in `app/workflow/graph.py` combines primary processing, tool execution, fallback handling, error responses, and SQLite checkpointing.

See `docs/QUICK_START.md`, `docs/STRUCTURE.md`, and `docs/MIGRATION.md` for additional project notes.


