# Data Formulator: Complete Backend-to-Frontend Architecture Guide

**Version**: 0.8.0b1  
**Purpose**: AI-powered data visualization & exploration platform  
**Last Updated**: 2026

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Directory Structure](#directory-structure)
4. [Backend Architecture](#backend-architecture)
5. [Frontend Architecture](#frontend-architecture)
6. [Communication Protocols](#communication-protocols)
7. [Data Flow Examples](#data-flow-examples)
8. [Key Concepts](#key-concepts)
9. [Development Workflow](#development-workflow)
10. [Deployment & Configuration](#deployment--configuration)

---

## Project Overview

**Data Formulator** is an intelligent data exploration platform that:
- Allows users to load data from 15+ sources (databases, cloud, local files)
- Enables natural language queries through AI agents
- Supports branching analysis paths called "Data Threads"
- Renders interactive visualizations with 30+ chart types
- Persists sessions and workspaces for collaborative work
- Provides a unified analytics interface

**Key Features**:
- Multi-language support (English, Chinese)
- Server-side and Desktop deployment options
- Real-time streaming responses from AI agents
- Credential vault for secure data source authentication
- Sandbox isolation for code execution
- Support for complex LLM reasoning workflows

---

## Technology Stack

### Backend
| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Framework** | Flask | Web server & API |
| **Language** | Python 3.11+ | Core logic |
| **Data Engine** | DuckDB | In-memory SQL queries |
| **Storage** | Parquet, JSON | Persistent data storage |
| **LLM** | LiteLLM | Multi-provider LLM support |
| **Authentication** | OAuth 2.0, OIDC, GitHub | User authentication |
| **Logging** | Python logging | Structured logging |

### Frontend
| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Framework** | React 18 | UI components |
| **Language** | TypeScript | Type-safe development |
| **State** | Redux | Application state management |
| **UI Components** | Material-UI v7 | Component library |
| **Charts** | Flint | Semantic chart rendering |
| **Build Tool** | Vite | Module bundler |
| **Code Editor** | CodeMirror | Syntax-highlighted code editing |
| **Text Editor** | TipTap | Rich text with tables |
| **Localization** | i18next | Multi-language support |
| **Auth** | oidc-client-ts | OpenID Connect client |

---

## Directory Structure

### Backend (`py-src/data_formulator/`)
```
py-src/data_formulator/
├── __main__.py                    # Entry point for CLI
├── __init__.py                    # Package initialization
├── app.py                         # Flask application setup
├── desktop.py                     # Desktop (PyWebView) integration
├── error_handler.py               # Global error handling
├── errors.py                      # Custom error classes
├── model_registry.py              # LLM provider configuration
├── workspace_factory.py           # Workspace initialization
├── agent_config.py                # Agent configuration
├── data_connector.py              # Data source abstraction
│
├── agents/                        # AI Agent System
│   ├── __init__.py
│   ├── agent_*.py                 # Specialized agents (10 variants)
│   ├── analyst/                   # Modern unified agent (v0.8.0b1+)
│   │   ├── agent.py               # Main analyst agent
│   │   ├── skills/                # Plugin system
│   │   │   ├── skill_*.py         # Individual skills
│   │   │   └── __init__.py
│   │   └── tools/                 # Tool definitions
│   ├── context.py                 # Context management
│   └── client_utils.py            # Shared utilities
│
├── api/                           # API Blueprints (Lazy-loaded)
│   ├── __init__.py
│   ├── tables.py                  # Workspace/table management
│   ├── agents.py                  # Agent execution endpoints
│   ├── sessions.py                # Session persistence
│   ├── credentials.py             # Credential vault
│   ├── connectors.py              # Data source connectors
│   ├── auth/                      # Authentication routes
│   │   ├── oidc.py
│   │   ├── github.py
│   │   └── kusto.py
│   ├── exports.py                 # Data export endpoints
│   ├── marketplace.py             # Plugin marketplace
│   └── ...                        # 12 blueprints total
│
├── data_loader/                   # Data Import System
│   ├── __init__.py
│   ├── data_loader_base.py        # Base loader class
│   ├── loaders/                   # 21 concrete loaders
│   │   ├── local_csv.py           # CSV files
│   │   ├── cloud_s3.py            # AWS S3
│   │   ├── cloud_azure.py         # Azure Blob
│   │   ├── db_postgresql.py       # PostgreSQL
│   │   ├── db_mysql.py            # MySQL
│   │   ├── analytics_bigquery.py   # BigQuery
│   │   └── ... (18 more)
│   └── type_inference.py          # Column type detection
│
├── datalake/                      # Storage Backend
│   ├── __init__.py
│   ├── datalake_factory.py        # Factory pattern
│   ├── local.py                   # Filesystem storage
│   ├── ephemeral.py               # In-memory storage
│   └── azure_blob.py              # Azure Blob Storage
│
├── auth/                          # Authentication
│   ├── auth_base.py               # Base auth class
│   ├── auth_transparent.py        # No-auth mode
│   ├── auth_oidc.py               # OIDC provider
│   ├── auth_github.py             # GitHub OAuth
│   ├── auth_kusto.py              # Kusto delegated auth
│   └── token_store.py             # Server-side session cache
│
├── analyst/                       # Analyst Agent (Modern)
│   ├── agent.py                   # Core agent logic
│   ├── context_builder.py         # Context assembly
│   ├── message_processor.py       # LLM response parsing
│   ├── skills/                    # Skill plugins
│   │   ├── base_skill.py
│   │   ├── skill_visualize.py
│   │   ├── skill_aggregate.py
│   │   └── ...
│   └── tools/                     # Tool definitions
│       ├── tool_inspect.py
│       ├── tool_execute.py
│       └── ...
│
├── dist/                          # Built Frontend (Production)
│   ├── index.html
│   ├── assets/
│   │   ├── *.js (bundled)
│   │   ├── *.css (bundled)
│   │   └── *.woff2 (fonts)
│   └── robots.txt
│
└── config/                        # Configuration
    ├── __init__.py
    ├── settings.py                # Environment-based settings
    └── defaults.py                # Default configurations
```

### Frontend (not in repo, but implied structure)
```
src/
├── index.tsx                      # React entry point
├── App.tsx                        # Root component
├── redux/                         # Redux state management
│   ├── store.ts
│   ├── slices/
│   │   ├── workspaceSlice.ts
│   │   ├── agentSlice.ts
│   │   ├── chartSlice.ts
│   │   └── ...
│   └── hooks.ts
│
├── pages/                         # Page components
│   ├── WorkspacePage.tsx          # Main data exploration UI
│   ├── SessionBrowser.tsx         # View saved sessions
│   ├── DataConnector.tsx          # Connect to data sources
│   ├── ChartBuilder.tsx           # Visual chart editor
│   └── ...
│
├── components/                    # Reusable components
│   ├── DataThreadPanel.tsx        # Thread visualization
│   ├── ChartCanvas.tsx            # Chart rendering
│   ├── CodeEditor.tsx             # Code editing
│   ├── AgentChat.tsx              # Agent conversation UI
│   └── ...
│
├── services/                      # API communication
│   ├── api.ts                     # HTTP client
│   ├── agentService.ts            # Agent API methods
│   ├── connectorService.ts        # Data connector API
│   ├── sessionService.ts          # Session management API
│   └── ...
│
├── hooks/                         # Custom React hooks
│   ├── useAgentStream.ts          # SSE listener
│   ├── useWorkspace.ts            # Workspace state
│   ├── useAuth.ts                 # Authentication
│   └── ...
│
├── utils/                         # Utility functions
│   ├── validators.ts
│   ├── formatters.ts
│   ├── chartHelpers.ts            # Flint/Vega integration
│   └── ...
│
├── i18n/                          # Internationalization
│   ├── en.json                    # English messages
│   ├── zh.json                    # Chinese messages
│   └── config.ts                  # i18next setup
│
├── styles/                        # Global styles
│   ├── theme.ts                   # Material-UI theme
│   └── globals.css
│
└── types/                         # TypeScript types
    ├── api.ts                     # API response types
    ├── workspace.ts               # Workspace types
    ├── agent.ts                   # Agent types
    └── ...
```

---

## Backend Architecture

### 1. Flask Application Structure

**Entry Point**: `py-src/data_formulator/__main__.py`

```python
# Startup sequence:
1. Load environment variables and configuration
2. Initialize Flask application
3. Set up logging and error handlers
4. Register middleware (CORS, error handling)
5. Lazy-load 12 blueprint modules
6. Set up static file serving from dist/
7. Register blueprints with /api prefix
8. Start server (Gunicorn for server, PyWebView for desktop)
```

**Key Configuration** (`app.py`):
- Max upload size: 500 MB
- Session storage: FileSystemCache (ServerSide storage)
- CORS: Configured for development
- Error handling: Unified `AppError` responses
- Logging: Persistent to `~/.data_formulator/logs/`

### 2. API Blueprint System (Lazy-Loaded)

Data Formulator uses Flask Blueprints to organize API routes by domain:

| Blueprint | File | Purpose | Key Endpoints |
|-----------|------|---------|----------------|
| **tables** | `api/tables.py` | Workspace & table CRUD | `GET/POST /api/tables/*` |
| **agents** | `api/agents.py` | LLM agent execution | `POST /api/agents/run` |
| **sessions** | `api/sessions.py` | Session persistence | `GET/POST /api/sessions/*` |
| **credentials** | `api/credentials.py` | Credential vault | `POST /api/credentials/store` |
| **connectors** | `api/connectors.py` | Data source discovery | `GET /api/connectors`, `POST /api/connectors/connect` |
| **auth/oidc** | `api/auth/oidc.py` | OIDC authentication | `GET /api/auth/oidc/login` |
| **auth/github** | `api/auth/github.py` | GitHub OAuth | `GET /api/auth/github/callback` |
| **auth/kusto** | `api/auth/kusto.py` | Kusto delegated auth | `POST /api/auth/kusto/token` |
| **exports** | `api/exports.py` | Data export | `POST /api/exports/csv` |
| **marketplace** | `api/marketplace.py` | Plugin management | `GET /api/marketplace/plugins` |
| **plugins** | `api/plugins.py` | Custom extensions | `POST /api/plugins/install` |
| **system** | `api/system.py` | System info | `GET /api/app-config` |

**Lazy Loading Pattern**:
```python
# In app.py
blueprints = [
    'tables', 'agents', 'sessions', 'credentials',
    'connectors', 'auth.oidc', 'auth.github', ...
]

for blueprint_name in blueprints:
    # Import and register only when first request arrives
    module = import_module(f'data_formulator.api.{blueprint_name}')
    app.register_blueprint(module.bp)
```

**Benefits**: Faster startup times, on-demand module loading

### 3. Data Connector System (21 Loaders)

**Architecture**: Abstract base class with concrete implementations

**Base Class** (`data_loader/data_loader_base.py`):
```python
class DataLoaderBase:
    async def test_connection(self) -> bool
    async def get_catalog_tree(self) -> Dict
    async def import_data(self, table_path: str, **options) -> Dict
    async def discover_columns(self, table_path: str) -> List[ColumnMetadata]
```

**Concrete Loaders**:

1. **Local File System**
   - `LocalCSVLoader`: CSV files
   - `LocalExcelLoader`: .xlsx files
   - `LocalJSONLoader`: JSON/JSONL
   - `LocalParquetLoader`: Parquet files
   - `LocalFolderLoader`: Scan directory

2. **Cloud Storage**
   - `S3Loader`: AWS S3 with IAM/credentials
   - `AzureBlobLoader`: Azure Blob Storage
   - `GCSLoader`: Google Cloud Storage
   - `DatabricksLoader`: Databricks volumes

3. **SQL Databases**
   - `PostgreSQLLoader`: PostgreSQL
   - `MySQLLoader`: MySQL/MariaDB
   - `MSSQLLoader`: SQL Server
   - `MongoDBLoader`: MongoDB
   - `ClickhouseLoader`: Clickhouse
   - `KustoLoader`: Azure Data Explorer

4. **Analytics Platforms**
   - `BigQueryLoader`: Google BigQuery
   - `SupersetLoader`: Apache Superset
   - `AthenaLoader`: AWS Athena
   - `SnowflakeLoader`: Snowflake

5. **Real-Time Data**
   - `YFinanceLoader`: Stock market data
   - `URLLoader`: Fetch URLs with Playwright rendering
   - `APILoader`: Generic REST API

**Data Import Flow**:
```
User selects source → POST /api/connectors/connect
                  ↓ (Test connection)
    Credentials validated or stored in vault
                  ↓
    POST /api/connectors/get-catalog-tree
                  ↓ (Discover available tables)
    User selects table → POST /api/connectors/import-data
                  ↓
    Loader executes query:
      - Infer column types
      - Generate table metadata
      - Convert to Parquet
                  ↓
    Save to ~/.data_formulator/workspaces/{workspace_id}/
                  ↓
    Return table metadata to frontend
```

### 4. Agent System

#### Legacy Agents (10 Variants)
Located in `agents/` directory:

1. **DataLoadAgent** (`agent_data_load.py`)
   - Infers column types and semantic roles
   - Generates display names

2. **DataLoadingAgent** (`agent_data_loading_chat.py`)
   - Conversational data loading with tool use
   - Follows user instructions step-by-step

3. **ChartRestyleAgent** (`agent_chart_restyle.py`)
   - Modifies Vega-Lite specifications
   - Adjusts colors, axes, legends, etc.

4. **CodeExplanationAgent** (`agent_code_explanation.py`)
   - Explains derived field formulas
   - Describes transformations

5. **SortDataAgent** (`agent_sort_data.py`)
   - Orders data by column
   - Handles custom sort orders

6. **SimpleAgent** (`agent_simple.py`)
   - Basic conversation without tool use
   - Fast, low-latency responses

7. **StarterQuestionsAgent** (`agent_starter_questions.py`)
   - Suggests initial analysis questions
   - Context-aware recommendations

8. **WorkflowDistillAgent** (`agent_workflow_distill.py`)
   - Summarizes analysis workflows
   - Generates reproducible steps

9. **LanguageAgent** (`agent_language.py`)
   - Handles language detection and switching
   - Manages i18n context

10. **DiagnosticsAgent** (`agent_diagnostics.py`)
    - System health checks
    - Performance analysis

#### Modern Analyst Agent (v0.8.0b1+)
Located in `analyst/` directory:

**Architecture**: Unified agent with plugin skills and tools

**Skills** (Plugin System):
```python
class BaseSkill:
    async def execute(self, action: Dict, context: Context) -> Result
    
# Example skills:
- VisualizeSkill: Create/modify charts
- AggregateSkill: Group and summarize data
- TransformSkill: Clean and prepare data
- FilterSkill: Subset data by conditions
- DelegateSkill: Route to specialized agents
```

**Tools** (Available to LLM):
```python
# Inspection tools (parallel execution)
- inspect_source_data(table_name: str)
  Returns: {columns, sample_rows, statistics}

- execute_python_script(script: str, inputs: Dict)
  Returns: {output, visualization_data}

- load_skill(skill_name: str)
  Returns: {skill_metadata, available_actions}

# Action tools (serial execution)
- visualize(action: Dict)
  Renders chart with Vega-Lite

- delegate(agent_name: str, input: Dict)
  Routes to specialized agent

- skill-specific actions
  E.g., aggregate.group_by(), filter.where_clause()
```

**Streaming Flow**:
```
POST /api/agents/run
  ├─ Load workspace context
  ├─ Format system prompt with schema
  ├─ Send to LLM with streaming
  │
  ├─ event: init {agent_id, model}
  ├─ event: tool_call {tool, args}  (parallel tools)
  ├─ event: chunk "reasoning text"  (streamed)
  ├─ event: action {skill, params}  (execute serially)
  ├─ event: completion {summary}
  └─ event: error (if failed)
```

**LLM Configuration**:
```python
{
    "model": "gpt-4-turbo",
    "temperature": 0.1,
    "max_tokens": 4000,
    "reasoning_effort": "low" | "medium" | "high"
        # Trade-off: latency vs. quality
        # Recommended:
        #   - Code generation: "low"
        #   - Multi-step logic: "medium"
        #   - Complex reasoning: "high"
}
```

### 5. Workspace & Storage Architecture

**Storage Hierarchy**:
```
~/.data_formulator/
├── workspaces/
│   └── {workspace_id}/
│       ├── workspace.json           # Metadata
│       │   {
│       │     "id": "uuid",
│       │     "name": "Sales Analysis",
│       │     "created_at": "2026-01-15T10:00:00Z",
│       │     "threads": [{...}],
│       │     "archived_threads": [{...}]
│       │   }
│       ├── tables/
│       │   ├── sales.parquet        # Data (Parquet format)
│       │   ├── regions.parquet
│       │   └── metadata/
│       │       ├── sales.json       # Column metadata
│       │       └── regions.json
│       └── artifacts/
│           ├── chart_1.json         # Saved chart specs
│           ├── script_1.py          # Generated code
│           └── export_1.csv         # Exported data
│
├── sessions/
│   └── user@example.com/
│       └── oidc_token_cache.json    # SSO token (server-side)
│
└── logs/
    └── data_formulator.log          # Application log
```

**Backend Options**:

1. **Local** (Default)
   - Storage: `~/.data_formulator/`
   - Use case: Desktop, single-user
   - No setup required

2. **Ephemeral** (In-Memory)
   - Storage: RAM only
   - Use case: Stateless containers, demos
   - Data lost on restart

3. **Azure Blob Storage**
   - Storage: Azure Blob Container
   - Use case: Multi-user cloud deployment
   - Requires: Connection string or Entra ID credentials
   - Automatic sync with TTL

**Workspace Context**:
```python
class Workspace:
    id: str                           # UUID
    name: str
    created_at: datetime
    tables: Dict[str, TableMetadata]
    threads: List[DataThread]         # Analysis paths
    archived_threads: List[DataThread]
```

### 6. Authentication & Authorization

**Providers**:

1. **Transparent** (Development)
   - No auth required
   - Single user: "default"

2. **OIDC** (Production)
   - Provider: Any OIDC-compliant server
   - Flow: PKCE authorization code
   - Token storage: Server-side session cache
   - Config: `OIDC_CLIENT_ID`, `OIDC_DISCOVERY_URL`

3. **GitHub OAuth**
   - Provider: github.com
   - Flow: OAuth 2.0 redirect
   - Scopes: `user:email, read:user`
   - Config: `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`

4. **Kusto Delegated** (Enterprise)
   - Provider: Azure Kusto (ADX)
   - Flow: User's Kusto credentials
   - Automatic token refresh

**Token Storage**:
```python
# Server-side cache (avoids 4KB cookie limit)
FileSystemCache: ~/.data_formulator/sessions/{user_id}/
Azure Blob: {container}/sessions/{user_id}/

# Contains:
{
    "access_token": "...",
    "refresh_token": "...",
    "expires_at": 1234567890,
    "scope": "profile email",
    "id_token": "..."  # OIDC only
}
```

**Authorization Checks**:
```python
@app.before_request
def check_auth():
    if AUTH_PROVIDER != 'transparent':
        user_id = session.get('user_id')
        if not user_id:
            return redirect('/api/auth/{provider}/login')
    request.user_id = session.get('user_id', 'default')
    request.workspace_id = request.headers.get('X-Workspace-Id')
```

### 7. Error Handling

**Unified Error Response Format**:
```python
{
    "status": "error",
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "detail": "Technical details",
    "timestamp": "2026-01-15T10:00:00Z"
}
```

**Error Categories**:

| Code | Category | Example | HTTP Status |
|------|----------|---------|-------------|
| `AUTH_*` | Authentication | `AUTH_REQUIRED`, `AUTH_INVALID_TOKEN` | 401 |
| `PERM_*` | Permission | `PERM_WORKSPACE_ACCESS_DENIED` | 403 |
| `VAL_*` | Validation | `VAL_MISSING_FIELD`, `VAL_INVALID_TYPE` | 400 |
| `LLM_*` | LLM errors | `LLM_RATE_LIMIT`, `LLM_CONTEXT_TOO_LONG` | 429/400 |
| `DATA_*` | Data errors | `DATA_TABLE_NOT_FOUND`, `DATA_TYPE_MISMATCH` | 404/400 |
| `EXEC_*` | Execution | `EXEC_SCRIPT_FAILED`, `EXEC_TIMEOUT` | 500 |
| `CAT_*` | Catalog errors | `CAT_UNKNOWN_PROVIDER`, `CAT_CONNECT_FAILED` | 400/500 |
| `SYS_*` | System errors | `SYS_STORAGE_ERROR`, `SYS_OUT_OF_MEMORY` | 500 |

**Error Handling Middleware**:
```python
@app.errorhandler(AppError)
def handle_app_error(error):
    return jsonify({
        "status": "error",
        "code": error.code,
        "message": error.message,
        "detail": error.detail
    }), error.status_code
```

---

## Frontend Architecture

### 1. React Application Setup

**Entry Point**: `dist/index.html` (bundled by Vite)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Formulator</title>
</head>
<body>
    <div id="root"></div>
    <script type="module" src="/src/index.tsx"></script>
</body>
</html>
```

**React Entry** (`src/index.tsx`):
```typescript
import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import { I18nextProvider } from 'react-i18next';
import App from './App';
import store from './redux/store';
import i18n from './i18n/config';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Provider store={store}>
      <I18nextProvider i18n={i18n}>
        <App />
      </I18nextProvider>
    </Provider>
  </React.StrictMode>
);
```

### 2. Component Hierarchy

**Root Component** (`src/App.tsx`):
```
<App>
  <AuthProvider>
    <Router>
      <MainLayout>
        <Header />
        <Sidebar />
        <Routes>
          <Route path="/" element={<WorkspacePage />} />
          <Route path="/sessions" element={<SessionBrowser />} />
          <Route path="/connector" element={<DataConnector />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </MainLayout>
    </Router>
  </AuthProvider>
</App>
```

### 3. Redux State Management

**Store Structure**:
```typescript
{
  // Authentication
  auth: {
    user: { id, email, name },
    isAuthenticated: boolean,
    token: string,
    provider: 'oidc' | 'github' | 'transparent'
  },

  // Workspace
  workspace: {
    id: string,
    name: string,
    tables: { [name]: TableMetadata },
    threads: DataThread[],
    selectedThread: string,
    isLoading: boolean
  },

  // Agent interaction
  agent: {
    isStreaming: boolean,
    messages: Message[],
    currentAgent: string,
    reasoning: string,
    error: AppError | null
  },

  // Chart/visualization
  chart: {
    selectedChart: ChartSpec,
    editMode: boolean,
    vegaSpec: any,
    data: any[]
  },

  // Data connectors
  connectors: {
    available: ConnectorInfo[],
    connecting: boolean,
    connectionStatus: 'idle' | 'testing' | 'connected' | 'failed'
  },

  // UI state
  ui: {
    sidebarOpen: boolean,
    theme: 'light' | 'dark',
    locale: 'en' | 'zh'
  }
}
```

**Slices** (Redux Toolkit):
- `authSlice.ts`: Auth state and login/logout actions
- `workspaceSlice.ts`: Workspace and thread management
- `agentSlice.ts`: Agent messages and streaming state
- `chartSlice.ts`: Chart specifications and editing
- `connectorSlice.ts`: Data source connection state
- `uiSlice.ts`: UI preferences and layout

### 4. Key Components

#### WorkspacePage (Main UI)
```typescript
<WorkspacePage>
  <ThreadPanel>           {/* Data thread history */}
    <ThreadCard />
    <ThreadCard />
  </ThreadPanel>
  
  <MainCanvas>
    <ChartCanvas />        {/* Renders Vega-Lite chart */}
    <DataGridView />       {/* Table view */}
  </MainCanvas>
  
  <RightSidebar>
    <AgentChat />          {/* Conversation interface */}
    <ChartEditor />        {/* Chart customization */}
    <TableMetadata />      {/* Column info */}
  </RightSidebar>
</WorkspacePage>
```

#### AgentChat Component
```typescript
<AgentChat>
  <MessageList>
    <Message role="user" content="..." />
    <Message role="assistant" content="..." streaming={true} />
  </MessageList>
  
  <ReasoningDisplay>
    {/* Shows thinking process */}
  </ReasoningDisplay>
  
  <InputBox>
    <TextInput placeholder="Ask a question..." />
    <SubmitButton />
  </InputBox>
</AgentChat>
```

#### ChartCanvas Component
```typescript
<ChartCanvas>
  <VegaLiteRenderer
    spec={vegaSpec}
    data={tableData}
    onInteraction={handleChartClick}
  />
  <ChartLegend />
  <TooltipRenderer />
</ChartCanvas>
```

### 5. API Communication Service

**HTTP Client** (`src/services/api.ts`):
```typescript
class ApiClient {
  private baseUrl = '/api';
  private headers = {
    'Content-Type': 'application/json',
    'X-Workspace-Id': workspaceId
  };

  async request<T>(method: string, endpoint: string, data?: any): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method,
      headers: this.headers,
      body: data ? JSON.stringify(data) : undefined
    });
    
    if (!response.ok) {
      throw new AppError(await response.json());
    }
    
    return response.json();
  }

  get<T>(endpoint: string) { return this.request<T>('GET', endpoint); }
  post<T>(endpoint: string, data: any) { return this.request<T>('POST', endpoint, data); }
  put<T>(endpoint: string, data: any) { return this.request<T>('PUT', endpoint, data); }
  delete<T>(endpoint: string) { return this.request<T>('DELETE', endpoint); }
}
```

**Agent Service** (`src/services/agentService.ts`):
```typescript
class AgentService {
  async *streamAgentResponse(
    messages: Message[],
    context: Context,
    config: AgentConfig
  ): AsyncGenerator<StreamEvent> {
    const response = await fetch('/api/agents/run', {
      method: 'POST',
      headers: { 'X-Workspace-Id': context.workspaceId },
      body: JSON.stringify({ messages, context, config })
    });

    const reader = response.body!.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      for (const line of chunk.split('\n')) {
        if (line.startsWith('event: ')) {
          const event = JSON.parse(line.slice(7));
          yield event;
        }
      }
    }
  }
}
```

**Connector Service** (`src/services/connectorService.ts`):
```typescript
class ConnectorService {
  async listConnectors(): Promise<ConnectorInfo[]> {
    return api.get('/connectors');
  }

  async testConnection(type: string, credentials: any): Promise<boolean> {
    return api.post(`/connectors/${type}/test`, { credentials });
  }

  async getCatalogTree(type: string, credentials: any): Promise<CatalogNode[]> {
    return api.post(`/connectors/${type}/catalog`, { credentials });
  }

  async importData(type: string, path: string, options: any) {
    return api.post(`/connectors/${type}/import`, { path, options });
  }
}
```

### 6. Custom Hooks

**useAgentStream** - Server-Sent Events listener:
```typescript
function useAgentStream() {
  const dispatch = useAppDispatch();

  const streamAgent = useCallback(async (message: string) => {
    dispatch(agentSlice.actions.setStreaming(true));
    
    for await (const event of agentService.streamAgentResponse(...)) {
      switch (event.type) {
        case 'init':
          dispatch(agentSlice.actions.initAgent(event.data));
          break;
        case 'chunk':
          dispatch(agentSlice.actions.addReasoning(event.data));
          break;
        case 'action':
          dispatch(agentSlice.actions.executeAction(event.data));
          break;
        case 'completion':
          dispatch(agentSlice.actions.completeAgent(event.data));
          break;
      }
    }
    
    dispatch(agentSlice.actions.setStreaming(false));
  }, [dispatch]);

  return { streamAgent };
}
```

**useWorkspace** - Workspace state:
```typescript
function useWorkspace() {
  const workspace = useAppSelector(state => state.workspace);
  const dispatch = useAppDispatch();

  const loadWorkspace = useCallback(async (workspaceId: string) => {
    const data = await workspaceService.getWorkspace(workspaceId);
    dispatch(workspaceSlice.actions.setWorkspace(data));
  }, [dispatch]);

  return { workspace, loadWorkspace, ...workspaceSlice.actions };
}
```

---

## Communication Protocols

### 1. REST API Requests

**Standard Request Format**:
```
POST /api/agents/run
X-Workspace-Id: 550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json

{
  "messages": [
    {
      "role": "user",
      "content": "Show me sales by region"
    }
  ],
  "context": {
    "workspace_id": "550e8400-...",
    "focused_thread": {
      "table_name": "sales",
      "chart_type": "bar",
      "display_instruction": {...}
    },
    "other_threads": []
  },
  "config": {
    "model": "gpt-4-turbo",
    "reasoning_effort": "low"
  }
}
```

**Standard Response Format**:
```json
{
  "status": "success",
  "data": {...},
  "timestamp": "2026-01-15T10:00:00Z"
}
```

**Error Response Format**:
```json
{
  "status": "error",
  "code": "DATA_TABLE_NOT_FOUND",
  "message": "Table 'sales' not found in workspace",
  "detail": "Available tables: customers, orders, products",
  "timestamp": "2026-01-15T10:00:00Z"
}
```

### 2. Server-Sent Events (SSE) - Agent Streaming

**SSE Connection**:
```
POST /api/agents/run
Accept: text/event-stream

Response:
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

data: {"event": "init", "agent_id": "analyst_001", "model": "gpt-4-turbo"}

data: {"event": "tool_call", "tool": "inspect_source_data", "args": {"table_name": "sales"}}

data: {"event": "chunk", "delta": "Analyzing sales data by region"}

data: {"event": "action", "skill": "visualize", "params": {"chart_type": "bar", "x": "region", "y": "total_sales"}}

data: {"event": "completion", "summary": "Created bar chart showing sales by region"}

data: [DONE]
```

**Event Types**:

| Event | Payload | Description |
|-------|---------|-------------|
| `init` | `{agent_id, model}` | Agent initialized |
| `tool_call` | `{tool, args}` | Tool invoked (parallel) |
| `chunk` | `{delta}` | Reasoning text streamed |
| `action` | `{skill, params}` | Action executed (serial) |
| `completion` | `{summary}` | Agent completed |
| `error` | `{code, message}` | Error occurred |

### 3. WebSocket (Optional - for Real-Time Collaboration)

**Not currently implemented**, but future enhancement for:
- Multi-user workspace synchronization
- Collaborative editing
- Live cursor tracking

---

## Data Flow Examples

### Example 1: "Show me sales by region"

**Step 1: Frontend → Backend**
```
POST /api/agents/run
X-Workspace-Id: workspace123
{
  "messages": [{"role": "user", "content": "Show me sales by region"}],
  "context": {
    "workspace_id": "workspace123",
    "focused_thread": {
      "table_name": "sales",
      "columns": ["date", "region", "product", "amount"]
    }
  }
}
```

**Step 2: Backend Processing**
```python
# 1. Load workspace
workspace = datalake.get_workspace("workspace123")

# 2. Load tables into DuckDB
duckdb.query("""
    CREATE TABLE sales AS SELECT * FROM 'sales.parquet'
""")

# 3. Build system prompt with schema
schema_info = """
Available tables:
- sales: date, region, product, amount (100,000 rows)
"""

# 4. Call LLM with streaming
response = await llm.stream(
    model="gpt-4-turbo",
    messages=[
        {"role": "system", "content": f"You are a data analyst. {schema_info}"},
        {"role": "user", "content": "Show me sales by region"}
    ],
    tools=[inspect_source_data, execute_python_script, visualize]
)

# 5. LLM calls tools in parallel
tool_calls = [
    {"tool": "inspect_source_data", "args": {"table": "sales"}},
    {"tool": "execute_python_script", "args": {"script": "SELECT region, SUM(amount) FROM sales GROUP BY region"}}
]

# 6. Execute tools
inspect_result = inspect_source_data("sales")
exec_result = execute_python_script("SELECT region, SUM(amount) FROM sales GROUP BY region")

# 7. LLM decides action
action = {
    "skill": "visualize",
    "params": {
        "chart_type": "bar",
        "x": "region",
        "y": "SUM(amount)",
        "title": "Sales by Region",
        "vegaSpec": {...}
    }
}

# 8. Stream responses back to frontend
yield {"event": "init", "agent_id": "analyst_001"}
yield {"event": "tool_call", "tool": "inspect_source_data", ...}
yield {"event": "chunk", "delta": "Analyzing sales..."}
yield {"event": "action", "skill": "visualize", ...}
yield {"event": "completion", "summary": "Chart created"}
```

**Step 3: Frontend Updates**
```
Receives SSE event: init
→ Show "Agent thinking..." indicator

Receives SSE event: chunk
→ Stream reasoning text in chat

Receives SSE event: action (visualize)
→ Extract Vega-Lite spec
→ Fetch data: GET /api/tables/sales?region=*&amount=*
→ Render chart with Flint
→ Update Redux state with new chart

Receives SSE event: completion
→ Hide spinner
→ Add response to message history
→ Enable next input
```

---

### Example 2: Loading Data from PostgreSQL

**Step 1: User Selects Data Source**
```
Frontend: POST /api/connectors/postgres/test
Body: {
  "host": "db.example.com",
  "port": 5432,
  "database": "analytics",
  "username": "user",
  "password": "***"
}

Backend: PostgreSQLLoader.test_connection()
→ Attempts connection
→ Returns success/failure
→ Optionally stores credentials in vault
```

**Step 2: Browse Catalog**
```
Frontend: POST /api/connectors/postgres/catalog
Body: {
  "host": "db.example.com",
  "credentials": {...}
}

Backend: PostgreSQLLoader.get_catalog_tree()
→ SELECT table_name FROM information_schema.tables
→ For each table: SELECT column_name, data_type FROM information_schema.columns
→ Returns:
{
  "databases": [
    {
      "name": "analytics",
      "tables": [
        {
          "name": "orders",
          "columns": ["id", "customer_id", "amount", "date"],
          "row_count": 50000
        },
        {
          "name": "customers",
          "columns": ["id", "name", "email", "country"],
          "row_count": 10000
        }
      ]
    }
  ]
}

Frontend: Display tree UI
```

**Step 3: Import Table**
```
Frontend: POST /api/connectors/postgres/import-data
Body: {
  "table": "orders",
  "column_selection": ["id", "customer_id", "amount", "date"],
  "filters": ["amount > 100"],
  "limit": 10000
}

Backend:
1. Execute filtered query
2. Infer column types (id→int, amount→float, date→datetime)
3. Generate ColumnMetadata with semantic types
4. Convert to Parquet
5. Save to ~/.data_formulator/workspaces/workspace123/tables/orders.parquet
6. Save metadata to .../tables/metadata/orders.json

Returns:
{
  "status": "success",
  "table": {
    "name": "orders",
    "row_count": 9500,
    "columns": [
      {"name": "id", "type": "number", "semantic_type": "ID"},
      {"name": "customer_id", "type": "number", "semantic_type": "ID"},
      {"name": "amount", "type": "number", "semantic_type": "Measure", "unit": "USD"},
      {"name": "date", "type": "date", "semantic_type": "Date"}
    ]
  }
}

Frontend:
→ Update Redux workspace.tables["orders"]
→ Show success notification
→ Enable chat interaction
```

---

### Example 3: Data Thread Creation

**What is a Data Thread?**
- A branching alternative analysis path
- Maintains independent chart/view
- Shares underlying data
- Allows exploration of multiple hypotheses

**Creation Flow**:
```
Frontend: Click "New Thread" button
→ POST /api/tables/threads
Body: {
  "workspace_id": "workspace123",
  "source_thread_id": "thread_original",
  "name": "Alternative Sales View"
}

Backend:
1. Load source thread
2. Copy chart spec and metadata
3. Create new thread entry in workspace.json
4. Return new thread_id

Frontend:
→ Switch active thread to new thread
→ Load new empty canvas
→ User can now create independent visualization
```

---

## Key Concepts

### 1. Workspace
- Container for a single analysis session
- Contains multiple data threads
- Stores tables as Parquet files + metadata
- Maps 1:1 with a user session

### 2. Data Thread
- A branching analysis path
- Contains: Chart spec, display instruction, focused table
- Immutable history (linear time)
- Can be archived

### 3. Table Metadata
- Enriched column information
- Semantic types (ID, Measure, Date, Region, etc.)
- Bounds, units, sort orders
- Enables intelligent chart recommendations

### 4. Display Instruction
- Vega-Lite specification
- Defines visual encoding (marks, channels)
- Attached to thread (not persisted separately)
- Regenerated when thread is reloaded

### 5. Semantic Types
- **ID**: Unique identifier (no aggregation)
- **Measure**: Numeric quantity (sum, avg, count)
- **Date**: Temporal value (grouping, filtering)
- **Region**: Geographic or categorical (grouping)
- **Ordinal**: Ranked categories (month, day, grade)

### 6. Flint Semantic Chart Language
- Layer: Base chart mark (bar, line, point, etc.)
- Encoding: Data-to-visual mapping (x, y, color, size)
- Transformation: Data processing (aggregation, sorting)
- Constraint: Rules (2-3 encodings max)

---

## Development Workflow

### 1. Backend Development

**Setup**:
```bash
cd data-formulator
source .venv/bin/activate
uv pip install -e .
```

**Running the Server**:
```bash
# Development server with hot reload
uv run data_formulator

# Or directly with Flask
export FLASK_APP=py-src/data_formulator/app.py
export FLASK_ENV=development
uv run flask run --port 5567
```

**Testing**:
```bash
uv run pytest                              # Run all tests
uv run pytest tests/test_agents.py        # Specific module
uv run pytest -k test_agent_stream        # Specific test
```

**Adding a New API Endpoint**:
```python
# 1. Create route in api/tables.py
from flask import Blueprint, request, jsonify
bp = Blueprint('tables', __name__, url_prefix='/api/tables')

@bp.route('/search', methods=['POST'])
def search_tables():
    workspace_id = request.headers.get('X-Workspace-Id')
    query = request.json.get('q')
    
    # Implementation
    results = [...]
    
    return jsonify({'status': 'success', 'results': results})
```

**Adding a New Data Loader**:
```python
# 1. Create class in data_loader/loaders/
from data_loader.data_loader_base import DataLoaderBase

class NewSourceLoader(DataLoaderBase):
    async def test_connection(self) -> bool:
        # Verify credentials work
        pass
    
    async def get_catalog_tree(self) -> Dict:
        # Return available tables
        pass
    
    async def import_data(self, table_path: str, **options) -> Dict:
        # Load into Parquet
        pass

# 2. Register in data_loader/__init__.py
LOADERS = {
    'newsource': NewSourceLoader,
    ...
}
```

### 2. Frontend Development

**Setup**:
```bash
cd data-formulator
npm install
npm run dev                                # Starts Vite dev server on :5173
```

**Development Flow**:
1. `npm run dev` - Vite dev server watches `src/` and hot-reloads
2. Backend `uv run data_formulator` - Flask server on :5567
3. Vite proxies API requests to Flask (configured in `vite.config.ts`)

**Building**:
```bash
npm run build                              # Bundles to dist/
                                          # Then copied to py-src/data_formulator/dist/
```

**Testing**:
```bash
npm run test                               # Vitest
npm run test:ui                            # Vitest UI
```

**Adding a New Component**:
```typescript
// src/components/MyComponent.tsx
import { useAppDispatch, useAppSelector } from '../redux/hooks';
import { mySlice } from '../redux/slices/mySlice';

export function MyComponent() {
  const state = useAppSelector(state => state.my);
  const dispatch = useAppDispatch();
  
  return <div>{state.value}</div>;
}

// src/redux/slices/mySlice.ts
import { createSlice } from '@reduxjs/toolkit';

export const mySlice = createSlice({
  name: 'my',
  initialState: { value: '' },
  reducers: {
    setValue: (state, action) => {
      state.value = action.payload;
    }
  }
});

export default mySlice.reducer;
```

---

## Deployment & Configuration

### 1. Environment Variables

**LLM Configuration**:
```bash
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODELS=gpt-4-turbo,gpt-4

# Azure OpenAI
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://....openai.azure.com/
AZURE_OPENAI_MODELS=gpt-4-turbo

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODELS=claude-3-opus-20240229

# Google Gemini
GEMINI_API_KEY=...
GEMINI_MODELS=gemini-pro

# Ollama (Local)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODELS=mistral,neural-chat
```

**Workspace & Storage**:
```bash
# Storage backend
WORKSPACE_BACKEND=local|ephemeral|azure_blob
WORKSPACE_PATH=/data/formulator        # For local backend

# Azure Blob Storage
AZURE_BLOB_CONNECTION_STRING=DefaultEndpointsProtocol=https;...
AZURE_BLOB_CONTAINER_NAME=data-formulator
```

**Authentication**:
```bash
# OIDC
AUTH_PROVIDER=oidc
OIDC_CLIENT_ID=...
OIDC_CLIENT_SECRET=...
OIDC_DISCOVERY_URL=https://auth.example.com/.well-known/openid-configuration
OIDC_REDIRECT_URI=http://localhost:5567/api/auth/oidc/callback

# GitHub OAuth
AUTH_PROVIDER=github
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...
GITHUB_REDIRECT_URI=http://localhost:5567/api/auth/github/callback
```

**Server Configuration**:
```bash
# Server
FLASK_ENV=development|production
FLASK_DEBUG=1
LOG_LEVEL=INFO|DEBUG
MAX_UPLOAD_SIZE=500000000              # 500 MB

# Limits
MAX_DISPLAY_ROWS=10000
MAX_QUERY_TIMEOUT=300                  # seconds
SANDBOX=local|docker                   # Code execution isolation
```

### 2. Deployment Modes

**Desktop (Recommended for Local Use)**:
```bash
# Uses PyWebView to embed Flask in desktop window
uv run data_formulator --mode desktop

# Packages with PyInstaller for distribution
python packaging/data_formulator_desktop.py
```

**Server (Multi-User Cloud)**:
```bash
# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5567 data_formulator.app:app

# Or Docker
docker build -t data-formulator .
docker run -p 5567:5567 \
  -e OPENAI_API_KEY=... \
  -e AUTH_PROVIDER=oidc \
  data-formulator
```

**Docker Compose** (Full Stack):
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5567:5567"
    environment:
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      AUTH_PROVIDER: oidc
      WORKSPACE_BACKEND: azure_blob
    volumes:
      - /data/formulator:/root/.data_formulator
```

### 3. Performance Tuning

**For Large Datasets**:
```bash
# Increase DuckDB memory
DUCKDB_MEMORY_LIMIT=16GB

# Increase Flask upload timeout
FLASK_SEND_FILE_MAX_AGE_DEFAULT=3600

# Use Parquet compression
PARQUET_COMPRESSION=snappy              # or gzip
```

**For Concurrent Users**:
```bash
# Gunicorn workers
gunicorn -w 8 -k gevent ...

# Connection pooling
DATABASE_POOL_SIZE=20
DATABASE_POOL_RECYCLE=3600
```

---

## Quick Reference: Common Tasks

### Backend: Add a New Agent Skill

```python
# agents/analyst/skills/skill_export.py
from .base_skill import BaseSkill

class ExportSkill(BaseSkill):
    name = "export"
    description = "Export data to CSV or Excel"
    
    async def execute(self, action: Dict, context: Context) -> Dict:
        format = action.get('format', 'csv')  # csv, xlsx
        table_name = action.get('table')
        
        # Implementation
        return {'status': 'success', 'file_path': '/downloads/export.csv'}
```

### Frontend: Add a New Redux Slice

```typescript
// redux/slices/exportSlice.ts
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

export const exportData = createAsyncThunk(
  'export/exportData',
  async (payload: ExportPayload) => {
    const response = await api.post('/api/export', payload);
    return response;
  }
);

export const exportSlice = createSlice({
  name: 'export',
  initialState: { status: 'idle', url: null },
  extraReducers: (builder) => {
    builder
      .addCase(exportData.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(exportData.fulfilled, (state, action) => {
        state.status = 'success';
        state.url = action.payload.url;
      });
  }
});
```

### Debugging: Enable Verbose Logging

```bash
export LOG_LEVEL=DEBUG
export FLASK_DEBUG=1
uv run data_formulator
```

---

## Summary

The Data Formulator architecture follows a **layered, modular design**:

- **Backend**: Flask with lazy-loaded blueprints, 21 data connectors, pluggable agent system
- **Frontend**: React + Redux for state, Material-UI for components, Vite for bundling
- **Communication**: REST + Server-Sent Events (SSE) for real-time streaming
- **Storage**: Parquet tables + JSON metadata in local/cloud backends
- **LLM Integration**: Multi-provider support with streaming responses
- **Extensibility**: Plugin architecture for skills, loaders, and connectors

This guide should provide a complete map for navigating the codebase, from API endpoints through React components, with clear examples of data flow and extension points.
