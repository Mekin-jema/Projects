# Data Formulator Backend Architecture Guide

**Project**: AI-powered data visualization & exploration platform  
**Version**: 0.8.0b1  
**Backend Language**: Python 3.11+  
**Framework**: Flask with lazy-loaded blueprints  
**Last Updated**: 2026

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Entry Points](#entry-points)
3. [Core Application Setup](#core-application-setup)
4. [Directory Structure & Components](#directory-structure--components)
5. [Key Modules](#key-modules)
6. [Agent Architecture](#agent-architecture)
7. [Data Loading System](#data-loading-system)
8. [Authentication & Authorization](#authentication--authorization)
9. [Error Handling](#error-handling)
10. [Component Connections](#component-connections)

---

## Quick Start

### Running the Backend

```bash
# Activate virtual environment
source .venv/bin/activate  # or use uv run

# Start Flask development server (runs on :5567)
uv run data_formulator

# Alternatively, start with specific options
uv run data_formulator --workspace-backend local --sandbox local --host 127.0.0.1
```

### Key Environment Variables

```bash
# LLM Configuration
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=claude-...
LLM_MODEL=gpt-4o                    # Default model

# Storage
WORKSPACE_BACKEND=local             # local | ephemeral | azure_blob
DATA_FORMULATOR_HOME=~/.data_formulator

# Authentication
AUTH_PROVIDER=transparent           # transparent | oidc | github | kusto

# Server
HOST=127.0.0.1
SANDBOX=local                       # local | docker
LOG_LEVEL=INFO
MAX_DISPLAY_ROWS=10000
```

---

## Entry Points

### 1. **CLI Entry Point** — `py-src/data_formulator/__main__.py`
```python
from .app import run_app
if __name__ == "__main__":
    run_app()
```
**Role**: Package-level entry point for `uv run data_formulator` or `python -m data_formulator`

### 2. **Application Factory** — `py-src/data_formulator/app.py`
**Key Functions**:
- `run_app()` — Parses CLI args, configures logging, initializes Flask, registers blueprints
- `configure_logging()` — Sets up console & file logging with sanitization
- `_register_blueprints()` — Heavy imports happen here (lazy-loaded for startup speed)

**Config Applied**:
- Flask `app.secret_key` (OIDC sessions)
- `app.config['CLI_ARGS']` — All CLI flags stored for route handlers
- File handler logging to `~/.data_formulator/logs/data_formulator.log`
- Session backend (filesystem via `flask-session` if available)

### 3. **Desktop Entry Point** — `py-src/data_formulator/desktop.py`
**Role**: PyWebView integration for standalone desktop app  
**Handles**: Window lifecycle, local server management

---

## Core Application Setup

### Flask Application Setup Flow

```
app.py:
  1. Load .env files early (FLASK_SECRET_KEY needed)
  2. Create Flask(name, static_url_path='', static_folder='dist/')
  3. Configure secret key, session backend, JSON encoder
  4. [Deferred] Import + register 6+ blueprints (_register_blueprints)
  5. Configure error handlers + request-id middleware
  6. Initialize auth providers (OIDC, GitHub OAuth, etc.)
  7. Serve React bundle from dist/
```

### Lazy Blueprint Loading

Blueprints are imported only when `_register_blueprints()` is called to:
- Speed up startup (no heavy ML/DB imports until needed)
- Support different deployment modes (local vs. hosted)

**Blueprints Registered** (as of v0.8.0b1):
| Blueprint | Module Path | Role | Prefix |
|-----------|-------------|------|--------|
| `tables_bp` | `routes.tables` | Workspace/table CRUD + metadata | `/api/tables` |
| `agent_bp` | `routes.agents` | Agent execution, streaming responses | `/api/agents` |
| `session_bp` | `routes.sessions` | Session persistence, restore | `/api/sessions` |
| `demo_stream_bp` | `routes.demo_stream` | Demo data streaming (rate-limited) | `/api/demo` |
| `logs_bp` | `routes.logs` | Server logs inspection (local-mode only) | `/api/logs` |
| `model_endpoints_bp` | `routes.model_endpoints` | LLM provider status | `/api/models` |
| `github_bp` | `auth.gateways.github_gateway` | GitHub OAuth callback | `/auth/github` |
| `auth_tokens_bp` | `auth.gateways.oidc_gateway` | OIDC token refresh, logout | `/auth/tokens` |

---

## Directory Structure & Components

### Root Configuration Files

```
py-src/data_formulator/
├── __init__.py              # Package init; exports run_app()
├── __main__.py              # CLI entry point
├── app.py                   # Flask factory & blueprint registration
├── desktop.py               # PyWebView integration
│
├── agent_config.py          # LLM reasoning effort per agent (minimal/low/medium/high)
├── model_registry.py        # LLM provider configuration loader
├── workspace_factory.py     # Workspace backend factory (local/ephemeral/azure_blob)
├── data_connector.py        # Generic data source connector lifecycle
├── error_handler.py         # Global error handlers + unified error envelope
├── errors.py                # ErrorCode enum + AppError exception class
│
├── example_datasets_config.py  # Sample datasets for demos
├── _startup_spinner.py      # CLI spinner for startup progress
```

### 1. Core Configuration — `agent_config.py`

**Purpose**: Single source of truth for LLM reasoning effort per agent

**Key Components**:
- `ReasoningEffort` — Type: `"none" | "minimal" | "low" | "medium" | "high"`
- `AGENT_REASONING_EFFORT` — Dict mapping agent IDs to effort levels
- `get_reasoning_effort(agent_id)` — Resolve from env var → config → default
- `reasoning_effort_for(model, effort)` — Adapt effort tier based on model capabilities

**Usage**:
```python
from data_formulator.agent_config import reasoning_effort_for
effort = reasoning_effort_for("gpt-4o", "low")  # Returns "low" on GPT-4o, "minimal" on GPT-5
```

**Agent Reasoning Tiers**:
- **Heavy** (code-gen, multi-step): `"low"` — data_transform, analyst, data_loading_chat
- **Light** (extractors, classifiers): `"minimal"` — chart_insight, code_explanation, sort_data

---

### 2. Model Registry — `model_registry.py`

**Purpose**: Runtime discovery & configuration of all available LLM providers

**Key Components**:
- `ModelRegistry` class — Loads provider configs from environment
- `_discover_providers()` — Scans env vars ending with `_ENABLED=true`
- `_reload()` — Populates provider → model mapping

**Supported Providers**:
| Provider | Built-in | Auth | Config Vars |
|----------|----------|------|-------------|
| OpenAI | ✅ | API Key | `OPENAI_API_KEY`, `OPENAI_MODELS` |
| Azure OpenAI | ✅ | API Key | `AZURE_API_KEY`, `AZURE_API_BASE` |
| Anthropic | ✅ | API Key | `ANTHROPIC_API_KEY`, `ANTHROPIC_MODELS` |
| Google Gemini | ✅ | API Key | `GEMINI_API_KEY`, `GEMINI_MODELS` |
| Ollama | ✅ | None | `OLLAMA_API_BASE`, `OLLAMA_MODELS` |
| Custom (any) | ✅ | Via env | `{NAME}_ENABLED`, `{NAME}_API_KEY`, `{NAME}_ENDPOINT` |

**Usage**:
```python
from data_formulator.model_registry import ModelRegistry
registry = ModelRegistry()
all_models = registry.get_models()  # {provider → [model_name, ...]}
```

---

### 3. Error Handling — `errors.py` & `error_handler.py`

**Error Protocol**: **HTTP 200 + structured JSON body**
- Application errors are *not* HTTP status changes; they are business-logic errors
- Response: `{"status": "error", "code": "ERROR_CODE", "message": "...", "request_id": "..."}`

**ErrorCode Enum** (`errors.py`):
```python
class ErrorCode:
    # Authentication
    AUTH_REQUIRED, AUTH_EXPIRED, ACCESS_DENIED
    
    # Validation
    INVALID_REQUEST, TABLE_NOT_FOUND, FILE_PARSE_ERROR
    
    # LLM Errors
    LLM_AUTH_FAILED, LLM_RATE_LIMIT, LLM_CONTEXT_TOO_LONG
    LLM_MODEL_NOT_FOUND, LLM_TIMEOUT, LLM_SERVICE_ERROR
    
    # Data Connector
    CONNECTOR_AUTH_FAILED, DB_CONNECTION_FAILED, DB_QUERY_ERROR
    
    # Code Execution
    CODE_EXECUTION_ERROR, AGENT_ERROR
    
    # System
    INTERNAL_ERROR, SERVICE_UNAVAILABLE
```

**Global Error Handlers** (`error_handler.py`):
```python
def register_error_handlers(app):
    """Install unified error handlers on Flask app"""
    # Catches AppError, unknown exceptions, HTTP 404/413
    # Returns consistent envelope with request_id for debugging
```

**Error Classification**:
- LLM errors parsed from exception message (regex matching)
- Connector errors classified by database type
- Unknown errors wrapped with safe debug hint + request_id

**Usage in Routes**:
```python
from data_formulator.errors import AppError, ErrorCode
raise AppError(ErrorCode.TABLE_NOT_FOUND, "Table 'sales' not found")
# → {"status": "error", "code": "TABLE_NOT_FOUND", "message": "Table 'sales' not found"}
```

---

### 4. Workspace Factory — `workspace_factory.py`

**Purpose**: Abstract away workspace storage backend selection

**Key Components**:
- `_get_backend()` — Read from Flask config (env vars via CLI)
- `get_workspace_manager(identity_id)` — Return manager for user's workspaces
- `_build_azure_container_client(cfg)` — Azure Blob credential resolution

**Backends**:
| Backend | Storage | Use Case | Config |
|---------|---------|----------|--------|
| `local` | Filesystem | Single-user, local dev | `~/.data_formulator/users/<id>/` |
| `ephemeral` | RAM | Demos, testing, anonymous | Sessions lost on restart |
| `azure_blob` | Azure Blob Storage | Multi-user hosted | Connection string or Entra ID |

**Usage**:
```python
from data_formulator.workspace_factory import get_workspace_manager
from flask import current_app

# In a route handler (Flask context required)
mgr = get_workspace_manager(user_id)
ws = mgr.get_or_create("my_analysis")  # Returns Workspace instance
```

---

### 5. Data Connector — `data_connector.py`

**Purpose**: Generic lifecycle wrapper for data loaders → Flask blueprints

**Key Components**:
- `DataConnector` class — Wraps any `ExternalDataLoader` subclass
- `create_blueprint()` → Returns Flask blueprint with auth/catalog/data routes
- `DATA_CONNECTORS` — Global registry of enabled connectors

**Generated Routes** per connector:
- `GET /api/connectors/{id}/catalog` — Browse data sources
- `POST /api/connectors/{id}/test-connection` — Validate credentials
- `GET /api/connectors/{id}/data` — Execute query, return sample rows

**Example: Registering PostgreSQL**:
```python
from data_formulator.data_connector import DataConnector
from data_formulator.data_loader.postgresql_data_loader import PostgreSQLDataLoader

connector = DataConnector.from_loader(
    PostgreSQLDataLoader,
    source_id="prod_pg",
    display_name="Production Database",
    default_params={"host": "db.corp", "database": "prod"}
)
app.register_blueprint(connector.create_blueprint())
```

---

## Key Modules

### `py-src/data_formulator/agents/` — Legacy Agents (11 specialized agents)

**Purpose**: Single-turn or simple-loop agents for specific tasks  
**Pattern**: System prompt + 1 LLM call → dict result (no streaming, no workspace access)

**Files**:
```
agents/
├── agent_simple.py           # nl_to_filter, workspace_name, intent extraction
├── agent_data_load.py        # One-shot type inference (minimal reasoning)
├── agent_data_loading_chat.py # Conversational data loading w/ tools
├── agent_chart_restyle.py    # Apply style edits to Vega-Lite specs
├── agent_code_explanation.py # Describe derived fields
├── agent_chart_insight.py    # Title + 1-3 takeaways from chart
├── agent_sort_data.py        # Natural-order sorting
├── agent_workflow_distill.py # Summarise analysis context
├── agent_diagnostics.py      # Troubleshooting agent
├── agent_language.py         # Language instruction injection
├── agent_utils.py            # Shared helpers (compose prompts, extract JSON, etc.)
├── client_utils.py           # LLM client wrapper (streaming, error handling)
├── context.py                # Context assembly (schema, stats, sample rows)
├── semantic_types.py         # Column semantic type definitions
├── reasoning_log.py          # Reasoning chain tracking
└── web_utils.py              # Web-based utilities
```

**Key Functions**:
- `compose_system_prompt(base, coding_rules, language)` — Assemble system prompts
- `extract_json_objects(text)` — Parse JSON from LLM responses
- `build_lightweight_table_context(ws, table_name)` — 1KB schema summary
- `build_focused_thread_context(ws, thread_id, num_rows)` — 4KB detailed context

**Usage Pattern**:
```python
from data_formulator.agents.agent_simple import extract_intent
from data_formulator.agents.client_utils import Client

result = extract_intent(
    Client(model="gpt-4o", temperature=0.2),
    user_query="Show me sales by region"
)
# → {"intent": "visualization", "intent_type": "aggregate"}
```

---

### `py-src/data_formulator/analyst/` — Modern Unified Agent

**Purpose**: Replace separate DataAgent + ReportGenAgent with single multi-skill agent  
**Pattern**: Tool-calling loop + skills system (gated actions)

**Architecture**:
```
analyst/
├── agent.py              # Main AnalystAgent shell (tool loop + skill dispatch)
├── tools.py              # Inspection tools (execute_python, inspect_source_data, load_skill)
├── __init__.py           # Public exports (AnalystAgent, Event, Skill, etc.)
│
└── skills/               # Skill plugins
    ├── base.py           # BaseSkill, SkillRegistry classes
    ├── __init__.py       # Skill export + registry builder
    │
    ├── core/             # Core skill (always loaded)
    │   ├── skill.py      # SKILL.md content, visualize/delegate actions
    │   └── handler.py    # Tool/action handlers
    │
    ├── data-loading/     # Data loading skill (gated)
    ├── data_loading/     # Alternative data loading
    ├── report/           # Report generation skill (gated)
    └── ... (more skills)
```

**Core Concepts**:

1. **Inspection Tools** (parallel-safe, internal):
   - `execute_python_script(purpose, code)` → stdout string
   - `inspect_source_data(table_names)` → schema + stats + samples
   - `load_skill(name)` → unlock gated actions from skill

2. **Always-Available Actions**:
   - `visualize(table_name, vega_lite_spec)` → render chart
   - `delegate(target_agent, input)` → call another agent (e.g., for report writing)

3. **Gated Actions** (unlocked after `load_skill`):
   - `write_report()` — From report skill
   - `restyle_chart()` — From chart skill
   - ... (skill-defined)

**Run Lifecycle**:
```
1. Load core skill, build tool registry
2. Call LLM with system prompt (includes loaded skills)
3. LLM calls tools (inspect_python_script, etc.) or commits action (visualize, etc.)
4. Shell routes to skill handler, gets observation
5. Repeat until LLM produces no action (run ends)
→ Final plain text is completion (shown to user)
```

**Usage**:
```python
from data_formulator.analyst import AnalystAgent
from data_formulator.agents.client_utils import Client

agent = AnalystAgent(
    client=Client(model="gpt-4o", temperature=0.7),
    workspace=ws,
    thread_id="analysis-1"
)

# Stream events back to frontend
for event in agent.run(user_query="Analyze sales trends"):
    if event.type == "action":
        print(f"Visualizing: {event.data}")
    elif event.type == "completion":
        print(f"Done: {event.data}")
```

---

### `py-src/data_formulator/data_loader/` — Data Import System

**Purpose**: Unified interface for 15+ data sources (databases, cloud, APIs)

**Architecture**:
```
data_loader/
├── __init__.py                      # Registry + loader discovery
├── external_data_loader.py          # Abstract base class
├── connector_errors.py              # Error classification
├── probe_utils.py                   # Connection testing utilities
│
├── [Database Loaders]
│   ├── postgresql_data_loader.py    # PostgreSQL
│   ├── mysql_data_loader.py         # MySQL
│   ├── mssql_data_loader.py         # SQL Server
│   ├── clickhouse_data_loader.py    # ClickHouse
│   ├── databricks_data_loader.py    # Databricks
│   └── kusto_data_loader.py         # Azure Kusto
│
├── [Cloud Storage]
│   ├── s3_data_loader.py            # AWS S3
│   ├── azure_blob_data_loader.py    # Azure Blob
│   └── local_folder_data_loader.py  # Local filesystem
│
├── [Analytics Platforms]
│   ├── bigquery_data_loader.py      # Google BigQuery
│   ├── athena_data_loader.py        # AWS Athena
│   ├── superset_data_loader.py      # Superset instance
│   └── sample_datasets_loader.py    # Built-in demo data
│
├── [Document Stores]
│   ├── mongodb_data_loader.py       # MongoDB
│   └── cosmosdb_data_loader.py      # Azure CosmosDB
│
└── guides/                          # Documentation
```

**Loader Registration** (`__init__.py`):
```python
_LOADER_SPECS = [
    ("mysql", "mysql_data_loader", "MySQLDataLoader", "pymysql"),
    ("postgresql", "postgresql_data_loader", "PostgreSQLDataLoader", "psycopg2-binary"),
    # ... 15 total
]

# Output:
DATA_LOADERS              # {loader_key → LoaderClass}
DISABLED_LOADERS          # {key → ImportError reason}
PLUGIN_LOADERS            # {key → file_path} for plugins
PLUGIN_ERRORS             # {key → {"file", "reason"}}
```

**ExternalDataLoader Base Class**:
```python
class ExternalDataLoader(ABC):
    @abstractmethod
    def get_catalog(self) → CatalogNode
        """Return hierarchical catalog (databases → schemas → tables)"""
    
    @abstractmethod
    def get_table_schema(self, table_path: str) → TableSchema
        """Return column names + types for a table"""
    
    @abstractmethod
    def get_sample_data(self, table_path: str, limit=100) → pd.DataFrame
        """Return sample rows (used for data preview)"""
    
    @abstractmethod
    def query(self, sql: str, limit=1000) → pd.DataFrame
        """Execute SQL query, return results"""
```

**Plugin System**:
- Scan `~/.data_formulator/plugins/` for `*_data_loader.py` files
- Auto-register any `ExternalDataLoader` subclass
- Built-in loaders can be overridden by plugins (plugin key wins)
- Only enabled in local single-user mode (set `DF_ALLOW_PLUGINS=1` to enable on servers)

**Error Classification** (`connector_errors.py`):
```python
classify_connector_error(exc, loader_type) → ErrorCode
# Detects: auth failures, firewall blocks, query syntax errors, etc.
# Maps to: CONNECTOR_AUTH_FAILED, DB_FIREWALL_BLOCKED, DB_QUERY_ERROR, ...
```

---

### `py-src/data_formulator/auth/` — Authentication & Authorization

**Purpose**: Pluggable auth system supporting OIDC, GitHub OAuth, Kusto, Transparent (no-auth)

**Architecture**:
```
auth/
├── __init__.py
├── identity.py               # Auth provider factory + get_active_provider()
├── token_store.py            # Server-side session token storage
│
├── gateways/                 # Flask blueprints for auth flow endpoints
│   ├── oidc_gateway.py       # OIDC callback, token refresh
│   ├── github_gateway.py     # GitHub OAuth callback
│   ├── kusto_oauth_gateway.py # Kusto delegated auth callback
│   └── __init__.py
│
├── providers/                # Auth provider implementations
│   ├── base.py               # BaseAuthProvider abstract class
│   ├── oidc.py               # OIDC provider (Entra ID, Keycloak, etc.)
│   ├── github_oauth.py       # GitHub OAuth provider
│   ├── azure_easyauth.py     # Azure App Service EasyAuth
│   └── __init__.py
│
└── vault/                    # Credential storage
    ├── base.py               # BaseVault abstract class
    ├── local_vault.py        # Filesystem-based encryption
    └── __init__.py
```

**Auth Providers** (`identity.py`):

| Provider | Mode | Description | Config Vars |
|----------|------|-------------|-------------|
| `transparent` | No-auth | Anonymous, all users same identity | None |
| `oidc` | SSO | OIDC-compliant (Entra ID, Keycloak, Okta) | `AUTH_PROVIDER=oidc`, `OIDC_*` vars |
| `github` | OAuth2 | GitHub OAuth app | `AUTH_PROVIDER=github`, `GITHUB_*` vars |
| `kusto` | Delegated | Kusto delegated auth (Entra ID) | `AUTH_PROVIDER=kusto`, `KUSTO_*` vars |
| `azure_easyauth` | Managed | Azure App Service EasyAuth | `AUTH_PROVIDER=azure_easyauth` |

**BaseAuthProvider Interface**:
```python
class BaseAuthProvider:
    @property
    def name(self) → str
        """Provider identifier (e.g. "oidc", "github")"""
    
    def get_identity_id(self, request) → str
        """Extract current user's identity from request"""
    
    def get_tokens(self) → dict[str, str]
        """Return SSO tokens for data connector use"""
    
    def redirect_to_login(self) → Response
        """Initiate login flow (if needed)"""
```

**Token Store** (`token_store.py`):
```python
# Server-side session storage for OAuth tokens (avoids 4KB cookie limit)
store = TokenStore(storage_backend=FileSystemCache)
store.set(identity_id, "oidc_access_token", token_value)
store.get(identity_id, "oidc_access_token") → token_value
```

**Usage in Routes**:
```python
from data_formulator.auth.identity import get_active_provider

provider = get_active_provider()
user_id = provider.get_identity_id(request)  # Current logged-in user
tokens = provider.get_tokens()               # SSO tokens
```

---

## Agent Architecture

### Agent Selection Flow

```
Frontend: POST /api/agents/run
  → Request includes: agent_id, workspace_id, query, thread_id
  
Backend routes.agents:
  1. Load workspace from workspace_id
  2. If agent_id == "analyst":
       → Use modern AnalystAgent (skill-based)
  3. Else (legacy agents):
       → Route to agent_*.py function
       → Return result dict
       
Streaming:
  → Agent yields events (tool_call, chunk, action, completion)
  → Each event is NDJSON line (Server-Sent Events)
  → Client receives in real-time, updates Redux state
```

### Legacy Agent Types

| Agent | File | Purpose | Reasoning Effort | Streaming |
|-------|------|---------|------------------|-----------|
| `data_transform` | agent_data_load.py | Type inference + schema learning | low | ✅ (if Python output) |
| `data_loading_chat` | agent_data_loading_chat.py | Conversational data loading w/ tools | low | ✅ |
| `chart_recommendation` | agent_chart_restyle.py | Suggest chart types | low | ❌ |
| `code_explanation` | agent_code_explanation.py | Describe derived field code | minimal | ❌ |
| `chart_insight` | agent_chart_insight.py | Generate chart title + takeaways | minimal | ❌ |
| `simple` | agent_simple.py | Intent extraction, filter parsing | minimal | ❌ |
| `language` | agent_language.py | Language-aware prompt injection | minimal | ❌ |
| `starter_questions` | agent_starter_questions.py | Generate initial analysis ideas | minimal | ❌ |

### Modern Analyst Agent

| Aspect | Details |
|--------|---------|
| **File** | `analyst/agent.py` |
| **Reasoning** | `"low"` (via `agent_config.py`) |
| **Streaming** | ✅ Full tool-calling loop |
| **Skills** | Dynamically loaded (core always, others on-demand) |
| **Actions** | visualize, delegate, write_report (if skill loaded) |
| **Context** | Builds focused/peripheral context per turn |

---

## Data Loading System

### Loader Discovery & Initialization

```python
from data_formulator.data_loader import DATA_LOADERS, DISABLED_LOADERS

# All available loaders
for key, loader_class in DATA_LOADERS.items():
    print(f"{key}: {loader_class}")

# Loaders that failed to import (missing dependencies)
for key, error_msg in DISABLED_LOADERS.items():
    print(f"{key} disabled: {error_msg}")
```

### Using a Loader

```python
from data_formulator.data_loader import DATA_LOADERS

# PostgreSQL example
loader = DATA_LOADERS['postgresql'](
    host='db.example.com',
    port=5432,
    database='analytics',
    username='user',
    password='pass'
)

# Browse data
catalog = loader.get_catalog()
# → CatalogNode(name='root', children=[...databases...])

# Get table schema
schema = loader.get_table_schema('public.customers')
# → TableSchema(columns={'id': 'INT', 'email': 'VARCHAR', ...})

# Fetch sample data
df = loader.get_sample_data('public.customers', limit=100)

# Execute query
df = loader.query('SELECT * FROM public.customers WHERE created > NOW() - INTERVAL 1 DAY')
```

### Adding a Custom Loader

**Option 1: Built-in** — Add to `_LOADER_SPECS` in `__init__.py`:
```python
_LOADER_SPECS.append(
    ("my_api", "data_formulator.data_loader.my_api_loader", "MyAPILoader", "my-api-package")
)
```

**Option 2: Plugin** — Create `~/.data_formulator/plugins/my_custom_loader.py`:
```python
from data_formulator.data_loader.external_data_loader import ExternalDataLoader

class MyCustomLoader(ExternalDataLoader):
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url
    
    def get_catalog(self):
        # Return hierarchical catalog
        ...
    
    def query(self, sql, limit=1000):
        # Execute query via API
        ...
```

---

## Error Handling

### Unified Error Envelope

**On Error**:
```json
{
  "status": "error",
  "code": "LLM_RATE_LIMIT",
  "message": "Rate limit exceeded. Please try again in 30 seconds.",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "retryable": true,
  "details": { ... }
}
```

**On Success**:
```json
{
  "status": "ok",
  "data": { ... },
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Error Classification

**LLM Errors** are classified by regex matching on exception message:

| Pattern | ErrorCode | Retryable |
|---------|-----------|-----------|
| 401, unauthorized, invalid.*api.*key | LLM_AUTH_FAILED | ❌ |
| 429, rate.*limit | LLM_RATE_LIMIT | ✅ |
| context.*length, too many tokens | LLM_CONTEXT_TOO_LONG | ❌ |
| 50x, bad gateway, unavailable | LLM_SERVICE_ERROR | ✅ |
| timeout, connection refused | LLM_TIMEOUT | ✅ |
| content.*filter, safety | LLM_CONTENT_FILTERED | ❌ |

**Database Errors** are classified by connector type:
- PostgreSQL: Parse server error messages
- MySQL: Check error codes
- Kusto: Map ADX-specific errors
- etc.

### Sanitization

All error messages are sanitized via `SensitiveDataFilter`:
- Removes API keys, tokens, passwords
- Redacts in both logs and HTTP responses
- Applies regex patterns for common patterns

---

## Component Connections

### Request Flow: Running an Agent

```
1. Frontend (React)
   └─→ POST /api/agents/run
       { agent_id: "analyst", query: "...", workspace_id: "...", thread_id: "..." }

2. Route Handler (routes.agents.py)
   ├─ Load workspace via WorkspaceManager
   ├─ Load agent context (tables, previous thread state)
   ├─ Instantiate agent (AnalystAgent or legacy)
   └─ Stream events back as NDJSON

3. Agent Execution
   ├─ [Modern] AnalystAgent.run(query)
   │  ├─ Build system prompt (core skill + loaded skills)
   │  ├─ Call LLM with tool registry
   │  ├─ For each tool call:
   │  │  ├─ execute_python_script → run in sandbox, capture stdout
   │  │  ├─ inspect_source_data → query workspace metadata
   │  │  └─ load_skill → inject skill SKILL.md into context
   │  ├─ For each action (visualize, write_report, etc.):
   │  │  ├─ Route to skill handler
   │  │  ├─ Get observation string
   │  │  └─ Feed back to LLM
   │  └─ When LLM commits no action → run ends
   │
   └─ [Legacy] agent_*.py() function
      └─ Single LLM call → return result dict

4. Response Streaming
   ├─ Event: "init" (startup markers)
   ├─ Event: "tool_call" → tool_name, tool_input
   ├─ Event: "chunk" → LLM reasoning token
   ├─ Event: "action" → user-visible surface (chart rendered, etc.)
   ├─ Event: "completion" → final summary text
   └─ Send as NDJSON lines (one JSON per line, \n-separated)

5. Frontend Redux
   ├─ On "chunk": accumulate into assistant message
   ├─ On "action": render surface (Vega chart, etc.)
   ├─ On "completion": finalize thread, allow next turn
   └─ Update UI accordingly
```

### Data Loading Flow

```
1. Frontend: User adds connector via DataConnector UI
   └─→ POST /api/connectors/{id}/test-connection

2. DataConnector Blueprint (data_connector.py)
   ├─ Route → DataConnector instance (from DATA_CONNECTORS registry)
   ├─ Call Loader.get_catalog() or Loader.query(...)
   ├─ If error → classify via classify_connector_error()
   └─ Return structured response

3. Catalog Browsing
   └─→ GET /api/connectors/{id}/catalog?path=db/schema
       ├─ Loader.get_catalog() → CatalogNode tree
       ├─ Report progress via _set_catalog_progress()
       └─ Return paginated nodes

4. Data Query
   └─→ GET /api/connectors/{id}/data?table=my_table
       ├─ Loader.get_table_schema() → columns
       ├─ Loader.get_sample_data() → sample rows
       ├─ Serialize to JSON via df_to_safe_records()
       └─ Return {"schema": ..., "data": [...]}

5. Data Persistence
   ├─ Save sample as Parquet in workspace
   ├─ Store metadata (semantic types, column tags)
   └─ Workspace.add_table(name, df, metadata)
```

### Authentication Flow (OIDC Example)

```
1. Frontend: User opens app
   ├─ Check localStorage for id_token
   └─ If missing or expired → redirect to login

2. Login Redirect
   └─→ GET /auth/tokens/login
       ├─ OIDC provider checks AUTH_PROVIDER env
       ├─ Redirect to IdP (e.g., Entra ID)
       └─ [IdP: User enters credentials]

3. IdP Callback
   ← Redirect from IdP with authorization_code

4. Callback Handler (oidc_gateway.py)
   └─→ POST /auth/callback
       ├─ Exchange code for tokens (client_credentials flow)
       ├─ Store tokens in TokenStore (server-side session)
       ├─ Set secure httpOnly cookie
       └─ Redirect to "/" with redirect param

5. Authenticated Requests
   ├─ Browser sends cookie automatically
   ├─ Route handler:
   │  ├─ provider = get_active_provider()
   │  ├─ user_id = provider.get_identity_id(request)
   │  └─ Load user's workspace via user_id
   └─ Success

6. Token Refresh
   └─ If access token expired, refresh via TokenStore
      (automatic, no frontend involvement)
```

---

## Environment & Configuration

### Configuration Resolution Order

| Layer | Source | Priority |
|-------|--------|----------|
| 1 | CLI arguments (`--flag value`) | Highest |
| 2 | Environment variables (`.env`) | Medium |
| 3 | Defaults (in code) | Lowest |

### Flask Config

All CLI args stored in:
```python
from flask import current_app
cli_args = current_app.config['CLI_ARGS']
# {
#   'host': '127.0.0.1',
#   'workspace_backend': 'local',
#   'sandbox': 'local',
#   'disable_data_connectors': False,
#   'max_display_rows': 10000,
#   ...
# }
```

### Logging Configuration

**File Logging**: `~/.data_formulator/logs/data_formulator.log`
- Rotates at 10 MB, keeps 5 backups
- Includes all components at DEBUG level
- Sanitized (API keys removed)

**Console Logging**: Stdout
- Default level: INFO
- Override via `LOG_LEVEL=DEBUG` env var

---

## Development Tips

### 1. Adding a New Route Handler

Create `py-src/data_formulator/routes/my_feature.py`:
```python
from flask import Blueprint, request
from flask_cors import cross_origin
from data_formulator.error_handler import json_ok
from data_formulator.errors import AppError, ErrorCode

my_feature_bp = Blueprint('my_feature', __name__, url_prefix='/api/my-feature')

@my_feature_bp.route('/endpoint', methods=['POST'])
@cross_origin()
def my_endpoint():
    try:
        data = request.get_json()
        # ... your logic ...
        return json_ok({"result": ...})
    except AppError as e:
        raise  # Global error handler catches
    except Exception as e:
        # Wrap unexpected errors
        raise AppError(ErrorCode.INTERNAL_ERROR, str(e))
```

Then register in `app.py`:
```python
from data_formulator.routes.my_feature import my_feature_bp
app.register_blueprint(my_feature_bp)
```

### 2. Debugging Agent Execution

```python
import logging
logging.getLogger('data_formulator.analyst.agent').setLevel(logging.DEBUG)

# Logs will show:
# - Tool calls with inputs
# - LLM responses
# - Skill routing
# - Action execution
```

### 3. Testing Loaders

```python
from data_formulator.data_loader import DATA_LOADERS

loader = DATA_LOADERS['postgresql'](
    host='localhost',
    port=5432,
    database='test',
    username='user',
    password='pass'
)

# Test connection
try:
    catalog = loader.get_catalog()
    print("✓ Connected")
except Exception as e:
    print(f"✗ Connection failed: {e}")
```

### 4. Using the Sandbox

```python
from data_formulator.sandbox import execute_python_script

output = execute_python_script(
    """
import pandas as pd
df = pd.read_csv('data.csv')
print(df.describe())
    """,
    timeout=30
)
print(output)  # Stdout captured
```

---

## Key Files Quick Reference

| File | Purpose |
|------|---------|
| `app.py` | Flask factory, blueprint registration |
| `__main__.py` | CLI entry point |
| `agent_config.py` | Reasoning effort per agent |
| `model_registry.py` | LLM provider loader |
| `workspace_factory.py` | Workspace backend factory |
| `data_connector.py` | Generic connector lifecycle |
| `errors.py` | ErrorCode enum |
| `error_handler.py` | Global error handlers |
| `agents/agent_*.py` | 10 legacy single-turn agents |
| `analyst/agent.py` | Modern multi-turn agent (skills) |
| `analyst/skills/` | Skill plugins (visualize, report, etc.) |
| `data_loader/` | 15+ data source loaders |
| `auth/providers/` | OIDC, GitHub, Kusto, Azure auth |
| `auth/gateways/` | OAuth callback handlers |

---

## Summary

The Data Formulator backend is a **modular, pluggable architecture** built on Flask:

- **Entry**: `uv run data_formulator` → `app.py` → lazy blueprint loading
- **Agents**: Modern skill-based (analyst) + 10 legacy single-turn agents
- **Data**: 15+ loaders via generic `ExternalDataLoader` + plugin system
- **Auth**: Pluggable providers (OIDC, GitHub, Kusto, transparent)
- **Errors**: Unified HTTP 200 + JSON envelope with machine-readable codes
- **Storage**: Pluggable backends (local filesystem, ephemeral RAM, Azure Blob)

Each component is independently testable and can be extended without touching others. The system favors **separation of concerns** and **fail-graceful** error handling.
