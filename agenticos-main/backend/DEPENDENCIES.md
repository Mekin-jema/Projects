# AgenticOS dependency reference

This document describes the packages declared in `pyproject.toml`. The descriptions are based on the dependency names and the configuration comments; for packages whose use is not explicitly described there, the purpose is the package's usual role. A dependency being installed does not mean every feature is enabled in every deployment.

## Runtime dependencies

- **`fastapi>=0.141.1`** — Builds the platform's HTTP API and request/response routes.
- **`uvicorn[standard]>=0.54.0`** — Runs the ASGI application server.
- **`pydantic[email]>=2.13.5`** — Validates and serializes structured data; includes email validation extra.
- **`pydantic-settings>=2.15.0`** — Loads and validates application configuration from environment/settings.
- **`python-multipart>=0.0.20`** — Enables multipart form and file-upload parsing in FastAPI/Starlette.
- **`logfire[fastapi,asyncpg,redis,httpx]>=5.1.0`** — Application observability, tracing and logging; integrations for FastAPI, asyncpg, Redis and httpx.
- **`sqlalchemy[asyncio]>=2.1.3`** — ORM and database access layer, including asynchronous support.
- **`asyncpg>=0.31.0`** — Async PostgreSQL driver used by postgresql+asyncpg database URLs.
- **`psycopg2-binary>=2.9.13`** — PostgreSQL driver used by Alembic's synchronous migration URL.
- **`alembic>=1.19.2`** — Manages and applies database schema migrations.
- **`greenlet>=3.5.5`** — Provides the bridge used by SQLAlchemy's async support.
- **`pyjwt>=2.15.1`** — Creates and verifies JSON Web Tokens.
- **`bcrypt>=4.0.0`** — Hashes and verifies passwords.
- **`authlib>=1.8.0`** — OAuth and authentication client/server utilities.
- **`anyio>=4.15.1`** — Async concurrency and compatibility utilities; also imported by application services.
- **`redis>=8.1.0`** — Connects to Redis for caching, queues or shared state.
- **`aiosmtplib>=5.1.3`** — Sends email using SMTP asynchronously.
- **`itsdangerous>=2.2.0`** — Signs data such as session cookies.
- **`prefect>=3.8.7`** — Orchestrates and schedules workflows/tasks.
- **`pydantic-ai-slim[openrouter,anthropic,google,duckduckgo,web-fetch,groq,mistral,cohere,huggingface,xai]>=2.52.0`** — Pydantic AI agent framework with provider and integration extras (OpenRouter, Anthropic, Google, web search/fetch and others).
- **`genai-prices>=0.1.4`** — Provides model pricing data for estimating AI usage costs.
- **`pydantic-ai-slim[mcp]>=2.52.0`** — Pydantic AI agent framework with provider and integration extras (OpenRouter, Anthropic, Google, web search/fetch and others).
- **`mcp>=2.3.0`** — Model Context Protocol SDK for connecting to MCP tools/servers.
- **`pydantic-ai-harness>=0.52.0`** — Adds agent capabilities used here for guardrails, planning and context compaction.
- **`websockets>=15.0`** — WebSocket protocol support for real-time connections.
- **`rank-bm25>=0.2.2`** — BM25 keyword-based ranking used in hybrid document retrieval.
- **`pymupdf>=1.28.2`** — Reads and extracts text/content from PDF documents.
- **`pillow>=10.0.0`** — Image processing and image conversion, including chart images.
- **`python-docx>=1.1.0`** — Reads and writes Microsoft Word DOCX documents.
- **`openpyxl>=3.1.0`** — Reads and writes Excel XLSX spreadsheets.
- **`llama-cloud>=2.16.0`** — Connects to LlamaCloud document parsing/indexing services.
- **`liteparse>=2.15.1`** — Lightweight document/content parsing.
- **`google-api-python-client>=2.201.0`** — Calls Google APIs such as Drive and related services.
- **`google-auth>=2.59.1`** — Google authentication and credential handling.
- **`boto3>=1.43.108`** — AWS SDK for Python; accesses AWS services.
- **`httpx>=0.28.0`** — Async/sync HTTP client used for the application's own HTTP requests.
- **`httpx2>=2.13.1`** — Second HTTP client API required by the MCP SDK/vendor SDK boundary in this project.
- **`click>=8.5.0`** — Builds command-line interfaces.
- **`tabulate>=0.9.0`** — Formats CLI output as readable tables.
- **`markdown-it-py>=4.0.0`** — Converts Markdown into rendered HTML/content.
- **`tqdm>=4.70.1`** — Displays progress bars for long-running operations.
- **`tavily-python>=0.8.4`** — Uses Tavily search/research API.
- **`pydantic-monty>=1.1.0`** — Provides the Monty execution/runtime integration used by the agent platform.
- **`pydantic-ai-skills>=2.0.0`** — Loads and exposes agent skills/capabilities.
- **`pydantic-ai-backend[console,remote,workspaces,daytona]>=0.2.32`** — Backend integrations for agent consoles, remote files/workspaces and Daytona sandboxes.
- **`subagents-pydantic-ai>=0.2.25`** — Supports delegating tasks to child/subagents.
- **`cryptography>=50.0.2`** — Cryptographic primitives and secure cryptographic operations.
- **`aiogram>=3.31.0,<4.0`** — Telegram bot framework.
- **`slack-sdk>=3.45.0`** — Integrates with Slack APIs and bot features.
- **`aiohttp>=3.14.4`** — Async HTTP transport required for Slack Socket Mode.
- **`croniter>=3.0.0`** — Calculates upcoming times for cron schedule expressions.
- **`mem0ai>=2.2.1`** — Provides persistent/long-term memory functionality for AI agents.
- **`requests>=2.34.2`** — Synchronous HTTP client; declared for a dependency that imports it.
- **`xlrd>=2.0.2`** — Reads legacy Excel XLS files.
- **`odfpy>=1.4.1`** — Reads and writes OpenDocument spreadsheet/document formats.
- **`python-pptx>=1.0.2`** — Reads and writes PowerPoint PPTX presentations.
- **`olefile>=0.47`** — Reads OLE compound files used by some older Microsoft Office formats.
- **`ldap3>=2.9.1`** — Communicates with LDAP directories such as Active Directory/OpenLDAP/FreeIPA.
- **`phonenumberslite>=9.0.40`** — Parses and validates phone numbers using numbering-plan metadata.

## Optional dependencies

These are installed only when the corresponding extra is selected.

### `browser` extra
- **`cdp-use==1.4.5`** — Typed asynchronous Chrome DevTools Protocol client used by the browser capability.
- **`pydantic-ai-slim[typesafe]>=2.52.0`** — Pydantic AI agent framework with provider and integration extras (OpenRouter, Anthropic, Google, web search/fetch and others).

### `kerberos` extra
- **`gssapi>=1.9.0`** — Enables Kerberos/SPNEGO integrated sign-in; requires system Kerberos libraries when building the package.

## Development dependency group (`dev`)

Installed for development/testing, not in a production `--no-dev` environment.

- **`pytest>=9.0.0`** — Runs automated tests.
- **`anyio[trio]>=4.15.1`** — Async concurrency and compatibility utilities; also imported by application services.
- **`pytest-cov>=6.1.0`** — Reports test coverage.
- **`httpx>=0.28.0`** — HTTP client used by API tests.
- **`ruff>=0.16.10`** — Lints and formats Python code, including import sorting and many bug/security checks.
- **`ty>=0.0.84`** — Static type checker for Python.
- **`pre-commit>=4.6.2`** — Runs configured checks automatically before commits.
- **`pytest-xdist>=3.8.0`** — Runs tests in parallel.
- **`pytest-randomly>=5.0.0`** — Randomizes test order to reveal order-dependent tests.
- **`vulture>=2.14`** — Finds potentially unused Python code.
- **`deptry>=0.23.0`** — Checks dependency declarations against imports.
- **`types-ldap3>=2.9.13`** — Typing stubs for ldap3.

## Documentation dependency group (`docs`)

Used to build the project documentation website.

- **`mkdocs>=1.6.0`** — Builds the documentation site.
- **`mkdocs-glightbox>=0.5.2`** — Adds image lightbox behavior to documentation pages.
- **`mkdocs-material>=9.5.0`** — Provides the Material theme and site components.
- **`mkdocstrings[python]>=1.0.6`** — Generates API documentation from Python docstrings.
- **`mkdocs-static-i18n>=1.2.3`** — Builds localized documentation from translated Markdown files.

## Build and quality tools configured in this file

- **Hatchling** — builds the Python package/wheel.
- **Vulture** — detects unused code.
- **Deptry** — checks dependency/import consistency.
- **Ruff** — Python linting and import/style checks.
- **ty** — static type checking.
- **pytest** — test discovery and execution; the `security` marker labels security-boundary tests.
- **Coverage.py** (through `pytest-cov`) — measures test coverage for selected application modules.

## Notes

- Package version constraints are preserved in the cleaned TOML file.
- `browser` and `kerberos` are optional extras; `dev` and `docs` are dependency groups.
- The CLI entry point is `agenticos`, mapped to `cli.commands:main`.
