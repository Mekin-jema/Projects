# System Execution & Architecture Guide

This document details the end-to-end execution flow of the **arXiv Paper Curator** Production Agentic RAG system. It covers both the **Batch Data Ingestion Pipeline** (orchestrated with Apache Airflow) and the **Real-Time Agentic RAG Serving Engine** (orchestrated with FastAPI, LangGraph, Ollama, and OpenSearch).

---

## 1. High-Level Macro System Architecture

The project operates across two interconnected execution tracks:
1. **Scheduled Batch Ingestion Track (Airflow)**: Automatically triggers daily, queries arXiv, parses academic research PDFs using Docling, stores metadata & full text in PostgreSQL, computes overlapping text chunks, generates dense vector representations with Jina AI, and populates the OpenSearch hybrid index.
2. **Interactive Agentic Query Track (FastAPI + LangGraph)**: Receives questions via Gradio UI, Telegram bot, or REST API, routes queries through a multi-node LangGraph StateGraph (domain guardrail validation, tool-based hybrid retrieval, LLM-based document grading, self-correcting query rewrites, and cited answer synthesis), and records full traces with Langfuse.

```mermaid
flowchart TB
    classDef client fill:#1e1b4b,stroke:#6366f1,stroke-width:2px,color:#e0e7ff;
    classDef api fill:#0f172a,stroke:#38bdf8,stroke-width:2px,color:#f0f9ff;
    classDef agent fill:#3b0764,stroke:#c084fc,stroke-width:2px,color:#faf5ff;
    classDef airflow fill:#14532d,stroke:#22c55e,stroke-width:2px,color:#f0fdf4;
    classDef storage fill:#1c1917,stroke:#f59e0b,stroke-width:2px,color:#fef3c7;
    classDef ai fill:#451a03,stroke:#fb923c,stroke-width:2px,color:#fff7ed;
    classDef obs fill:#4c0519,stroke:#fb7185,stroke-width:2px,color:#fff1f2;

    subgraph Clients ["1. Client Interfaces"]
        UI["Gradio Web App<br/>(Port 7861)"]:::client
        TG["Telegram Bot Service<br/>(python-telegram-bot)"]:::client
        REST["REST API Clients<br/>(OpenAPI /docs)"]:::client
    end

    subgraph Gateway ["2. FastAPI Gateway (Port 8000)"]
        API["FastAPI Lifespan Router"]:::api
        ASK["/api/v1/ask<br/>(Standard RAG)"]:::api
        STREAM["/api/v1/stream<br/>(Streaming SSE)"]:::api
        AGENT_EP["/api/v1/ask-agentic<br/>(LangGraph Agentic)"]:::api
        CACHE["Exact Match Cache<br/>(Redis 6379)"]:::storage
    end

    subgraph AgenticEngine ["3. LangGraph Agentic Pipeline"]
        STATE_GRAPH["StateGraph Orchestrator"]:::agent
        GR["Guardrail Validation<br/>(Domain Filter)"]:::agent
        RET["Retrieve Node<br/>(Attempts <= 3)"]:::agent
        TOOL["ToolNode<br/>(retrieve_papers)"]:::agent
        GRADE["Grade Documents<br/>(Relevance Assessment)"]:::agent
        REWRITE["Rewrite Query<br/>(Query Reformulation)"]:::agent
        GEN["Generate Answer<br/>(Citation Synthesis)"]:::agent
    end

    subgraph BatchPipeline ["4. Scheduled Batch Pipeline (Airflow:8080)"]
        DAG["arxiv_paper_ingestion DAG<br/>(Mon-Fri 06:00 UTC)"]:::airflow
        T_SETUP["setup_environment"]:::airflow
        T_FETCH["fetch_daily_papers<br/>(Docling PDF Parser)"]:::airflow
        T_INDEX["index_papers_hybrid<br/>(Chunker + Jina Embeddings)"]:::airflow
        T_REP["generate_daily_report"]:::airflow
        T_CLEAN["cleanup_temp_files"]:::airflow
    end

    subgraph CoreServices ["5. Storage, AI Models & Observability"]
        PG[("PostgreSQL DB<br/>(papers table / Port 5432)")]:::storage
        OS[("OpenSearch Cluster<br/>(arxiv_chunks_hybrid / Port 9200)")]:::storage
        OLLAMA["Ollama LLM<br/>(llama3.2:1b / Port 11434)"]:::ai
        JINA["Jina AI Embeddings<br/>(1024-dim dense vectors)"]:::ai
        LF["Langfuse Monitoring<br/>(Spans, Traces, Latency / Port 3001)"]:::obs
    end

    %% Client -> Gateway
    UI & TG & REST --> API
    API --> ASK & STREAM & AGENT_EP
    ASK <--> CACHE
    AGENT_EP --> STATE_GRAPH

    %% LangGraph Internal Workflow
    STATE_GRAPH --> GR
    GR -->|Pass| RET
    RET --> TOOL
    TOOL --> GRADE
    GRADE -->|Relevant| GEN
    GRADE -->|Irrelevant & attempts < 3| REWRITE
    REWRITE --> RET

    %% Tool & Model interactions
    TOOL <-->|Embed Query| JINA
    TOOL <-->|KNN + BM25 Hybrid Search| OS
    GR & GRADE & REWRITE & GEN <--> OLLAMA
    STATE_GRAPH -.-> LF

    %% Batch Ingestion Flow
    DAG --> T_SETUP --> T_FETCH --> T_INDEX --> T_REP --> T_CLEAN
    T_FETCH -->|Raw text & sections| PG
    T_INDEX -->|Query unprocessed papers| PG
    T_INDEX <-->|Batch Embeddings| JINA
    T_INDEX -->|Bulk Index Chunks| OS
```

---

## 2. Airflow Data Ingestion Pipeline

The batch pipeline is declared in [airflow/dags/arxiv_paper_ingestion.py](file:///c:/Users/Mekin.Jemal/OneDrive%20-%20Safaricom%20Ethiopia/Desktop/Projects/LLM/production-agentic-rag-course-main/airflow/dags/arxiv_paper_ingestion.py) and executes on a defined schedule (`0 6 * * 1-5` UTC):

```mermaid
flowchart TD
    classDef task fill:#0f172a,stroke:#3b82f6,stroke-width:2px,color:#f8fafc;
    classDef step fill:#1e293b,stroke:#10b981,stroke-width:1.5px,color:#ecfdf5;
    classDef action fill:#701a75,stroke:#f472b6,stroke-width:1.5px,color:#fdf2f8;

    CRON((Schedule Trigger<br/>Cron: 0 6 * * 1-5)):::task

    subgraph S1 ["1. Setup Environment"]
        T1["setup_environment (setup.py)"]:::task
        T1_A["Verify PostgreSQL & OpenSearch connectivity"]:::step
        T1_B["Initialize 'arxiv_chunks_hybrid' index if missing"]:::action
        T1 --> T1_A --> T1_B
    end

    subgraph S2 ["2. Fetch & Parse Papers"]
        T2["fetch_daily_papers (fetching.py)"]:::task
        T2_A["Calculate target date (execution_date - 1 day)"]:::step
        T2_B["Query arXiv API for cs.AI and cs.LG categories"]:::step
        T2_C["Download PDF and parse via Docling (Extract Markdown, Sections, References)"]:::action
        T2_D["Persist metadata & full text in PostgreSQL 'papers' table"]:::step
        T2_E["Push 'fetch_results' (stored paper count) to XCom"]:::action
        T2 --> T2_A --> T2_B --> T2_C --> T2_D --> T2_E
    end

    subgraph S3 ["3. Hybrid Indexing"]
        T3["index_papers_hybrid (indexing.py)"]:::task
        T3_A["XCom pull 'fetch_results' and load newly stored papers from PostgreSQL"]:::step
        T3_B["TextChunker.chunk_paper() (600-word sliding window, 100-word overlap)"]:::action
        T3_C["JinaEmbeddingsClient batches chunks to generate 1024-dim dense vectors"]:::step
        T3_D["Bulk index chunks into OpenSearch (BM25 keyword text + KNN vector)"]:::action
        T3_E["Push 'hybrid_index_stats' to XCom"]:::action
        T3 --> T3_A --> T3_B --> T3_C --> T3_D --> T3_E
    end

    subgraph S4 ["4. Reporting & Cleanup"]
        T4["generate_daily_report (reporting.py)"]:::task
        T4_A["Aggregate XCom fetch & indexing metrics and log summary"]:::step
        T5["cleanup_temp_files (BashOperator)"]:::task
        T5_A["find /tmp -name '*.pdf' -mtime +30 -delete"]:::action
        T4 --> T4_A
        T5 --> T5_A
    end

    END_DAG((Pipeline Execution Finished)):::task

    CRON --> S1 --> S2 --> S3 --> S4 --> END_DAG
```

---

## 3. LangGraph Agentic RAG Decision Cycle

Configured in [src/services/agents/agentic_rag.py](file:///c:/Users/Mekin.Jemal/OneDrive%20-%20Safaricom%20Ethiopia/Desktop/Projects/LLM/production-agentic-rag-course-main/src/services/agents/agentic_rag.py), this cyclic graph adaptively validates, retrieves, grades, rewrites, and answers:

```mermaid
flowchart TD
    classDef startNode fill:#0284c7,stroke:#38bdf8,stroke-width:2px,color:#ffffff;
    classDef decision fill:#6d28d9,stroke:#c084fc,stroke-width:2px,color:#ffffff;
    classDef process fill:#1e293b,stroke:#94a3b8,stroke-width:1.5px,color:#f8fafc;
    classDef tool fill:#047857,stroke:#34d399,stroke-width:2px,color:#ffffff;
    classDef rejection fill:#be123c,stroke:#fb7185,stroke-width:2px,color:#ffffff;
    classDef doneNode fill:#059669,stroke:#10b981,stroke-width:2px,color:#ffffff;

    START(["__start__ (User Question)"]):::startNode

    GUARDRAIL["guardrail<br/>(ainvoke_guardrail_step)<br/>LLM checks query relevance to CS/AI/ML"]:::process
    DEC_GUARD{"Guardrail Score >= 0.7?"}:::decision
    OUT_OF_SCOPE["out_of_scope<br/>(ainvoke_out_of_scope_step)<br/>Return domain boundary disclaimer"]:::rejection

    RETRIEVE["retrieve<br/>(ainvoke_retrieve_step)<br/>Manage retrieval attempts counter"]:::process
    DEC_ATTEMPTS{"attempts >= max_attempts?<br/>(default: 3)"}:::decision
    FALLBACK["Fallback: Max retrieval attempts exceeded"]:::rejection

    TOOL["tool_retrieve<br/>(ToolNode: retrieve_papers)"]:::tool
    OS_CALL[("OpenSearch Hybrid Retrieval<br/>BM25 keyword + Jina KNN vector")]:::tool

    GRADE["grade_documents<br/>(ainvoke_grade_documents_step)<br/>Structured LLM binary relevance check"]:::process
    DEC_GRADE{"binary_score == 'yes'?"}:::decision

    REWRITE["rewrite_query<br/>(ainvoke_rewrite_query_step)<br/>LLM reformulates technical query"]:::process

    GENERATE["generate_answer<br/>(ainvoke_generate_answer_step)<br/>Ollama synthesizes answer with paper citations"]:::doneNode
    END_NODE(["__end__ (Return AgenticAskResponse)"]):::startNode

    %% Graph Routing
    START --> GUARDRAIL --> DEC_GUARD
    DEC_GUARD -->|No: Score < 0.7| OUT_OF_SCOPE --> END_NODE
    DEC_GUARD -->|Yes: Score >= 0.7| RETRIEVE

    RETRIEVE --> DEC_ATTEMPTS
    DEC_ATTEMPTS -->|Yes| FALLBACK --> END_NODE
    DEC_ATTEMPTS -->|No| TOOL

    TOOL <--> OS_CALL
    TOOL --> GRADE --> DEC_GRADE

    DEC_GRADE -->|No: Irrelevant chunks| REWRITE
    REWRITE -->|Loop back with improved query| RETRIEVE

    DEC_GRADE -->|Yes: Chunks are relevant| GENERATE --> END_NODE
```

---

## 4. End-to-End Query-to-Answer Sequence

This sequence diagram illustrates the call path when a user submits a question to `/api/v1/ask-agentic`:

```mermaid
sequenceDiagram
    autonumber
    actor User as User (Gradio / Telegram)
    participant API as FastAPI Gateway (src/main.py)
    participant Agent as LangGraph Engine (agentic_rag.py)
    participant Ollama as Ollama LLM (:11434)
    participant Jina as Jina Embeddings API
    participant OpenSearch as OpenSearch (:9200)
    participant Langfuse as Langfuse Tracer (:3001)

    User->>API: POST /api/v1/ask-agentic {"query": "Explain multi-head attention"}
    activate API
    API->>Langfuse: create_trace("agentic_rag", user_id="api_user")

    %% Guardrail Phase
    API->>Agent: ainvoke(query)
    activate Agent
    Agent->>Langfuse: create_span("guardrail_validation")
    Agent->>Ollama: Check if question is in CS/AI/ML research scope
    Ollama-->>Agent: score: 0.95 (in-scope)
    Agent->>Langfuse: end_span(score=0.95)

    %% Retrieval Phase
    Agent->>Langfuse: create_span("document_retrieval_initiation", attempt=1)
    Agent->>Jina: POST /embeddings (query text)
    Jina-->>Agent: 1024-dim dense vector
    Agent->>OpenSearch: Hybrid query (BM25 matches + KNN vector search)
    OpenSearch-->>Agent: Top-K retrieved chunks with metadata & score
    Agent->>Langfuse: end_span(chunks_returned=K)

    %% Grading Phase
    Agent->>Langfuse: create_span("document_grading")
    Agent->>Ollama: Assess relevance of chunks against query
    Ollama-->>Agent: binary_score: "yes", reasoning: "Documents explain multi-head attention formula..."
    Agent->>Langfuse: end_span(route="generate_answer")

    %% Answer Generation Phase
    Agent->>Langfuse: create_span("answer_generation")
    Agent->>Ollama: Generate synthesis citing retrieved papers
    Ollama-->>Agent: Final formatted answer with arXiv references
    Agent->>Langfuse: end_span(answer_generation_complete)
    
    deactivate Agent

    API-->>User: HTTP 200 AgenticAskResponse (answer, sources, reasoning_steps, trace_id)
    deactivate API

    %% Optional Feedback Loop
    opt User Feedback
        User->>API: POST /api/v1/feedback {"trace_id": "...", "score": 1, "comment": "Accurate"}
        API->>Langfuse: submit_feedback()
    end
```

---

## 5. Docker Compose Microservices Topology

All runtime components run as services within the single `rag-network` bridge defined in [compose.yml](file:///c:/Users/Mekin.Jemal/OneDrive%20-%20Safaricom%20Ethiopia/Desktop/Projects/LLM/production-agentic-rag-course-main/compose.yml):

```mermaid
graph TB
    classDef container fill:#0f172a,stroke:#38bdf8,stroke-width:2px,color:#f8fafc;
    classDef storage fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#ecfdf5;
    classDef ext fill:#451a03,stroke:#fb923c,stroke-width:2px,color:#fff7ed;

    subgraph BridgeNetwork ["Docker Network: rag-network"]
        %% APIs & Orchestration
        API["rag-api<br/>(FastAPI :8000)"]:::container
        AIRFLOW["rag-airflow<br/>(Airflow Web & Scheduler :8080)"]:::container
        
        %% Model Service
        OLLAMA["rag-ollama<br/>(Ollama Local LLM :11434)"]:::container

        %% Storage & Search Engines
        POSTGRES[("rag-postgres<br/>(PostgreSQL :5432)")]:::storage
        REDIS[("rag-redis<br/>(Redis Cache :6379)")]:::storage
        OPENSEARCH[("rag-opensearch<br/>(OpenSearch :9200)")]:::storage
        DASHBOARDS["rag-dashboards<br/>(OpenSearch UI :5601)"]:::container

        %% Langfuse Observability Stack
        LF_WEB["rag-langfuse-web<br/>(Langfuse UI :3001)"]:::container
        LF_WORKER["rag-langfuse-worker<br/>(Worker :3030)"]:::container
        CLICKHOUSE[("rag-clickhouse<br/>(ClickHouse :8123/:9000)")]:::storage
        LF_PG[("rag-langfuse-postgres<br/>(PostgreSQL :5433)")]:::storage
        LF_REDIS[("rag-langfuse-redis<br/>(Redis :6380)")]:::storage
        LF_MINIO[("rag-langfuse-minio<br/>(MinIO S3 :9090/:9091)")]:::storage
    end

    subgraph ExternalWorld ["Host & External Services"]
        BROWSER["Host Browser<br/>(Gradio UI :7861 / Docs :8000)"]:::ext
        TG_NET["Telegram Cloud API"]:::ext
        JINA_API["Jina AI Embeddings Cloud API"]:::ext
        ARXIV_CLOUD["arXiv.org REST API & e-Prints"]:::ext
    end

    %% Network Connections
    BROWSER --> API
    BROWSER --> AIRFLOW
    BROWSER --> DASHBOARDS
    BROWSER --> LF_WEB

    API --> TG_NET
    API --> JINA_API
    AIRFLOW --> ARXIV_CLOUD
    AIRFLOW --> JINA_API

    API --> POSTGRES & REDIS & OPENSEARCH & OLLAMA & LF_WEB
    AIRFLOW --> POSTGRES & OPENSEARCH & OLLAMA & REDIS
    DASHBOARDS --> OPENSEARCH

    %% Langfuse Internal Connections
    LF_WEB --> LF_PG & LF_REDIS & CLICKHOUSE & LF_MINIO
    LF_WORKER --> LF_PG & LF_REDIS & CLICKHOUSE & LF_MINIO
```

---

## 6. Execution Components & File Directory Mapping

| Layer / Subsystem | Primary Implementation Files | Key Responsibilities |
| :--- | :--- | :--- |
| **API Entrypoint** | [src/main.py](file:///c:/Users/Mekin.Jemal/OneDrive%20-%20Safaricom%20Ethiopia/Desktop/Projects/LLM/production-agentic-rag-course-main/src/main.py) | Application lifespan, service registry injection, router binding |
| **Agentic StateGraph** | [src/services/agents/agentic_rag.py](file:///c:/Users/Mekin.Jemal/OneDrive%20-%20Safaricom%20Ethiopia/Desktop/Projects/LLM/production-agentic-rag-course-main/src/services/agents/agentic_rag.py) | Compiles LangGraph workflow with typed `Context` and `AgentState` |
| **Agent Node Handlers** | [src/services/agents/nodes/](file:///c:/Users/Mekin.Jemal/OneDrive%20-%20Safaricom%20Ethiopia/Desktop/Projects/LLM/production-agentic-rag-course-main/src/services/agents/nodes) | Individual execution steps: Guardrail, Retrieve, Grade, Rewrite, Generate |
| **Scheduled Batch DAG** | [airflow/dags/arxiv_paper_ingestion.py](file:///c:/Users/Mekin.Jemal/OneDrive%20-%20Safaricom%20Ethiopia/Desktop/Projects/LLM/production-agentic-rag-course-main/airflow/dags/arxiv_paper_ingestion.py) | Orchestrates setup, fetching, hybrid indexing, report, and cleanup |
| **PDF Extraction** | [src/services/pdf_parser/docling.py](file:///c:/Users/Mekin.Jemal/OneDrive%20-%20Safaricom%20Ethiopia/Desktop/Projects/LLM/production-agentic-rag-course-main/src/services/pdf_parser/docling.py) | Layout-aware document parser extracting sections, references, & markdown |
| **Text Chunking** | [src/services/indexing/text_chunker.py](file:///c:/Users/Mekin.Jemal/OneDrive%20-%20Safaricom%20Ethiopia/Desktop/Projects/LLM/production-agentic-rag-course-main/src/services/indexing/text_chunker.py) | Sliding window chunking (600 words, 100 word overlap) preserving metadata |
| **Hybrid Search** | [src/services/opensearch/client.py](file:///c:/Users/Mekin.Jemal/OneDrive%20-%20Safaricom%20Ethiopia/Desktop/Projects/LLM/production-agentic-rag-course-main/src/services/opensearch/client.py) | Unifies OpenSearch BM25 keyword queries with KNN dense vector queries |
| **Dense Embeddings** | [src/services/embeddings/jina_client.py](file:///c:/Users/Mekin.Jemal/OneDrive%20-%20Safaricom%20Ethiopia/Desktop/Projects/LLM/production-agentic-rag-course-main/src/services/embeddings/jina_client.py) | Jina AI Embeddings v3 client generating 1024-dim dense vectors |
| **Local LLM Engine** | [src/services/ollama/client.py](file:///c:/Users/Mekin.Jemal/OneDrive%20-%20Safaricom%20Ethiopia/Desktop/Projects/LLM/production-agentic-rag-course-main/src/services/ollama/client.py) | Local inference for grading, rewriting, synthesis, and streaming |
| **Observability** | [src/services/langfuse/tracer.py](file:///c:/Users/Mekin.Jemal/OneDrive%20-%20Safaricom%20Ethiopia/Desktop/Projects/LLM/production-agentic-rag-course-main/src/services/langfuse/tracer.py) | Wraps requests with Langfuse traces, node spans, token counts, and feedback |
