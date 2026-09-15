# Flask in Data Formulator: Real-World Examples

**See Flask concepts applied in actual production code**

---

## Table of Contents

1. [Application Setup](#application-setup)
2. [Authentication Flows](#authentication-flows)
3. [Data Loading](#data-loading)
4. [Agent Execution & Streaming](#agent-execution--streaming)
5. [Error Handling](#error-handling)
6. [Session Management](#session-management)
7. [Middleware & Request Lifecycle](#middleware--request-lifecycle)

---

## Application Setup

### Creating the Flask App (from `app.py`)

**Concept**: Application factory pattern

```python
# Data Formulator's actual setup
import os
import secrets
from flask import Flask
from pathlib import Path

# 1. Create Flask app
app = Flask(__name__, static_url_path='', static_folder=os.path.join(APP_ROOT, "dist"))

# 2. Configure from environment
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(16)

# 3. Set limits
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 MB file upload limit

# 4. Session configuration
app.config['PERMANENT_SESSION_LIFETIME'] = 60 * 60 * 24 * 365  # 1 year
app.config['SESSION_COOKIE_HTTPONLY'] = True  # No JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection

# 5. JSON configuration
app.json.sort_keys = False
app.json.ensure_ascii = False

# 6. Load CLI arguments into config
app.config['CLI_ARGS'] = {
    'host': os.environ.get('HOST', '127.0.0.1'),
    'sandbox': os.environ.get('SANDBOX', 'local'),
    'max_display_rows': int(os.environ.get('MAX_DISPLAY_ROWS', '10000')),
}
```

**What's happening**:
- Loads frontend static files from `dist/` folder
- Sets session timeout to 1 year (for long-lived workspaces)
- Limits JSON responses to specific encoding
- Stores server configuration in `app.config` for access throughout the app

### Blueprint Registration (from `app.py`)

**Concept**: Lazy loading blueprints to optimize startup

```python
def _register_blueprints():
    """Import and register blueprints with lazy loading."""
    
    # Register error handlers first (always needed)
    from data_formulator.error_handler import register_error_handlers
    register_error_handlers(app)
    
    # Load heavy libraries with spinner feedback
    from data_formulator._startup_spinner import spinner
    
    # Data blueprints
    with spinner("Loading data loader drivers"):
        from data_formulator.routes.tables import tables_bp
    app.register_blueprint(tables_bp)  # Routes: /api/tables/*
    
    # Agent blueprints
    with spinner("Loading AI agents"):
        from data_formulator.routes.agents import agent_bp
    app.register_blueprint(agent_bp)   # Routes: /api/agents/*
    
    # Session blueprints
    from data_formulator.routes.sessions import session_bp
    app.register_blueprint(session_bp) # Routes: /api/sessions/*
    
    # Authentication setup
    from data_formulator.auth.identity import init_auth, get_active_provider
    init_auth(app)  # Initialize auth provider (OIDC, GitHub, etc.)
    
    # Register auth gateways based on provider
    provider = get_active_provider()
    if provider and provider.name == "github":
        from data_formulator.auth.gateways.github_gateway import github_bp
        app.register_blueprint(github_bp)  # Routes: /api/auth/github/*
    
    # Always register token management
    from data_formulator.auth.gateways.oidc_gateway import auth_tokens_bp
    app.register_blueprint(auth_tokens_bp)  # Routes: /api/auth/*
```

**Why lazy load?**
- Avoid importing heavy dependencies (litellm, sklearn, databases) until needed
- Faster startup for CLI commands
- Show progress to user

---

## Authentication Flows

### OIDC Login (OpenID Connect)

**Concept**: Multi-step OAuth2 authorization flow

**File**: `auth/gateways/oidc_gateway.py`

```python
from flask import Blueprint, redirect, request, session
import secrets
import urllib.parse

oidc_bp = Blueprint("oidc_gateway", __name__, url_prefix="/api/auth/oidc")

# Step 1: User clicks "Login with SSO"
@oidc_bp.route("/login")
def oidc_login():
    """
    Flow:
    1. Generate random state (CSRF protection)
    2. Store state in server session
    3. Redirect to OAuth provider
    """
    cfg = _get_oidc_config()
    authorize_url = cfg.get("authorize_url")
    client_id = cfg.get("client_id")
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    session["_oauth_state"] = state  # Store server-side
    
    # Build authorization URL
    params = {
        "response_type": "code",      # We want an authorization code
        "client_id": client_id,       # App identifier
        "redirect_uri": _callback_url(),  # Where user returns
        "scope": "openid profile email",  # What info we want
        "state": state,               # CSRF token
    }
    
    auth_url = f"{authorize_url}?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)  # Send user to OAuth provider

# Step 2: OAuth provider redirects back with code
@oidc_callback_bp.route("/auth/callback")
def oidc_callback():
    """
    Flow:
    1. Get authorization code from URL
    2. Verify CSRF state
    3. Exchange code for tokens
    4. Store tokens in session
    5. Redirect to app
    """
    # OAuth provider sends: /callback?code=xyz&state=abc
    code = request.args.get("code")
    state = request.args.get("state")
    
    # Verify state matches what we stored (CSRF protection)
    if state != session.get("_oauth_state"):
        raise AppError(ErrorCode.INVALID_REQUEST, "State mismatch - CSRF attack?")
    
    # Exchange authorization code for tokens
    tokens = exchange_code_for_tokens(code)
    
    # Store tokens server-side (not in browser!)
    session["access_token"] = tokens["access_token"]
    session["refresh_token"] = tokens["refresh_token"]
    session["user_id"] = tokens["user_id"]
    
    # Redirect to app
    return redirect("/")

# Step 3: After user is logged in
@oidc_bp.route("/me")
def get_current_user():
    """
    Access token is in session (server-side)
    Frontend doesn't need to store tokens!
    """
    user_id = session.get("user_id")
    if not user_id:
        return {"error": "Not logged in"}, 401
    
    return {"user_id": user_id}

# Step 4: Logout
@oidc_bp.route("/logout")
def logout():
    """Clear session (server clears everything)."""
    session.clear()
    return {"status": "logged out"}
```

**Key Flask Concepts**:
- `session` dictionary for server-side storage
- `request.args` for URL query parameters
- `redirect()` for OAuth flow
- Tokens never exposed to browser

### GitHub OAuth (Simpler Flow)

**File**: `auth/gateways/github_gateway.py`

```python
from flask import Blueprint, request, session, redirect

github_bp = Blueprint("github_auth", __name__, url_prefix="/api/auth/github")

@github_bp.route("/login")
def github_login():
    """Start GitHub OAuth flow."""
    state = secrets.token_urlsafe(32)
    session["_github_state"] = state
    
    # Redirect to GitHub
    return redirect(
        f"https://github.com/login/oauth/authorize?"
        f"client_id={GITHUB_CLIENT_ID}&"
        f"redirect_uri={callback_url}&"
        f"scope=user:email&"
        f"state={state}"
    )

@github_bp.route("/callback")
def github_callback():
    """GitHub redirects back here."""
    code = request.args.get("code")
    state = request.args.get("state")
    
    # Verify state
    if state != session.get("_github_state"):
        abort(400)
    
    # Exchange code for token (server-to-server, not in browser)
    import requests
    response = requests.post(
        "https://github.com/login/oauth/access_token",
        data={
            "client_id": GITHUB_CLIENT_ID,
            "client_secret": GITHUB_CLIENT_SECRET,
            "code": code,
            "redirect_uri": callback_url,
        },
        headers={"Accept": "application/json"}
    )
    
    token_data = response.json()
    
    # Store in session
    session["github_token"] = token_data["access_token"]
    
    return redirect("/")
```

---

## Data Loading

### List Available Tables

**Concept**: GET request returning JSON

**File**: `routes/tables.py` (simplified)

```python
from flask import Blueprint, request, jsonify
from data_formulator.errors import AppError, ErrorCode

tables_bp = Blueprint("tables", __name__, url_prefix="/api/tables")

@tables_bp.route("/", methods=['GET'])
def list_tables():
    """
    GET /api/tables?workspace_id=123
    Returns: List of tables in workspace
    """
    workspace_id = request.args.get('workspace_id')
    
    # Load workspace
    try:
        workspace = load_workspace(workspace_id)
    except FileNotFoundError:
        raise AppError(
            ErrorCode.WORKSPACE_NOT_FOUND,
            f"Workspace '{workspace_id}' not found"
        )
    
    # Build response
    tables = []
    for table in workspace.tables:
        tables.append({
            'id': table.id,
            'name': table.name,
            'rows': len(table),
            'columns': list(table.columns),
            'semantic_types': table.semantic_types  # ID, Measure, Date, etc.
        })
    
    return jsonify({'tables': tables})
```

**Flask Patterns**:
- `@tables_bp.route()` decorator registers the route
- `methods=['GET']` specifies HTTP method
- `request.args.get()` extracts query parameters
- `jsonify()` returns JSON response

### Load Data from External Source

**Concept**: POST request with validation and error handling

```python
@tables_bp.route("/", methods=['POST'])
def create_table():
    """
    POST /api/tables
    Body: {
        "workspace_id": "123",
        "type": "postgresql",
        "config": {"host": "localhost", "database": "mydb"},
        "table_name": "users"
    }
    Returns: Loaded table metadata
    """
    data = request.json  # Parse JSON body
    
    # Validate input
    if not data.get('workspace_id'):
        raise AppError(ErrorCode.INVALID_REQUEST, "workspace_id required")
    if not data.get('type'):
        raise AppError(ErrorCode.INVALID_REQUEST, "type required")
    
    workspace_id = data['workspace_id']
    connector_type = data['type']
    
    try:
        # 1. Load workspace
        workspace = load_workspace(workspace_id)
        
        # 2. Get data connector
        connector = get_connector(connector_type)
        
        # 3. Validate credentials
        connector.validate_config(data['config'])
        
        # 4. Load data
        df = connector.load(data['table_name'], data['config'])
        
        # 5. Infer semantic types (ID, Measure, Date, etc.)
        semantic_types = infer_types(df)
        
        # 6. Save to workspace
        table = workspace.add_table(
            data['table_name'],
            df,
            semantic_types
        )
        workspace.save()
        
        # 7. Return success
        return jsonify({
            'id': table.id,
            'name': table.name,
            'rows': len(df),
            'columns': list(df.columns),
            'semantic_types': semantic_types
        }), 201  # HTTP 201 Created
        
    except ValueError as e:
        # Validation error
        raise AppError(ErrorCode.INVALID_REQUEST, str(e))
    except ConnectionError as e:
        # Connection error
        raise AppError(ErrorCode.DATA_LOAD_FAILED, f"Connection failed: {e}")
    except Exception as e:
        # Unexpected error
        raise AppError(ErrorCode.INTERNAL_ERROR, "Failed to load data")
```

**Flask Patterns**:
- `request.json` for JSON body
- Return with status code: `return data, 201`
- Try-except for error handling
- Custom exceptions raise `AppError`

---

## Agent Execution & Streaming

### Key Concept: Server-Sent Events (SSE)

Instead of waiting for the entire operation to complete, stream results back progressively.

```python
from flask import Response, stream_with_context
import json

agent_bp = Blueprint("agent", __name__, url_prefix="/api/agents")

@agent_bp.route("/run", methods=['POST'])
def run_agent():
    """
    POST /api/agents/run
    Body: {"workspace_id": "123", "question": "Show sales by region"}
    
    Returns: SSE stream of events
    
    Client receives:
    data: {"type":"init","message":"Analyzing..."}
    data: {"type":"message","chunk":"I found that..."}
    data: {"type":"action","step":"Creating chart"}
    data: {"type":"complete","result":{...}}
    """
    
    data = request.json
    workspace_id = data['workspace_id']
    question = data['question']
    
    def generate_events():
        """
        Generator function that yields events.
        Flask calls this to stream responses.
        """
        try:
            # 1. Load workspace
            workspace = load_workspace(workspace_id)
            
            # 2. Create agent
            agent = AnalystAgent(workspace)
            
            # 3. Stream events from agent
            for event in agent.run(question):
                # Convert event to JSON
                json_str = json.dumps(event)
                
                # SSE format: data: {json}\n\n
                yield f"data: {json_str}\n\n"
                
                # Flush to browser immediately
                import sys
                sys.stdout.flush()
                
        except AppError as e:
            # Send error as event
            error_event = {
                'type': 'error',
                'code': e.code.name,
                'message': e.message
            }
            yield f"data: {json.dumps(error_event)}\n\n"
    
    # Return SSE stream
    return Response(
        stream_with_context(generate_events()),
        mimetype='text/event-stream',  # Critical!
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'  # Don't buffer (for nginx/apache)
        }
    )
```

**How the client receives the stream**:

```javascript
// Frontend (JavaScript)
const response = await fetch('/api/agents/run', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ workspace_id: '123', question: '...' })
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
            // Update UI with event
            dispatch(agentEvent(event));
        }
    }
}
```

**Flask Patterns**:
- `Response()` for custom HTTP responses
- `stream_with_context()` for streaming
- `mimetype='text/event-stream'` for SSE
- Generator function yields data progressively

---

## Error Handling

### Global Error Handler (from `error_handler.py`)

**Concept**: Catch all errors and return consistent response format

```python
from flask import jsonify, g
from data_formulator.errors import AppError, ErrorCode

def register_error_handlers(app):
    """Register error handlers with the Flask app."""
    
    # Handle AppError (custom exceptions)
    @app.errorhandler(AppError)
    def handle_app_error(error):
        """Handle application-specific errors."""
        
        # Create response envelope
        response = {
            'success': False,
            'error': {
                'code': error.code.name,          # e.g., "WORKSPACE_NOT_FOUND"
                'message': error.message,         # e.g., "Workspace not found"
                'request_id': g.get('request_id')  # For support debugging
            }
        }
        
        # Log the error
        app.logger.warning(f"App error: {error.code.name}: {error.message}")
        
        # Return JSON response with HTTP 200 (always!)
        return jsonify(response), 200
    
    # Handle unexpected exceptions
    @app.errorhandler(Exception)
    def handle_unexpected(error):
        """Handle all other exceptions."""
        
        # Don't expose details to user
        response = {
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An unexpected error occurred',
                'request_id': g.get('request_id')
            }
        }
        
        # Log full error for debugging
        app.logger.error(f"Unexpected error: {error}", exc_info=True)
        
        # Return HTTP 200 (consistent with success responses)
        return jsonify(response), 200
    
    # Handle HTTP errors (404, 500, etc.)
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': 'Endpoint not found'
            }
        }), 200
```

**Why always HTTP 200?**
- Easier client parsing (all responses are JSON)
- HTTP status doesn't indicate success (avoid race conditions)
- Error info is in the JSON envelope
- Proxies/load balancers don't retry on 200

### Using AppError in Routes

```python
@app.route('/api/data')
def get_data():
    workspace_id = request.args.get('workspace_id')
    
    # Raise AppError - will be caught by error handler
    if not workspace_id:
        raise AppError(
            ErrorCode.INVALID_REQUEST,
            "workspace_id query parameter required"
        )
    
    try:
        workspace = load_workspace(workspace_id)
    except FileNotFoundError:
        raise AppError(
            ErrorCode.WORKSPACE_NOT_FOUND,
            f"Workspace '{workspace_id}' not found"
        )
    
    # Success path
    return jsonify({'workspace': workspace})
```

**Flask Pattern**: Middleware catches all errors and handles consistently

---

## Session Management

### Server-Side Sessions (from `app.py`)

**Concept**: Store sensitive data on server, send only session ID to browser

```python
from flask_session import Session
from cachelib import FileSystemCache

# Configure server-side session storage
app.config['SESSION_TYPE'] = 'cachelib'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'df_session:'
app.config['SESSION_CACHELIB'] = FileSystemCache(
    cache_dir=_session_dir,  # ~/.data_formulator/sessions
    threshold=500             # Keep 500 most recent sessions
)

# Initialize session extension
Session(app)
```

**Browser sees** (secure cookie):
```
Set-Cookie: session=abc123def456; HttpOnly; SameSite=Lax
```

**Server stores** (filesystem):
```
~/.data_formulator/sessions/df_session:abc123def456
{
    "access_token": "...",
    "refresh_token": "...",
    "user_id": 123
}
```

### Storing Data in Session

```python
@app.route('/login', methods=['POST'])
def login():
    # Authenticate user
    user = authenticate(request.json)
    
    # Store in session (server-side)
    session['user_id'] = user.id
    session['username'] = user.username
    session['access_token'] = user.access_token
    session['refresh_token'] = user.refresh_token
    session.permanent = True  # Persist across browser close
    
    return {'status': 'logged in'}

@app.route('/profile')
def profile():
    # Access from session (retrieved from server)
    user_id = session.get('user_id')
    if not user_id:
        return {'error': 'Not logged in'}, 401
    
    user = get_user(user_id)
    return {'user': user}

@app.route('/logout')
def logout():
    # Clear session
    session.clear()
    return {'status': 'logged out'}
```

**Security Benefits**:
- Tokens never exposed to JavaScript (HttpOnly flag)
- Tokens never in browser storage
- Server can revoke anytime
- Works across tabs/devices automatically

---

## Middleware & Request Lifecycle

### Request ID Middleware (for logging)

**From `error_handler.py`**

```python
from flask import g
import uuid

def register_error_handlers(app):
    """Includes request ID middleware."""
    
    @app.before_request
    def before_request():
        """Run before each request."""
        
        # Generate unique request ID
        request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
        g.request_id = request_id
        
        # Add to all responses
        g.request_id = request_id
        
        # Log request
        app.logger.debug(
            f"[{request_id}] {request.method} {request.path} "
            f"from {request.remote_addr}"
        )
    
    @app.after_request
    def after_request(response):
        """Run after each request."""
        
        # Add request ID to response headers
        response.headers['X-Request-ID'] = g.get('request_id', '')
        
        # Log response
        app.logger.debug(
            f"[{g.get('request_id')}] Response: {response.status_code}"
        )
        
        return response
```

**Usage in logging**:
```
[550e8400-e29b-41d4-a716-446655440000] GET /api/tables from 192.168.1.1
[550e8400-e29b-41d4-a716-446655440000] Response: 200
```

### Authentication Middleware

```python
@app.before_request
def check_authentication():
    """Check if user is authenticated before protected routes."""
    
    # Skip auth for public routes
    if request.path.startswith('/auth/'):
        return
    if request.path.startswith('/health'):
        return
    
    # Check session
    user_id = session.get('user_id')
    if not user_id:
        raise AppError(ErrorCode.AUTH_REQUIRED, "Please log in")
    
    # Store user in g for this request
    g.user_id = user_id
    g.user = get_user(user_id)
```

### Timing Middleware

```python
import time

@app.before_request
def start_timer():
    g.start_time = time.time()

@app.after_request
def log_timing(response):
    elapsed = time.time() - g.start_time
    
    # Add to response header
    response.headers['X-Process-Time'] = f"{elapsed:.2f}s"
    
    # Log slow requests
    if elapsed > 5.0:
        app.logger.warning(
            f"Slow request: {request.method} {request.path} "
            f"took {elapsed:.2f}s"
        )
    
    return response
```

---

## Summary: Flask in Data Formulator

| Concept | Usage | Example |
|---------|-------|---------|
| **Blueprints** | Organize routes by feature | auth, tables, agents, sessions |
| **Request Handling** | Parse input data | `request.json`, `request.args` |
| **Response** | Return data | `jsonify({'data': ...})` |
| **Status Codes** | Indicate result | 200, 201, 400, 401, 500 |
| **Sessions** | Server-side storage | OAuth tokens, user info |
| **Middleware** | Pre/post request logic | Auth checks, logging, timing |
| **Streaming** | Progressive responses | Agent execution via SSE |
| **Error Handling** | Consistent errors | AppError → global handler → JSON |
| **Configuration** | Environment settings | `app.config['KEY'] = value` |

---

## Next: Trace a Real Request

Try following this request through the code:

1. **User clicks "Load PostgreSQL data"**
2. **Frontend sends**: `POST /api/tables` with PostgreSQL credentials
3. **Flask routes to**: `tables_bp.create_table()` in `routes/tables.py`
4. **Handler**:
   - Validates input
   - Gets PostgreSQL connector
   - Loads data
   - Infers semantic types
   - Saves to workspace
   - Returns table metadata
5. **Error handler catches any exceptions** and returns consistent error JSON
6. **Frontend receives response** and updates Redux state
7. **UI re-renders** with new table

**Files to read**:
- `py-src/data_formulator/app.py` - App setup
- `py-src/data_formulator/routes/tables.py` - Table routes
- `py-src/data_formulator/data_connector.py` - Connector abstraction
- `py-src/data_formulator/error_handler.py` - Error handling

---

Now you understand how Flask powers data-formulator! 🚀
