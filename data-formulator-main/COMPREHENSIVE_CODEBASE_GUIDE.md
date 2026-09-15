# 📚 Data Formulator: Comprehensive Codebase Guide

**Complete Backend-to-Frontend Understanding** | Version 0.8.0b1  
*A detailed walkthrough from architecture to implementation*

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Quick Reference](#quick-reference)
3. [Architecture Overview](#architecture-overview)
4. [System Architecture Layers](#system-architecture-layers)
5. [Complete End-to-End Data Flow](#complete-end-to-end-data-flow)
6. [Backend Deep Dive](#backend-deep-dive)
7. [Frontend Deep Dive](#frontend-deep-dive)
8. [Communication Patterns](#communication-patterns)
9. [Development Workflow](#development-workflow)
10. [Debugging & Troubleshooting](#debugging--troubleshooting)

---

## Project Overview

### What is Data Formulator?

**Data Formulator** is an AI-powered data visualization and exploration platform that enables analysts to:
- Connect to 21+ data sources (databases, cloud storage, APIs)
- Ask natural language questions using AI agents
- Explore data through interactive visualizations
- Branch into alternative analyses using "Data Threads"
- Share insights through reports and workspaces

### Core Values

| Value | Implementation |
|-------|-----------------|
| **Accessibility** | Natural language queries + semantic chart recommendations |
| **Flexibility** | Multi-source data connectors + custom agent skills |
| **Collaboration** | Workspace persistence + branching analysis paths |
| **Intelligence** | LLM-powered agents with multi-provider support (OpenAI, Anthropic, Azure, custom) |

### Technology Stack at a Glance

```
┌─────────────────────────────────────────┐
│          Frontend (React/TS)             │
│  - UI: Material-UI v7                   │
│  - State: Redux + redux-persist         │
│  - Charts: Flint semantic language      │
│  - Build: Vite                          │
│  - i18n: English + Chinese              │
└────────────────────┬────────────────────┘
                     │ REST API + SSE
                     │
┌────────────────────▼────────────────────┐
│       Backend (Flask/Python)             │
│  - Framework: Flask + 12 blueprints     │
│  - Agents: Modern analyst + 10 legacy   │
│  - Data: DuckDB + 21 loaders            │
│  - LLM: LiteLLM (multi-provider)        │
│  - Auth: OIDC + GitHub OAuth            │
│  - Storage: Local/Ephemeral/Azure       │
└────────────────────┬────────────────────┘
                     │
         ┌───────────┼───────────┐
         ▼           ▼           ▼
    Databases    Cloud APIs    Local Files
```

---

## Quick Reference

### Environment Setup

**Backend (Python)**
```bash
# Install with uv (recommended)
uv pip install -e .

# Or with pip
pip install -e .

# Run the server (port 5567)
uv run data_formulator
```

**Frontend (TypeScript/React)**
```bash
# Install dependencies
npm install

# Development server (port 5173)
npm run dev

# Production build
npm run build

# Run tests
npm run test
```

### Key Environment Variables

**Backend**
```bash
# LLM Configuration
OPENAI_API_KEY=sk-...                    # OpenAI
ANTHROPIC_API_KEY=sk-ant-...            # Claude
AZURE_OPENAI_KEY=...                    # Azure OpenAI
AZURE_OPENAI_ENDPOINT=...

# Server Configuration
PORT=5567                                 # Flask port
SANDBOX=local                            # Code execution: local|docker
MAX_DISPLAY_ROWS=10000                   # Data display limit
LOG_LEVEL=INFO                           # Logging level

# Storage Backend
WORKSPACE_BACKEND=local                  # local|ephemeral|azure_blob
WORKSPACE_STORAGE_ACCOUNT=...            # For Azure Blob

# Authentication
AUTH_PROVIDER=transparent                # transparent|oidc|github|kusto
OIDC_CLIENT_ID=...                       # For OIDC
OIDC_CLIENT_SECRET=...

# Frontend
VITE_API_BASE_URL=http://localhost:5567  # Backend URL for dev
```

### Port Configuration

| Service | Port | Environment |
|---------|------|-------------|
| **Frontend Dev** | 5173 | Development |
| **Backend API** | 5567 | Development/Production |
| **Production Frontend** | 80/443 | Production (via reverse proxy) |

---

## Architecture Overview

### System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│                  (React/TypeScript + Material-UI)               │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌──────────────┐│
│  │ Data Load │  │ Data View │  │ Analytics │  │ Report/Share ││
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └──────┬───────┘│
└────────┼───────────────┼───────────────┼───────────────┼────────┘
         │               │               │               │
         └───────────────┼───────────────┼───────────────┘
                         │ Redux State Management
                         │ (workspace, threads, charts, auth)
                         │
                    REST API + SSE
                    (HTTP Streaming)
                         │
┌────────────────────────▼──────────────────────────────────────┐
│                      Flask Backend                             │
│  ┌──────────┬──────────┬──────────┬────────────────────────────┤
│  │ Auth API │ Data API │Agent API │ Connector/Workspace API   │
│  └──────────┴──────────┴──────────┴────────────────────────────┘
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              Agent System (Modern Analyst)                │ │
│  │  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐   │ │
│  │  │ LLM Router  │→ │ Tool Calling │→ │ Skill Loader  │   │ │
│  │  └─────────────┘  └──────────────┘  └───────────────┘   │ │
│  │       ↓                 ↓                    ↓            │ │
│  │  (OpenAI)          (inspect, call)    (data load,     │ │
│  │  (Claude)          (action)            report, core)   │ │
│  │  (Azure)                                                 │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │         Data Engine (DuckDB + Loaders)                    │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐   │ │
│  │  │ SQL DBs  │ │ Cloud    │ │ APIs     │ │ Local      │   │ │
│  │  │ (MySQL,  │ │ (S3,     │ │ (Sheets, │ │ Files      │   │ │
│  │  │ Postgres)│ │ BigQuery)│ │ Weather) │ │ (CSV, Json)│   │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────────┘   │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │        Storage & Persistence (Datalake)                   │ │
│  │  Parquet Files + JSON Metadata                            │ │
│  │  (Local, Ephemeral RAM, or Azure Blob)                    │ │
│  └───────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

---

## System Architecture Layers

### Layer 1: Presentation Layer (Frontend)

**Location**: `src/` directory  
**Technology**: React 18 + TypeScript + Material-UI  
**Responsibility**: User interface and client-side state

| Component | Purpose |
|-----------|---------|
| **Views** | Pages (WorkspaceView, ChartView, ReportView) |
| **Components** | Reusable UI elements (buttons, charts, forms) |
| **Data Operations** | Data transformation logic (coercion, inference) |
| **State (Redux)** | Central state: auth, workspace, charts, threads |
| **API Client** | HTTP + SSE communication with backend |
| **i18n** | Multi-language support (English, Chinese) |

**Key State Slices**:
- `auth`: User authentication, permissions
- `workspace`: Loaded tables, metadata, threads
- `agent`: LLM reasoning, streaming messages
- `chart`: Visualization specs, recommendations
- `connectors`: Data source configuration
- `ui`: UI state (modals, panels, selections)

### Layer 2: API & Routing Layer (Backend)

**Location**: `py-src/data_formulator/api/` directory  
**Technology**: Flask blueprints (lazy-loaded)  
**Responsibility**: HTTP endpoints and request routing

| Blueprint | Endpoints | Purpose |
|-----------|-----------|---------|
| **auth** | `/auth/login`, `/auth/callback`, `/auth/logout` | User authentication |
| **workspace** | `/workspaces/*` | Workspace CRUD operations |
| **agents** | `/agents/run`, `/agents/explore` | Agent execution |
| **charts** | `/charts/recommendations` | Chart synthesis |
| **connectors** | `/connectors/*` | Data source configuration |
| **data** | `/data/tables`, `/data/query` | Data operations |

### Layer 3: Agent Intelligence Layer (Backend)

**Location**: `py-src/data_formulator/agents/` and `py-src/data_formulator/analyst/`  
**Technology**: LiteLLM (multi-provider) + Tool calling  
**Responsibility**: AI reasoning and decision-making

| Component | Purpose |
|-----------|---------|
| **Modern Agent (analyst/)** | New unified agent with skills (v0.8.0b1+) |
| **Legacy Agents (agents/)** | Specialized agents for specific tasks |
| **LLM Providers** | OpenAI, Claude, Azure, custom endpoints |
| **Tool System** | Inspect, call, action, get_state |
| **Skills** | Pluggable capabilities (data load, visualize, report) |

### Layer 4: Data Engine Layer (Backend)

**Location**: `py-src/data_formulator/data_loader/` and `py-src/data_formulator/datalake/`  
**Technology**: DuckDB + 21 data loaders  
**Responsibility**: Data ingestion, querying, persistence

| Component | Supports |
|-----------|----------|
| **SQL Loaders** | MySQL, PostgreSQL, SQL Server, Kusto, Databricks |
| **Cloud Loaders** | S3, Azure Blob, BigQuery, Athena |
| **Document Loaders** | MongoDB, CosmosDB |
| **API Loaders** | Google Sheets, Weather APIs, Stock data |
| **Local Loaders** | Files, sample datasets, Excel |
| **Datalake** | Parquet storage, metadata management |

### Layer 5: Persistence Layer

**Location**: `py-src/data_formulator/datalake/` and file system  
**Technology**: Parquet files + JSON metadata  
**Backends**: Local filesystem, Ephemeral (RAM), Azure Blob  
**Responsibility**: Durable storage and recovery

---

## Complete End-to-End Data Flow

### Scenario 1: User Asks a Question (Data Exploration)

```
Step 1: Frontend - User Input
   ├─ User types: "Show me sales by region"
   ├─ Redux action: postMessage() 
   └─ Dispatch: agent/setMessage()
   
Step 2: Frontend → Backend (HTTP POST with SSE)
   ├─ URL: POST /api/agents/run
   ├─ Payload: { workspaceId, threadId, question, context }
   └─ Headers: { Accept: "text/event-stream" }
   
Step 3: Backend - Agent Initialization
   ├─ Load workspace from storage
   ├─ Initialize modern analyst agent
   ├─ Load workspace metadata (tables, schemas)
   └─ Prepare context for LLM
   
Step 4: Backend - LLM Reasoning Loop (Streaming)
   ├─ Send system + user prompt to LLM
   ├─ Stream back: init, tool_call events
   │  ├─ tool_call(inspect): "Read table schema"
   │  ├─ tool_call(call): "Query top 10 sales records"
   │  └─ chunk: LLM reasoning tokens
   ├─ Execute tools (inspect queries, SQL calls)
   └─ Collect results
   
Step 5: Backend - Skill Invocation
   ├─ Skill system loads: "visualize"
   ├─ Create Vega-Lite spec from query results
   └─ Return Display Instruction (chart spec)
   
Step 6: Frontend - SSE Stream Processing
   ├─ Receive events from stream
   │  ├─ agent/streamInit: Initialize message
   │  ├─ agent/streamMessage: Append reasoning
   │  ├─ agent/streamAction: Mark action completed
   │  └─ agent/streamComplete: Final result
   └─ Redux updates state
   
Step 7: Frontend - Chart Rendering
   ├─ Redux selector: selectDisplayInstruction()
   ├─ Get Vega-Lite spec from state
   ├─ Pass to Flint renderer
   └─ React re-renders <ChartView/>
   
Step 8: User Sees Result
   └─ Interactive chart with insights displayed
```

**Timeline**: 2-15 seconds (depending on query complexity)  
**Key Files**:
- Frontend: `src/views/ChartView.tsx`, `src/app/App.tsx`
- Backend: `py-src/data_formulator/api/agents_bp.py`, `py-src/data_formulator/analyst/agent.py`

---

### Scenario 2: Loading Data from External Source

```
Step 1: Frontend - Data Connector Selection
   ├─ User clicks "Connect Data"
   ├─ Modal shows available connectors
   └─ User selects "PostgreSQL"
   
Step 2: Frontend → Backend (Connector Config)
   ├─ POST /api/connectors/validate
   ├─ Payload: { type: "postgresql", host, port, database, credentials }
   └─ Response: { valid: true, tables: [...] }
   
Step 3: Backend - Credential Handling
   ├─ Validate connection
   ├─ Store in TokenStore/Vault (encrypted)
   └─ Return available tables
   
Step 4: Frontend - Table Selection
   ├─ Display list of tables from connector
   ├─ User selects tables to load
   └─ Click "Load Data"
   
Step 5: Frontend → Backend (Load Tables)
   ├─ POST /api/agents/run
   ├─ Instruction: "Load tables [table1, table2] from PostgreSQL"
   └─ Stream agent response
   
Step 6: Backend - Data Loading Agent
   ├─ Use data_loading skill
   ├─ Execute connector loader
   │  ├─ Connect to PostgreSQL
   │  ├─ Query table schemas
   │  ├─ Load data into DuckDB
   │  └─ Infer semantic types (ID, Measure, Date, etc.)
   ├─ Save to workspace storage (Parquet)
   └─ Return table metadata
   
Step 7: Frontend - State Update
   ├─ Redux: workspace/addTable()
   ├─ Add to tables list
   └─ Display in data explorer
   
Step 8: Ready for Analysis
   └─ User can now ask questions about loaded tables
```

**Timeline**: 5-30 seconds (depending on data size)  
**Key Files**:
- Backend: `py-src/data_formulator/data_loader/loaders/*.py`
- Backend: `py-src/data_formulator/analyst/skills/data_load/`

---

### Scenario 3: Branching Analysis (Data Thread)

```
Step 1: User Viewing Current Analysis
   ├─ Thread 1: "Sales by Region" (active)
   └─ Shows bar chart, some insights
   
Step 2: User Action: "Branch Here"
   ├─ Click "Create Branch" button
   └─ Frontend: createThread() action
   
Step 3: Frontend → Backend
   ├─ POST /api/workspaces/{id}/threads
   ├─ Payload: { parentThreadId, branchPoint, question }
   └─ Response: { threadId, newThread: {...} }
   
Step 4: Backend - Thread Creation
   ├─ Load parent thread state
   ├─ Copy data context up to branch point
   ├─ Create new thread object
   └─ Save to workspace storage
   
Step 5: Frontend - New Thread Display
   ├─ Redux: workspace/addThread()
   ├─ Tab bar shows: [Thread 1] [Thread 2 - new]
   ├─ Switch to Thread 2
   └─ Display empty analysis
   
Step 6: User Asks New Question in Thread 2
   ├─ "Show me sales by product instead"
   ├─ SSE POST to /api/agents/run with threadId
   ├─ Backend loads Thread 2 context (different data focus)
   └─ Execute new agent reasoning
   
Step 7: Compare Analysis Paths
   ├─ Split view shows Thread 1 and Thread 2 side-by-side
   ├─ User can switch between threads
   └─ Different visualizations reflect different analysis paths
```

**Key Concept**: Data Threads enable non-linear exploration  
**Key Files**:
- Frontend: `src/app/App.tsx` (thread management)
- Backend: `py-src/data_formulator/api/workspace_bp.py`

---

## Backend Deep Dive

### Entry Points

#### 1. CLI Entry (`__main__.py`)
```python
# Starts Flask development server
# Command: uv run data_formulator
# Listen on: http://localhost:5567
```

#### 2. Flask Application Factory (`app.py`)
```python
def create_app():
    # Initialize Flask app
    # Register blueprints (lazy-loaded)
    # Setup error handlers
    # Configure CORS, rate limiting
    # Return app instance
```

#### 3. Desktop Entry (`desktop.py`)
```python
# PyWebView integration for desktop app
# Bundles frontend (dist/) + backend
# Single-window application
```

### Core Modules

#### `model_registry.py` - LLM Provider Discovery
```python
# Maps provider names to LiteLLM models
# Discovers available models at runtime
# Supports: OpenAI, Azure, Anthropic, custom endpoints
# Configuration via environment variables
```

#### `agent_config.py` - Agent Reasoning Effort
```python
# Defines reasoning effort levels:
#   - minimal: Few LLM calls
#   - low: Standard reasoning
#   - medium: More thinking steps
#   - high: Extended reasoning (o1, etc.)
```

#### `workspace_factory.py` - Storage Backend Selection
```python
# Abstract workspace storage:
#   - local: Filesystem storage
#   - ephemeral: In-memory (RAM)
#   - azure_blob: Azure Blob Storage
# Abstracts save/load operations
```

#### `data_connector.py` - Data Source Abstraction
```python
# Base class for all data sources
# Lifecycle: validate → authenticate → load → query
# Manages credentials and connections
```

### API Blueprints

#### Authentication (`api/auth_bp.py`)
```
Routes:
  GET  /auth/login          → Redirect to OAuth provider
  GET  /auth/callback       → Process OAuth callback
  POST /auth/logout         → Clear session
  GET  /auth/me             → Get current user
  POST /auth/refresh_token  → Refresh JWT token
```

#### Workspace Management (`api/workspace_bp.py`)
```
Routes:
  GET    /workspaces              → List user's workspaces
  POST   /workspaces              → Create new workspace
  GET    /workspaces/{id}         → Load workspace
  PUT    /workspaces/{id}         → Update workspace
  DELETE /workspaces/{id}         → Delete workspace
  POST   /workspaces/{id}/threads → Create thread
  GET    /workspaces/{id}/export  → Export as report
```

#### Agent Execution (`api/agents_bp.py`)
```
Routes:
  POST   /agents/run              → Execute agent (SSE streaming)
  GET    /agents/run              → Accept SSE connection
  POST   /agents/explore          → Explore data (single call)
  GET    /agents/status           → Get agent execution status
```

#### Data Operations (`api/data_bp.py`)
```
Routes:
  GET    /data/tables             → List loaded tables
  GET    /data/tables/{id}        → Get table schema
  POST   /data/query              → Execute SQL query
  POST   /data/sample             → Get data sample
  POST   /data/infer_types        → Infer semantic types
```

#### Connectors (`api/connectors_bp.py`)
```
Routes:
  GET    /connectors              → List available connectors
  POST   /connectors/validate     → Validate credentials
  POST   /connectors/explore      → List remote tables
  POST   /connectors/load         → Load remote data
```

### Agent System

#### Modern Analyst Agent (`analyst/`)

**Architecture**:
```
Input (Question)
  ↓
[LLM Router] - Decides what to do
  ↓
[Tool Calling Loop]
  ├─ inspect: Query workspace state
  ├─ call: Execute data operations
  └─ action: Mark step complete
  ↓
[Skill System]
  ├─ core: Always active (reasoning, planning)
  ├─ data_load: Load external data
  ├─ visualize: Create charts
  └─ report: Generate insights
  ↓
Output (Visualization + Insights)
```

**Key Classes**:
- `AnalystAgent`: Main agent class
- `ToolCallHandler`: Processes tool invocations
- `SkillManager`: Loads and manages skills
- `Context`: Holds workspace, thread, state

#### Legacy Agents (`agents/`)

Individual agents for specific tasks (deprecated in v0.8.0b1):
- `agent_simple.py`: Basic data loading
- `agent_data_load.py`: External data connection
- `agent_chart_insight.py`: Chart synthesis
- `agent_exploration.py`: Data exploration

### Data Loading System

#### Loaders (`data_loader/loaders/`)

**SQL Databases**:
- `postgresql_loader.py`: PostgreSQL connector
- `mysql_loader.py`: MySQL connector
- `mssql_loader.py`: SQL Server connector
- `kusto_loader.py`: Azure Data Explorer
- `databricks_loader.py`: Databricks SQL

**Cloud Storage**:
- `s3_loader.py`: Amazon S3
- `azure_blob_loader.py`: Azure Blob Storage
- `bigquery_loader.py`: Google BigQuery
- `athena_loader.py`: AWS Athena

**Document Stores**:
- `mongodb_loader.py`: MongoDB
- `cosmosdb_loader.py`: Azure CosmosDB

**APIs & Local**:
- `google_sheets_loader.py`: Google Sheets
- `yfinance_loader.py`: Stock data
- `weather_loader.py`: Weather APIs
- `local_file_loader.py`: CSV, JSON, Excel, Parquet
- `sample_loader.py`: Built-in datasets

#### Loading Pipeline

```python
# 1. Connector Discovery
connectors = discover_connectors()
# Returns available data sources

# 2. Configuration
loader = get_loader(type="postgresql")
config = validate_config(host, port, database, credentials)

# 3. Authentication
loader.authenticate(credentials, vault)
# Stores credentials securely

# 4. Exploration
tables = loader.list_tables()
schema = loader.get_table_schema(table_name)

# 5. Loading
data_df = loader.load_table(table_name)

# 6. Type Inference
semantic_types = infer_semantic_types(data_df)
# ID, Measure, Date, Region, Ordinal, Categorical

# 7. Storage
save_to_workspace(table_name, data_df, semantic_types)
# Parquet + metadata JSON
```

### Storage & Persistence

#### Datalake (`datalake/`)

```
workspace_storage/
├── workspaces/
│   ├── {workspace_id}/
│   │   ├── metadata.json           # Workspace metadata
│   │   ├── tables/
│   │   │   ├── {table_id}.parquet  # Table data
│   │   │   └── {table_id}.json     # Schema + types
│   │   └── threads/
│   │       ├── {thread_id}.json    # Thread state
│   │       └── {thread_id}/
│   │           ├── results/
│   │           ├── messages/
│   │           └── charts/
```

**Backend Options**:
- **Local**: Filesystem at `~/.data_formulator/`
- **Ephemeral**: In-memory storage (testing, sessions)
- **Azure Blob**: Cloud storage with `WORKSPACE_STORAGE_ACCOUNT`

#### Save/Load Operations

```python
# Save workspace
workspace.save()  # → datalake.save_workspace()
# Serializes: tables, threads, metadata
# Format: Parquet + JSON

# Load workspace
workspace = load_workspace(workspace_id)  # → datalake.load_workspace()
# Deserializes: reconstructs tables, threads
# Lazy loads: data only when accessed
```

### Authentication & Authorization

#### Providers (`auth/`)

**OIDC (OpenID Connect)**:
```python
# Redirect to identity provider
# Exchange code for tokens
# Verify JWT, extract claims
# Populate user info
```

**GitHub OAuth**:
```python
# Redirect to GitHub
# Get access token
# Call GitHub API for user info
# Optional team/org verification
```

**Kusto (Azure Data Explorer)**:
```python
# Service principal auth
# Get access token from AAD
# Scope: Kusto cluster
```

**Transparent (No Auth)**:
```python
# No login required
# Anonymous access
# For dev/testing
```

#### Token Management

**TokenStore** (`auth/token_store.py`):
```python
# Server-side session storage (SQLite)
# Stores: access tokens, refresh tokens, user info
# Encrypted with rotating keys
# Enables SSO across tabs/devices
```

#### Credential Vault (`auth/vault/`)

```python
# Secure storage for data source credentials
# Encrypted at rest
# Per-workspace credential scoping
# Accessible only within server process
```

### Error Handling

#### Error System (`errors.py`)

```python
# Unified ErrorCode enum (40+ error types)
class ErrorCode(Enum):
    AUTH_REQUIRED           # Authentication needed
    CONNECTOR_NOT_FOUND     # Missing data source
    DATA_LOAD_FAILED        # Failed to load data
    LLM_API_ERROR           # LLM provider error
    QUERY_EXECUTION_ERROR   # SQL query failed
    INVALID_INPUT           # Bad request data
    # ... 34 more error types
```

#### Error Handler (`error_handler.py`)

```python
# Global error handlers
# Returns: HTTP 200 + JSON envelope
# Format: { success: false, error: { code, message, details } }
# Never returns 4xx/5xx status codes
# Allows client to parse with consistent format
```

---

## Frontend Deep Dive

### Directory Structure

```
src/
├── App.tsx                    # Root component
├── index.tsx                  # Entry point
├── index.css                  # Global styles
├── types.d.ts                 # Type definitions
├── mui.d.ts                   # MUI augmentation
│
├── app/                       # Application logic & Redux
│   ├── App.tsx                # Main layout
│   ├── AuthButton.tsx         # Auth UI
│   ├── apiClient.ts           # HTTP + SSE client
│   ├── chartCache.ts          # Chart caching
│   ├── chartRecommendation.ts # Recommendation engine
│   ├── connectorFormPersistence.ts
│   ├── thunks/                # Async Redux actions
│   └── slices/                # Redux state slices
│       ├── auth.ts            # Auth state
│       ├── workspace.ts       # Workspace state
│       ├── agent.ts           # Agent state
│       ├── chart.ts           # Chart state
│       ├── connectors.ts      # Connector state
│       └── ui.ts              # UI state
│
├── components/                # Reusable components
│   ├── DataTable/
│   ├── ChartRenderer/
│   ├── DataConnector/
│   ├── AgentMessage/
│   ├── ThreadList/
│   ├── WorkspaceSelector/
│   └── [50+ more components]
│
├── data/                      # Data operations
│   ├── operations.ts          # Data transformations
│   ├── type-coercion.ts       # Type conversion
│   ├── type-inference.ts      # Semantic type detection
│   └── vega-lite-mapping.ts   # Chart spec generation
│
├── dataOperations/            # Legacy data logic
├── i18n/                      # Localization
│   ├── config.ts              # i18next setup
│   ├── en/                    # English translations
│   └── zh/                    # Chinese translations
│
├── scss/                      # Styles
│   ├── app.scss               # App styles
│   ├── variables.scss         # Design tokens
│   └── [theme, components]
│
├── views/                     # Page-level components
│   ├── WorkspaceView/
│   ├── ChartView/
│   ├── ReportView/
│   ├── DataLoaderView/
│   └── AnalysisView/
│
├── assets/                    # Images, icons, docs
└── api/                       # API type definitions
    └── knowledgeApi.ts        # Knowledge base API
```

### Redux State Management

#### Store Structure

```typescript
interface DataFormulatorState {
  // Authentication
  auth: {
    user: User | null;
    isLoggedIn: boolean;
    token: string | null;
    permissions: string[];
  };

  // Workspace & Data
  workspace: {
    workspaces: Workspace[];
    activeWorkspaceId: string;
    tables: { [tableId: string]: Table };
    metadata: WorkspaceMetadata;
    isLoading: boolean;
  };

  // Analysis threads
  threads: {
    activeThreadId: string;
    threads: { [threadId: string]: Thread };
    threadMessages: { [threadId: string]: Message[] };
  };

  // Agent execution
  agent: {
    isRunning: boolean;
    currentMessage: string;
    streamingState: "init" | "message" | "action" | "complete";
    reasoning: string[];
    lastAction: string | null;
  };

  // Chart & visualization
  chart: {
    displayInstructions: { [threadId: string]: VegaLiteSpec };
    recommendations: ChartRecommendation[];
    selectedChart: string | null;
    chartTheme: "light" | "dark";
  };

  // Data connectors
  connectors: {
    availableConnectors: ConnectorType[];
    connectorConfig: ConnectorConfig | null;
    validationResult: ValidationResult | null;
  };

  // UI state
  ui: {
    sidebarOpen: boolean;
    modalOpen: boolean;
    selectedTableId: string | null;
    splitView: boolean;
    darkMode: boolean;
  };
}
```

#### Key Slices (Redux)

**`auth.ts` - Authentication**
```typescript
// Actions
setUser(user)
setToken(token)
logout()
updatePermissions(permissions)

// Selectors
selectUser()
selectIsLoggedIn()
selectUserPermissions()
```

**`workspace.ts` - Data & Tables**
```typescript
// Actions
loadWorkspace(workspaceId)
addTable(table)
updateTableMetadata(tableId, metadata)
deleteTable(tableId)
createThread(parentThreadId)

// Selectors
selectActiveWorkspace()
selectTables()
selectTableById(tableId)
selectThreads()
```

**`agent.ts` - LLM Reasoning**
```typescript
// Actions
startAgentRun()
streamInit(message)
streamMessage(chunk)
streamAction(action)
streamComplete(result)
stopAgentRun()

// Selectors
selectIsAgentRunning()
selectReasoningChain()
selectCurrentResult()
```

**`chart.ts` - Visualization**
```typescript
// Actions
setDisplayInstruction(spec)
setRecommendations(charts)
selectChart(chartId)
updateChartTheme(theme)

// Selectors
selectDisplayInstruction()
selectChartRecommendations()
selectSelectedChart()
```

### React Components

#### Main Layout (`App.tsx`)

```
<App>
  ├─ <Header>
  │   ├─ Logo
  │   ├─ WorkspaceSelector
  │   ├─ ThreadTabs
  │   └─ AuthButton
  │
  ├─ <MainContent>
  │   ├─ <Sidebar>
  │   │   ├─ WorkspaceTree
  │   │   └─ TableList
  │   │
  │   └─ <ContentArea>
  │       ├─ <ChartView>
  │       │   ├─ FlintChart (visualization)
  │       │   ├─ ChartControls (styling)
  │       │   └─ InsightPanel
  │       │
  │       ├─ <AgentInteraction>
  │       │   ├─ MessageInput
  │       │   └─ StreamingOutput
  │       │
  │       └─ <DataTable>
  │           ├─ TableHeader
  │           └─ RowList
  │
  └─ <Modals>
      ├─ DataConnectorModal
      ├─ WorkspaceModal
      └─ ExportModal
```

#### ChartView Component

```typescript
function ChartView() {
  const displayInstruction = useAppSelector(selectDisplayInstruction);
  const recommendations = useAppSelector(selectChartRecommendations);

  return (
    <div className="chart-view">
      <FlintChart 
        spec={displayInstruction}
        onDataClick={handleDataClick}
        onExport={handleExport}
      />
      <ChartRecommendations charts={recommendations} />
    </div>
  );
}
```

#### DataConnector Component

```typescript
function DataConnector() {
  const dispatch = useAppDispatch();
  const connectors = useAppSelector(selectAvailableConnectors);
  const validationResult = useAppSelector(selectValidationResult);

  // Form submission flow:
  // 1. User fills connector form
  // 2. Click "Validate"
  // 3. POST /api/connectors/validate
  // 4. Show available tables
  // 5. User selects tables
  // 6. Click "Load"
  // 7. Agent loads tables
}
```

### API Client

#### HTTP Request Builder (`apiClient.ts`)

```typescript
// Standard HTTP calls
async function fetchTables(workspaceId: string) {
  return fetch(`/api/data/tables?workspaceId=${workspaceId}`)
    .then(r => r.json());
}

// SSE Streaming
async function* runAgent(workspaceId: string, question: string) {
  const response = await fetch('/api/agents/run', {
    method: 'POST',
    headers: { 'Accept': 'text/event-stream' },
    body: JSON.stringify({ workspaceId, question })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    
    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const event = JSON.parse(line.slice(6));
        yield event;
      }
    }
  }
}
```

#### Redux Thunks (Async Actions)

```typescript
export const runAgentQuery = createAsyncThunk(
  'agent/runQuery',
  async (args: { workspaceId: string; question: string }) => {
    const stream = runAgent(args.workspaceId, args.question);
    
    for await (const event of stream) {
      if (event.type === 'init') {
        dispatch(agent/streamInit(event));
      } else if (event.type === 'message') {
        dispatch(agent/streamMessage(event.chunk));
      } else if (event.type === 'action') {
        dispatch(agent/streamAction(event));
      } else if (event.type === 'complete') {
        dispatch(agent/streamComplete(event.result));
      }
    }
  }
);
```

### Data Operations

#### Type Inference (`type-inference.ts`)

```typescript
function inferSemanticType(column: string[], name: string): SemanticType {
  // Check if column looks like:
  // - ID: unique, numeric or UUID
  // - Date: parseable dates
  // - Region: geographic names
  // - Measure: numeric, statistical
  // - Ordinal: small unique values
  // - Categorical: strings, small cardinality
  
  // Returns: "id" | "measure" | "date" | "region" | "ordinal" | "categorical"
}
```

#### Type Coercion (`type-coercion.ts`)

```typescript
function coerceValue(value: any, targetType: SemanticType): any {
  switch (targetType) {
    case 'date':
      return new Date(value);
    case 'measure':
      return parseFloat(value);
    case 'id':
      return String(value);
    // ...
  }
}
```

#### Vega-Lite Mapping (`vega-lite-mapping.ts`)

```typescript
function generateVegaSpec(
  data: any[],
  xField: string,
  yField: string,
  chartType: string
): VegaLiteSpec {
  return {
    $schema: 'https://vega.github.io/schema/vega-lite/v5.json',
    data: { values: data },
    mark: chartType,
    encoding: {
      x: { field: xField, type: getVegaType(xField) },
      y: { field: yField, type: getVegaType(yField) }
    }
  };
}
```

### Localization (i18n)

#### Configuration (`i18n/config.ts`)

```typescript
i18n
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: enTranslations },
      zh: { translation: zhTranslations }
    },
    lng: navigator.language.startsWith('zh') ? 'zh' : 'en',
    fallbackLng: 'en',
    interpolation: { escapeValue: false }
  });
```

#### Usage in Components

```typescript
function ChartViewHeader() {
  const { t } = useTranslation();
  
  return (
    <h1>{t('charts.title')}</h1>
    <p>{t('charts.description')}</p>
  );
}
```

#### Translation Structure

```
i18n/
├── en/
│   ├── common.json      # General UI terms
│   ├── charts.json      # Chart-specific
│   ├── data.json        # Data loading
│   ├── agent.json       # Agent interactions
│   └── errors.json      # Error messages
└── zh/
    ├── common.json
    ├── charts.json
    ├── data.json
    ├── agent.json
    └── errors.json
```

### Build Configuration

#### Vite Config (`vite.config.ts`)

```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:5567'  // Dev proxy
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendors': ['react', 'react-dom'],
          'redux': ['@reduxjs/toolkit', 'react-redux'],
          'ui': ['@mui/material', '@emotion/react']
        }
      }
    }
  }
});
```

#### Chunk Strategy

Production build splits code:
- `index-*.js`: Main app
- `react-vendors-*.js`: React/ReactDOM
- `redux-*.js`: Redux
- `ui-*.js`: Material-UI
- `flint-chart-*.js`: Chart library

This reduces initial load and improves caching.

---

## Communication Patterns

### 1. RESTful HTTP (Request-Response)

**Used for**: Non-streaming operations (CRUD, validation)

```
Client                              Server
  │                                   │
  ├─ GET /api/workspaces ──────────→  │
  │                         (List workspaces)
  │                                   │
  │  ← ─ ─ 200 OK [workspaces] ─ ─ ─ ┤
  │                                   │
  ├─ POST /api/data/query ───────────→  │
  │  { sql: "SELECT * FROM table" }  │
  │                                   │
  │  ← ─ ─ 200 OK [results] ─ ─ ─ ─ ─┤
  │                                   │
```

### 2. Server-Sent Events (SSE Streaming)

**Used for**: Agent execution (streaming responses)

```
Client                              Server
  │                                   │
  ├─ POST /api/agents/run ──────────→  │
  │  { question: "..." }              │
  │  Headers: Accept: text/event-stream
  │                                   │
  │  ← ─ data: {type:init,...} ─ ─ ─┤
  │  ← ─ data: {type:message,...} ─ ┤
  │  ← ─ data: {type:action,...} ─ ┤
  │  ← ─ data: {type:complete,...} ─┤
  │                                   │
```

**Event Stream Format**:

```
data: {"type":"init","message":"Analyzing data..."}
data: {"type":"message","chunk":"I can see that"}
data: {"type":"message","chunk":" sales increased"}
data: {"type":"action","step":"Creating visualization"}
data: {"type":"complete","result":{"spec":{...},"insights":"..."}}
```

### 3. Error Handling Pattern

**Backend returns HTTP 200 for all requests** (including errors)

**Response Format**:
```json
{
  "success": true,
  "data": { /* operation result */ }
}
```

or

```json
{
  "success": false,
  "error": {
    "code": "DATA_LOAD_FAILED",
    "message": "Could not connect to PostgreSQL",
    "details": "Connection refused: localhost:5432"
  }
}
```

**Frontend handling**:
```typescript
const response = await fetch('/api/agents/run', ...);
const json = await response.json();

if (json.success) {
  // Handle success
} else {
  // Handle error (but HTTP status is still 200)
  console.error(json.error.code, json.error.message);
}
```

### 4. State Synchronization

**Eventual Consistency Model**:

1. Frontend optimistically updates Redux state
2. Sends request to backend
3. Backend validates and persists
4. Frontend receives confirmation
5. If error, frontend reverts state

**Example** (Create Thread):
```typescript
// 1. Optimistic update
dispatch(workspace/addThread({ id: tempId, name: "Branch 1" }));

// 2. Send to server
const response = await createThreadAPI(workspaceId, { name: "Branch 1" });

// 3. Confirmation
if (response.success) {
  // Update with real ID from server
  dispatch(workspace/updateThreadId({ tempId, realId: response.data.id }));
} else {
  // Revert
  dispatch(workspace/removeThread(tempId));
}
```

---

## Development Workflow

### Local Development Setup

#### Backend Setup

```bash
# 1. Navigate to project root
cd /path/to/data-formulator

# 2. Create virtual environment (already done via uv)
source .venv/bin/activate

# 3. Install in editable mode
uv pip install -e .

# 4. Install dev dependencies
uv pip install pytest pytest-cov black flake8

# 5. Run backend server
uv run data_formulator
# Server runs on http://localhost:5567

# 6. In another terminal, run tests
uv run pytest tests/ -v
```

#### Frontend Setup

```bash
# 1. Navigate to project root
cd /path/to/data-formulator

# 2. Install dependencies
npm install

# 3. Start dev server (with proxy to backend)
npm run dev
# Frontend at http://localhost:5173
# Auto-proxies /api to http://localhost:5567

# 4. In another terminal, watch tests
npm run test:watch

# 5. Build production
npm run build
# Output: dist/
```

### Development Workflow: Adding a New Feature

#### Scenario: Add Support for new CSV Loader

**1. Create Backend Loader** (`py-src/data_formulator/data_loader/loaders/csv_advanced_loader.py`)

```python
from .loader_base import LoaderBase

class CSVAdvancedLoader(LoaderBase):
    """Advanced CSV loader with delimiter detection."""
    
    name = "csv_advanced"
    display_name = "Advanced CSV"
    
    def validate_config(self, config):
        """Check config has required fields."""
        return "file_path" in config
    
    def explore(self):
        """List available CSV files."""
        return {"files": [...]}
    
    def load_table(self, table_name):
        """Load CSV with auto-detection."""
        df = pd.read_csv(...)
        return df
```

**2. Register Loader** (`py-src/data_formulator/data_loader/__init__.py`)

```python
from .loaders.csv_advanced_loader import CSVAdvancedLoader

AVAILABLE_LOADERS = {
    "csv_advanced": CSVAdvancedLoader,
    # ... other loaders
}
```

**3. Create Frontend Component** (`src/components/DataConnector/CSVAdvancedForm.tsx`)

```typescript
function CSVAdvancedForm({ onLoadTable }) {
  const [filePath, setFilePath] = useState("");
  
  const handleLoad = async () => {
    const result = await apiClient.loadData({
      type: "csv_advanced",
      file_path: filePath
    });
    
    if (result.success) {
      onLoadTable(result.data);
    }
  };
  
  return (
    <div>
      <input 
        value={filePath}
        onChange={e => setFilePath(e.target.value)}
        placeholder="Path to CSV file"
      />
      <button onClick={handleLoad}>Load</button>
    </div>
  );
}
```

**4. Add Frontend Slice** (`src/app/slices/connectors.ts`)

```typescript
const connectorsSlice = createSlice({
  name: 'connectors',
  initialState,
  reducers: {
    addConnectorType(state, action) {
      state.availableConnectors.push(action.payload);
    }
  }
});

// On app init:
dispatch(addConnectorType({
  name: "csv_advanced",
  displayName: "Advanced CSV",
  component: CSVAdvancedForm
}));
```

**5. Test Locally**

```bash
# Backend test
uv run pytest tests/test_csv_advanced_loader.py -v

# Frontend test
npm run test -- CSVAdvancedForm.test.tsx

# Manual test
# 1. Start backend: uv run data_formulator
# 2. Start frontend: npm run dev
# 3. Create workspace, click "Add Data"
# 4. Select "Advanced CSV"
# 5. Enter path and load
```

**6. Build & Deploy**

```bash
# Backend
uv pip install -e .  # No change needed (already installed in editable mode)

# Frontend
npm run build
# Creates dist/ with updated bundle
```

### Code Structure Best Practices

#### Backend File Organization

```
py-src/data_formulator/
├── core/
│   ├── __init__.py
│   └── models.py           # Core data models
├── api/
│   ├── __init__.py
│   └── endpoints_bp.py     # API routes
├── services/
│   ├── __init__.py
│   └── data_service.py     # Business logic
├── data_loader/
│   ├── loaders/
│   │   └── loader_base.py  # Abstract base
│   └── __init__.py
└── tests/
    ├── test_services.py
    └── test_loaders.py
```

**Dependency Injection Pattern**:
```python
# Avoid circular imports and tight coupling
app = Flask(__name__)
db = Database()  # Initialized elsewhere

def create_app(database=None):
    app.database = database or Database()
    return app
```

#### Frontend Component Structure

```
src/components/
├── MyComponent/
│   ├── MyComponent.tsx     # Main component
│   ├── MyComponent.test.tsx
│   ├── MyComponent.module.scss
│   ├── useMyComponentLogic.ts  # Custom hook
│   ├── types.ts            # TypeScript interfaces
│   └── index.ts            # Exports
```

**Custom Hooks Pattern**:
```typescript
// src/hooks/useAgentStream.ts
export function useAgentStream() {
  const dispatch = useAppDispatch();
  const isRunning = useAppSelector(selectIsAgentRunning);
  
  const runAgent = async (question: string) => {
    dispatch(agent/startRun());
    // Handle streaming...
  };
  
  return { isRunning, runAgent };
}

// Usage in component
function ChartView() {
  const { isRunning, runAgent } = useAgentStream();
  // ...
}
```

---

## Debugging & Troubleshooting

### Backend Debugging

#### 1. Enable Debug Logging

```python
# In app.py or environment
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Log levels**:
- `DEBUG`: Detailed info (API calls, database queries)
- `INFO`: General info (server startup, requests)
- `WARNING`: Issues that might need attention
- `ERROR`: Errors that should be fixed
- `CRITICAL`: System failures

#### 2. Common Backend Issues

**Issue**: "Module not found: data_formulator"

```bash
# Solution: Install in editable mode
uv pip install -e .
```

**Issue**: "LLM API key not found"

```bash
# Solution: Set environment variable
export OPENAI_API_KEY=sk-...
uv run data_formulator
```

**Issue**: "DuckDB connection failed"

```bash
# Solution: Check data file exists and is readable
# Check file permissions
ls -la /path/to/data.parquet
```

**Issue**: "Agent streaming timeout"

```bash
# Solution: Check backend logs
tail -f ~/.data_formulator/logs/app.log

# Increase timeout in frontend:
// src/app/apiClient.ts
fetch(url, { timeout: 120000 })  // 120 seconds
```

#### 3. Interactive Debugging

```bash
# Run Flask with debugger
FLASK_DEBUG=1 uv run python py-src/data_formulator/__main__.py

# Add breakpoints in code
import pdb; pdb.set_trace()

# Use ipdb for better experience
uv pip install ipdb
import ipdb; ipdb.set_trace()
```

### Frontend Debugging

#### 1. Browser DevTools

```javascript
// Open Chrome DevTools (F12)
// Console tab: View logs, errors, warnings

// Redux DevTools Extension
// View: Redux action history, state changes

// Network tab: Monitor API calls
// See request/response payloads
```

#### 2. Common Frontend Issues

**Issue**: "API calls fail with 404"

```javascript
// Solution: Check proxy configuration
// vite.config.ts should proxy /api to backend
// Or set VITE_API_BASE_URL environment variable
```

**Issue**: "Redux state not updating"

```typescript
// Solution: Check Redux DevTools
// Verify action is dispatched
// Verify reducer handles action
// Check selector logic

// Debug in component
const state = useAppSelector(selectWorkspace);
console.log('Current workspace:', state);
```

**Issue**: "Chart not rendering"

```typescript
// Solution: Check Flint spec
// Open DevTools → Network → /api/agents/run
// Look at response.result.spec
// Validate spec at https://vega.github.io/editor/

// Check data
console.log('Display instruction:', displayInstruction);
console.log('Chart data:', displayInstruction.data.values);
```

#### 3. Redux DevTools

Install browser extension:
- [Redux DevTools Chrome Extension](https://chrome.google.com/webstore/detail/redux-devtools)

**Usage**:
1. Open DevTools (F12) → Redux tab
2. See all dispatched actions
3. Time-travel debug: click any action to revert/replay
4. Inspect state at each step
5. Export/import action history

### Testing

#### Backend Testing

```bash
# Run all tests
uv run pytest

# Run specific test
uv run pytest tests/test_agents.py::test_analyst_agent_initialization -v

# Run with coverage
uv run pytest --cov=py-src/data_formulator tests/

# Run specific loader test
uv run pytest tests/data_loader/test_postgresql_loader.py -v
```

**Test Structure**:
```python
# tests/test_agents.py
def test_analyst_agent_initialization():
    agent = AnalystAgent()
    assert agent.skills is not None
    assert "core" in agent.skills

def test_agent_reasoning_with_mock_llm():
    agent = AnalystAgent(llm=MockLLM())
    result = agent.run(question="...", workspace=test_workspace)
    assert result.success
```

#### Frontend Testing

```bash
# Run all tests
npm run test

# Run in watch mode
npm run test:watch

# Run specific test
npm run test -- ChartView.test.tsx

# Run with coverage
npm run test -- --coverage
```

**Test Structure**:
```typescript
// src/components/ChartView/ChartView.test.tsx
describe('ChartView', () => {
  it('renders chart from Redux state', () => {
    const { getByRole } = render(<ChartView />, {
      preloadedState: {
        chart: {
          displayInstructions: {
            [threadId]: vegaLiteSpec
          }
        }
      }
    });
    
    expect(getByRole('img')).toBeInTheDocument();
  });
});
```

### Performance Optimization

#### Backend Performance

**1. Query Optimization**
```python
# DuckDB query analysis
import duckdb
connection = duckdb.connect()
result = connection.execute(
    "EXPLAIN SELECT * FROM large_table WHERE id = 1"
).fetchall()
print(result)  # Shows query plan
```

**2. Caching**
```python
# Cache expensive operations
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_computation(param):
    # Only computes once per unique param
    return result
```

**3. Async/Streaming**
```python
# Use generator for large result sets
def fetch_large_dataset():
    for chunk in data_chunks:
        yield chunk  # Stream instead of loading all
```

#### Frontend Performance

**1. Redux Selectors**
```typescript
// Create memoized selectors (reselect)
const selectVisibleTables = createSelector(
  [selectAllTables, selectFilter],
  (tables, filter) => tables.filter(t => matches(t, filter))
);
// Only recomputes if input selectors change
```

**2. Component Memoization**
```typescript
// Prevent unnecessary re-renders
export const ChartView = memo(
  function ChartViewComponent() { /* ... */ },
  (prevProps, nextProps) => {
    // Return true if props are equal (skip render)
    return prevProps.specId === nextProps.specId;
  }
);
```

**3. Code Splitting**
```typescript
// Lazy load heavy components
const ReportView = lazy(() => import('./views/ReportView'));

// Use in component
<Suspense fallback={<Spinner />}>
  <ReportView />
</Suspense>
```

---

## Additional Resources

### Documentation Links

- [Detailed Backend Architecture](BACKEND_ARCHITECTURE_GUIDE.md)
- [Detailed Frontend Architecture](FRONTEND_ARCHITECTURE.md)
- [Original Architecture Guide](ARCHITECTURE_GUIDE.md)
- [Development Guides](docs/dev-guides/)
- [Data Connector Development](docs/dev-guides/5-data-connector-api.md)
- [Error Handling](docs/dev-guides/7-unified-error-handling.md)

### Key Configuration Files

- **Backend**: `pyproject.toml`, `pytest.ini`, `py-src/data_formulator/app.py`
- **Frontend**: `package.json`, `vite.config.ts`, `vitest.config.ts`, `tsconfig.json`

### External References

- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://react.dev/)
- [Redux Documentation](https://redux.js.org/)
- [DuckDB Documentation](https://duckdb.org/docs/)
- [LiteLLM Documentation](https://docs.litellm.ai/)
- [Material-UI Documentation](https://mui.com/)

---

## Conclusion

This comprehensive guide covers the data-formulator codebase from multiple perspectives:

1. **System Architecture**: How all layers interact
2. **End-to-End Flows**: Complete scenarios from user action to result
3. **Backend Deep Dive**: API, agents, data loaders, storage
4. **Frontend Deep Dive**: Redux, components, API client, i18n
5. **Communication**: REST, SSE, error handling
6. **Development**: Setup, workflow, testing
7. **Debugging**: Tools, common issues, optimization

### Quick Navigation

- **Need to add a data source?** → See Backend Deep Dive → Data Loading System
- **Need to fix a UI component?** → See Frontend Deep Dive → React Components
- **Need to understand data flow?** → See End-to-End Data Flow section
- **Getting an error?** → See Debugging & Troubleshooting
- **Want to optimize performance?** → See Debugging & Troubleshooting → Performance

For detailed information on specific subsystems, refer to the linked architecture guides.

---

**Last Updated**: 2026-09-01  
**Project Version**: 0.8.0b1  
**Maintained By**: Data Formulator Team
