# Flask Fundamentals: A Guide for Data Formulator Developers

**Learn Flask core concepts using real examples from the data-formulator codebase**

---

## Table of Contents

1. [What is Flask?](#what-is-flask)
2. [Installation & Quick Start](#installation--quick-start)
3. [Core Flask Concepts](#core-flask-concepts)
4. [Routing & URL Handling](#routing--url-handling)
5. [Request & Response Handling](#request--response-handling)
6. [Blueprints (Modular Organization)](#blueprints-modular-organization)
7. [Session & Cookies](#session--cookies)
8. [Configuration & Environment](#configuration--environment)
9. [Error Handling](#error-handling)
10. [Middleware & Request Lifecycle](#middleware--request-lifecycle)
11. [Data Formulator's Flask Architecture](#data-formulator-flask-architecture)
12. [Practical Examples from the Codebase](#practical-examples-from-the-codebase)

---

## What is Flask?

### Definition
Flask is a **lightweight web framework** for Python that helps you build web applications and APIs. It's a **microframework**, meaning it provides just the essentials and lets you add libraries as needed.

### Key Characteristics
- **Minimal**: Start with just 20 lines to run a web server
- **Flexible**: Build anything from simple APIs to complex applications
- **Pythonic**: Uses Python idioms and is easy to learn
- **Extensible**: Add functionality through extensions (packages)

### Common Use Cases
- **REST APIs** (what data-formulator uses)
- **Web applications**
- **Microservices**
- **Backend servers for frontend apps**

### Data Formulator's Usage
Data-formulator uses Flask to:
- Serve REST API endpoints for frontend requests
- Stream AI agent responses via Server-Sent Events (SSE)
- Handle user authentication (OAuth, OIDC)
- Manage sessions and data persistence

---

## Installation & Quick Start

### Install Flask

```bash
# Using pip
pip install flask

# Using uv (recommended in data-formulator)
uv pip install flask
```

### Simplest Flask App

```python
# app.py
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)
```

**Run it**:
```bash
python app.py
# Server runs on http://localhost:5000
```

**What happens**:
1. `Flask(__name__)` creates the application
2. `@app.route('/')` registers a URL handler
3. When user visits `/`, Flask calls `hello()` and returns the result
4. `app.run()` starts the web server

---

## Core Flask Concepts

### 1. The Flask Application Object

```python
from flask import Flask

# Create the Flask app
app = Flask(__name__)
```

**What is `__name__`?**
- It's the module's name (usually `'__main__'` when run directly)
- Flask uses it to find resources (templates, static files)

### 2. Routing: Mapping URLs to Functions

```python
# Simple route
@app.route('/')
def home():
    return 'Welcome!'

# Route with parameter
@app.route('/user/<name>')
def greet(name):
    return f'Hello, {name}!'

# Route with variable type
@app.route('/post/<int:post_id>')
def get_post(post_id):
    return f'Post {post_id}'
```

**How it works**:
1. User visits URL (e.g., `/user/Alice`)
2. Flask matches URL against registered routes
3. Extracts parameters from URL
4. Calls the function with parameters
5. Returns the result to browser

### 3. Request Object

Flask provides access to the incoming HTTP request:

```python
from flask import Flask, request

@app.route('/submit', methods=['POST'])
def submit():
    # Get JSON data from request body
    data = request.json  # {'name': 'Alice'}
    
    # Get query parameters
    page = request.args.get('page', '1')  # ?page=2
    
    # Get form data
    username = request.form.get('username')
    
    # Get headers
    token = request.headers.get('Authorization')
    
    return {'message': 'Received!'}
```

**Common Request Attributes**:
- `request.method` → 'GET', 'POST', 'PUT', 'DELETE'
- `request.json` → Parsed JSON body
- `request.args` → Query parameters (?key=value)
- `request.form` → Form data (from HTML forms)
- `request.headers` → HTTP headers
- `request.cookies` → Cookies from browser
- `request.remote_addr` → Client IP address

### 4. Response Object

Flask returns data to the client:

```python
from flask import Flask, jsonify

@app.route('/api/user')
def get_user():
    # Return JSON
    return jsonify({'id': 1, 'name': 'Alice'})

@app.route('/api/data')
def get_data():
    # Return with custom status code
    return jsonify({'data': [1, 2, 3]}), 201

@app.route('/custom')
def custom_response():
    # Return raw text
    return 'Plain text response'
```

**Common Return Patterns**:
- `return dict` → Converted to JSON
- `return jsonify(dict)` → Explicit JSON
- `return str` → Plain text
- `return data, status_code` → With HTTP status
- `return data, status_code, headers` → With headers

### 5. HTTP Methods

```python
from flask import request

@app.route('/api/item', methods=['GET', 'POST'])
def handle_item():
    if request.method == 'GET':
        # Retrieve items
        return {'items': [...]}
    elif request.method == 'POST':
        # Create new item
        data = request.json
        return {'id': 1, 'status': 'created'}, 201
```

**Standard HTTP Methods**:
- `GET` → Retrieve data (safe, no side effects)
- `POST` → Create new data
- `PUT` → Update existing data
- `DELETE` → Delete data
- `PATCH` → Partial update

---

## Routing & URL Handling

### Static Routes

```python
@app.route('/')              # Root
@app.route('/about')         # Static URL
@app.route('/api/tables')    # API endpoint
def handler():
    return 'response'
```

### Dynamic Routes (URL Parameters)

```python
@app.route('/user/<name>')
def user(name):
    return f'User: {name}'
    # /user/alice → name='alice'

@app.route('/post/<int:post_id>')
def post(post_id):
    return f'Post ID: {post_id}'
    # /post/42 → post_id=42

@app.route('/file/<path:filepath>')
def file(filepath):
    return f'File: {filepath}'
    # /file/docs/readme.md → filepath='docs/readme.md'
```

**Converters**:
- `<string:name>` → Text (default)
- `<int:id>` → Integer
- `<float:value>` → Decimal number
- `<path:filepath>` → Path with slashes
- `<uuid:id>` → UUID

### URL Building

```python
from flask import url_for

# Generate URL for a route
@app.route('/dashboard')
def dashboard():
    # Build URLs dynamically
    user_url = url_for('user', name='alice')  # /user/alice
    post_url = url_for('post', post_id=42)    # /post/42
    return f'Links: {user_url}, {post_url}'
```

**Why use `url_for()`?**
- Changes in routes don't break links
- Automatic URL encoding
- Works with parameters

---

## Request & Response Handling

### Getting Request Data

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/user', methods=['POST'])
def create_user():
    # Method 1: JSON body
    data = request.json
    name = data.get('name')
    email = data.get('email')
    
    # Method 2: Query parameters
    page = request.args.get('page', default=1, type=int)
    
    # Method 3: Form data
    password = request.form.get('password')
    
    # Method 4: Custom headers
    auth_token = request.headers.get('Authorization')
    
    # Method 5: Cookies
    session_id = request.cookies.get('session_id')
    
    return jsonify({'status': 'ok'})
```

### Sending Responses

```python
from flask import jsonify, send_file, make_response

# JSON response
@app.route('/json')
def json_response():
    return jsonify({'key': 'value'})

# Status code
@app.route('/created', methods=['POST'])
def created():
    return jsonify({'id': 1}), 201  # Created

# With headers
@app.route('/custom')
def custom():
    resp = make_response(jsonify({'data': [1,2,3]}))
    resp.headers['X-Custom'] = 'value'
    return resp

# File download
@app.route('/download')
def download():
    return send_file('file.csv', as_attachment=True)

# Streaming large responses
@app.route('/stream')
def stream():
    def generate():
        for i in range(1000):
            yield f'data: {i}\n'
    return generate(), {'Content-Type': 'text/event-stream'}
```

### Error Responses

```python
from flask import abort

@app.route('/user/<int:user_id>')
def get_user(user_id):
    if user_id < 1:
        abort(400)  # Bad Request
    
    if user_id == 999:
        abort(404)  # Not Found
    
    if not has_permission():
        abort(403)  # Forbidden
    
    return {'id': user_id, 'name': 'Alice'}
```

**Common Status Codes**:
- `200` → OK
- `201` → Created
- `400` → Bad Request
- `401` → Unauthorized
- `403` → Forbidden
- `404` → Not Found
- `500` → Server Error

---

## Blueprints (Modular Organization)

### What are Blueprints?

Blueprints allow you to organize routes into modular groups. Instead of putting all routes in one file, you split them by feature.

### Why Use Blueprints?

```
Without Blueprints (Bad for large apps):
─── app.py (5000 lines of routes)  ❌ Hard to maintain

With Blueprints (Good for large apps):
─── auth/
    ├── __init__.py
    └── routes.py       (Login, logout, etc.)
─── users/
    ├── __init__.py
    └── routes.py       (Create user, get profile, etc.)
─── data/
    ├── __init__.py
    └── routes.py       (Load table, query data, etc.)
─── app.py              (Just register blueprints) ✓ Clean!
```

### Creating a Blueprint

**File: `auth/routes.py`**
```python
from flask import Blueprint, request, jsonify

# Create a blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    credentials = request.json
    # Validate credentials
    return jsonify({'token': 'abc123'})

@auth_bp.route('/logout', methods=['POST'])
def logout():
    # Clear session
    return jsonify({'status': 'logged out'})

@auth_bp.route('/me')
def get_me():
    # Return current user
    return jsonify({'id': 1, 'name': 'Alice'})
```

**File: `users/routes.py`**
```python
from flask import Blueprint, request, jsonify

users_bp = Blueprint('users', __name__, url_prefix='/api/users')

@users_bp.route('', methods=['POST'])
def create_user():
    data = request.json
    # Create user
    return jsonify({'id': 1}), 201

@users_bp.route('/<int:user_id>')
def get_user(user_id):
    # Fetch user
    return jsonify({'id': user_id, 'name': 'Alice'})

@users_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    # Update user
    return jsonify({'id': user_id})
```

### Registering Blueprints

**File: `app.py`**
```python
from flask import Flask
from auth.routes import auth_bp
from users.routes import users_bp

app = Flask(__name__)

# Register blueprints
app.register_blueprint(auth_bp)      # Routes start with /api/auth
app.register_blueprint(users_bp)     # Routes start with /api/users

if __name__ == '__main__':
    app.run()
```

**Available Routes**:
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/me`
- `POST /api/users`
- `GET /api/users/1`
- `PUT /api/users/1`

### Blueprint Features

```python
from flask import Blueprint

# Create with URL prefix
tables_bp = Blueprint(
    'tables',                    # Name (used in url_for)
    __name__,                    # Module
    url_prefix='/api/tables',    # All routes start with this
    static_folder='static',      # Static files directory
    static_url_path='/static'    # URL path for static files
)

@tables_bp.route('/')
def list_tables():
    return {}

# Full URL: /api/tables/
```

---

## Session & Cookies

### Sessions (Server-Side Storage)

Sessions let you store user-specific data on the server:

```python
from flask import Flask, session, request, jsonify

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Required for sessions

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    # Validate credentials
    session['user_id'] = 123        # Store in session
    session['username'] = 'alice'
    return jsonify({'status': 'logged in'})

@app.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return {'error': 'Not logged in'}, 401
    
    return {'user_id': user_id}

@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    return {'status': 'logged out'}
```

**How it works**:
1. User logs in
2. Server stores data in `session` dictionary
3. Server creates a session ID
4. Session ID sent to browser as cookie
5. Browser sends cookie with each request
6. Server retrieves session data using cookie

### Cookies (Browser-Side Storage)

Cookies store small data on the browser:

```python
from flask import request, make_response

@app.route('/set-cookie')
def set_cookie():
    resp = make_response({'message': 'Cookie set'})
    resp.set_cookie(
        'my_cookie',
        value='abc123',
        max_age=3600,           # Expires in 1 hour
        secure=True,            # Only send over HTTPS
        httponly=True,          # Not accessible from JavaScript
        samesite='Lax'          # CSRF protection
    )
    return resp

@app.route('/read-cookie')
def read_cookie():
    value = request.cookies.get('my_cookie')
    return {'cookie_value': value}

@app.route('/delete-cookie')
def delete_cookie():
    resp = make_response({'message': 'Cookie deleted'})
    resp.delete_cookie('my_cookie')
    return resp
```

### Data Formulator's Session Usage

Data-formulator uses **server-side sessions** to store SSO tokens:

```python
# From auth/gateways/oidc_gateway.py
@oidc_bp.route("/login")
def oidc_login():
    state = secrets.token_urlsafe(32)
    session["_oauth_state"] = state  # Store in session
    
    # Redirect to OAuth provider
    return redirect(authorize_url)
```

---

## Configuration & Environment

### Application Configuration

```python
from flask import Flask

app = Flask(__name__)

# Configuration methods

# Method 1: Direct assignment
app.config['DEBUG'] = True
app.config['JSON_SORT_KEYS'] = False

# Method 2: Dictionary update
app.config.update(
    DEBUG=True,
    TESTING=False,
    SECRET_KEY='dev-key'
)

# Method 3: From object
class Config:
    DEBUG = True
    PERMANENT_SESSION_LIFETIME = 3600

app.config.from_object(Config)
```

### Environment Variables

```python
import os
from dotenv import load_dotenv

# Load from .env file
load_dotenv()

# Read variables
DATABASE_URL = os.environ.get('DATABASE_URL')
API_KEY = os.environ.get('API_KEY')
DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'
```

### Data Formulator's Configuration

From `app.py`:
```python
# Load environment early
load_dotenv(os.path.join(APP_ROOT, '.env'))

# Create app with config
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(16)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 MB
app.config['PERMANENT_SESSION_LIFETIME'] = 60 * 60 * 24 * 365
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Store CLI arguments
app.config['CLI_ARGS'] = {
    'host': os.environ.get('HOST', '127.0.0.1'),
    'sandbox': os.environ.get('SANDBOX', 'local'),
    'max_display_rows': int(os.environ.get('MAX_DISPLAY_ROWS', '10000')),
}
```

---

## Error Handling

### Global Error Handlers

```python
from flask import Flask, jsonify

app = Flask(__name__)

# Handle specific exceptions
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Handle custom exceptions
class CustomError(Exception):
    pass

@app.errorhandler(CustomError)
def handle_custom_error(error):
    return jsonify({'error': str(error)}), 400
```

### Try-Except Pattern

```python
@app.route('/api/query', methods=['POST'])
def run_query():
    try:
        data = request.json
        result = execute_query(data)
        return jsonify({'result': result})
    except ValueError as e:
        return jsonify({'error': f'Invalid input: {e}'}), 400
    except DatabaseError as e:
        return jsonify({'error': f'Database error: {e}'}), 500
    except Exception as e:
        return jsonify({'error': 'Unexpected error'}), 500
```

### Data Formulator's Error Pattern

From `error_handler.py`:

```python
from data_formulator.errors import AppError, ErrorCode

# Unified error response
def json_ok(data):
    """Build a success response with envelope."""
    return {'success': True, 'data': data}

# Error response
def error_response(code, message):
    """Build an error response."""
    return {
        'success': False,
        'error': {
            'code': code,
            'message': message,
            'details': '...'
        }
    }

# Usage
@app.route('/api/load-data', methods=['POST'])
def load_data():
    try:
        # Do work
        result = load_data_from_source(...)
        return json_ok({'table': result})
    except Exception as e:
        error = classify_and_wrap_llm_error(e)
        return error_response(error.code, error.message), 200
```

**Key Point**: Data-formulator always returns **HTTP 200**, even for errors! The error is in the JSON envelope.

---

## Middleware & Request Lifecycle

### What is Middleware?

Middleware runs **before or after** each request to modify behavior:

```
Request → Middleware 1 → Middleware 2 → Route Handler → Middleware 2 → Middleware 1 → Response
```

### Common Middleware

```python
from flask import Flask, request, g
import uuid
import time

app = Flask(__name__)

# 1. Request ID Middleware (for logging)
@app.before_request
def add_request_id():
    g.request_id = str(uuid.uuid4())
    print(f"Request: {g.request_id} {request.method} {request.path}")

# 2. Timing Middleware
@app.before_request
def start_timer():
    g.start_time = time.time()

@app.after_request
def log_duration(response):
    duration = time.time() - g.start_time
    print(f"Completed in {duration:.2f}s")
    return response

# 3. Authentication Middleware
@app.before_request
def check_auth():
    if request.path.startswith('/api/protected'):
        token = request.headers.get('Authorization')
        if not token:
            return {'error': 'Unauthorized'}, 401

# 4. CORS Middleware
from flask_cors import CORS
CORS(app)
```

### Decorators for Specific Routes

```python
from functools import wraps
from flask import request

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return {'error': 'No auth'}, 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/protected')
@require_auth
def protected():
    return {'message': 'Secret data'}
```

### Request Context (`g` Object)

```python
from flask import g

@app.before_request
def load_user():
    # Store user info for this request only
    g.user_id = get_user_from_token()
    g.user = fetch_user(g.user_id)

@app.route('/api/profile')
def profile():
    # Access user from any function in this request
    return {'user': g.user.name}
```

---

## Data Formulator's Flask Architecture

### 1. Application Initialization (`app.py`)

```python
# From app.py
from flask import Flask

# Create Flask app
app = Flask(__name__, static_url_path='', static_folder=...)

# Configure
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 MB
app.config['SESSION_TYPE'] = 'cachelib'  # Server-side sessions

# Setup error handlers
register_error_handlers(app)

# Register blueprints (lazy-loaded)
_register_blueprints()
```

### 2. Blueprint Registration

```python
# From app.py
def _register_blueprints():
    # Auth blueprints
    from data_formulator.auth.gateways.oidc_gateway import oidc_bp
    app.register_blueprint(oidc_bp)  # /api/auth/oidc/*
    
    # Data blueprints
    from data_formulator.routes.tables import tables_bp
    app.register_blueprint(tables_bp)  # /api/tables/*
    
    # Agent blueprints
    from data_formulator.routes.agents import agent_bp
    app.register_blueprint(agent_bp)  # /api/agents/*
```

### 3. Route Structure

```
/api/
├── /auth/          (Authentication)
│   ├── /login
│   ├── /logout
│   └── /callback
├── /tables/        (Data operations)
│   ├── GET  /      (List tables)
│   ├── POST /      (Create table)
│   └── GET  /:id   (Get table)
├── /agents/        (AI agents)
│   ├── POST /run   (Execute agent)
│   └── GET  /run   (SSE stream)
└── /sessions/      (Workspace sessions)
    ├── GET  /
    └── POST /
```

### 4. Request Flow for Agent Execution

```
1. Frontend sends: POST /api/agents/run
   {
     "workspace_id": "123",
     "question": "Show me sales by region"
   }

2. Backend route handler (agent_bp.py):
   @agent_bp.route('/run', methods=['POST'])
   def run_agent():
       # Parse request
       data = request.json
       
       # Load workspace
       workspace = load_workspace(data['workspace_id'])
       
       # Initialize agent
       agent = AnalystAgent()
       
       # Stream response
       def generate():
           for event in agent.run(...):
               yield f"data: {json.dumps(event)}\n"
       
       return Response(
           stream_with_context(generate()),
           mimetype='text/event-stream'
       )

3. Frontend receives SSE stream:
   data: {"type":"init","message":"Analyzing"}
   data: {"type":"message","chunk":"I found..."}
   data: {"type":"action","step":"Visualizing"}
   data: {"type":"complete","result":{...}}
```

---

## Practical Examples from the Codebase

### Example 1: Authentication Route (OIDC)

**File: `auth/gateways/oidc_gateway.py`**

```python
from flask import Blueprint, request, session, redirect
import secrets

# Create blueprint
oidc_bp = Blueprint("oidc_gateway", __name__, url_prefix="/api/auth/oidc")

# Route 1: Login (redirects to OAuth provider)
@oidc_bp.route("/login")
def oidc_login():
    """Redirect user to SSO authorization page."""
    cfg = _get_oidc_config()
    authorize_url = cfg.get("authorize_url", "")
    
    # Generate random state for CSRF protection
    state = secrets.token_urlsafe(32)
    session["_oauth_state"] = state
    
    # Redirect to OAuth provider
    params = {
        "response_type": "code",
        "client_id": cfg.get("client_id"),
        "redirect_uri": _callback_url(),
        "scope": "openid profile email",
        "state": state,
    }
    
    return redirect(f"{authorize_url}?{urlencode(params)}")

# Route 2: Callback (handles OAuth response)
@oidc_callback_bp.route("/auth/callback")
def oidc_callback():
    """Handle OAuth provider response."""
    # Get authorization code from URL
    code = request.args.get("code")
    state = request.args.get("state")
    
    # Verify state (CSRF protection)
    if state != session.get("_oauth_state"):
        raise AppError(ErrorCode.INVALID_REQUEST, "State mismatch")
    
    # Exchange code for tokens
    tokens = exchange_code_for_tokens(code)
    
    # Store tokens in session (secure, server-side)
    session["access_token"] = tokens["access_token"]
    session["refresh_token"] = tokens["refresh_token"]
    
    # Redirect to app
    return redirect("/")
```

### Example 2: Data Loading Route

**Simplified from `routes/tables.py`**

```python
from flask import Blueprint, request, jsonify
from data_formulator.errors import AppError, ErrorCode

tables_bp = Blueprint("tables", __name__, url_prefix="/api/tables")

@tables_bp.route("/", methods=['GET'])
def list_tables():
    """List tables in current workspace."""
    workspace_id = request.args.get('workspace_id')
    
    try:
        # Load workspace
        workspace = load_workspace(workspace_id)
        
        # Return table metadata
        tables = [
            {
                'id': t.id,
                'name': t.name,
                'rows': len(t),
                'columns': list(t.columns)
            }
            for t in workspace.tables
        ]
        
        return jsonify({'tables': tables})
    except FileNotFoundError:
        raise AppError(
            ErrorCode.WORKSPACE_NOT_FOUND,
            f"Workspace {workspace_id} not found"
        )

@tables_bp.route("/", methods=['POST'])
def create_table():
    """Load external data into workspace."""
    data = request.json
    workspace_id = data['workspace_id']
    connector_type = data['type']  # 'postgresql', 's3', etc.
    
    try:
        # Get connector
        connector = get_connector(connector_type)
        
        # Validate configuration
        connector.validate_config(data['config'])
        
        # Load data
        df = connector.load(data['table_name'])
        
        # Save to workspace
        workspace = load_workspace(workspace_id)
        workspace.add_table(data['table_name'], df)
        workspace.save()
        
        return jsonify({
            'id': table.id,
            'rows': len(df),
            'columns': list(df.columns)
        }), 201
    except ValueError as e:
        raise AppError(ErrorCode.INVALID_REQUEST, str(e))
    except Exception as e:
        raise AppError(ErrorCode.DATA_LOAD_FAILED, str(e))
```

### Example 3: Agent Execution (SSE Streaming)

**Simplified from `routes/agents.py`**

```python
from flask import Blueprint, request, Response, stream_with_context
import json

agent_bp = Blueprint("agent", __name__, url_prefix="/api/agents")

@agent_bp.route("/run", methods=['POST'])
def run_agent():
    """Execute agent with streaming response."""
    data = request.json
    workspace_id = data['workspace_id']
    question = data['question']
    
    def generate():
        try:
            # Load workspace
            workspace = load_workspace(workspace_id)
            
            # Initialize agent
            agent = AnalystAgent(workspace)
            
            # Stream agent events
            for event in agent.run(question):
                # Convert to JSON
                json_event = json.dumps(event)
                
                # Send as SSE
                yield f"data: {json_event}\n\n"
                
        except Exception as e:
            # Send error event
            error_event = {
                'type': 'error',
                'code': e.code,
                'message': str(e)
            }
            yield f"data: {json.dumps(error_event)}\n\n"
    
    # Return SSE stream
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )
```

### Example 4: Error Handling Pattern

**From `error_handler.py`**

```python
from flask import jsonify, g
from data_formulator.errors import AppError, ErrorCode

def register_error_handlers(app):
    """Register global error handlers."""
    
    # Handle AppError (custom exceptions)
    @app.errorhandler(AppError)
    def handle_app_error(error):
        response = {
            'success': False,
            'error': {
                'code': error.code.name,
                'message': error.message,
                'request_id': g.get('request_id')
            }
        }
        return jsonify(response), 200  # Always 200!
    
    # Handle unexpected errors
    @app.errorhandler(Exception)
    def handle_unexpected(error):
        # Log the error
        app.logger.error(f"Unexpected error: {error}")
        
        # Create response
        response = {
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An unexpected error occurred',
                'request_id': g.get('request_id')
            }
        }
        return jsonify(response), 200  # Always 200!

# Raise errors like this
@app.route('/api/data')
def get_data():
    workspace_id = request.args.get('workspace_id')
    
    try:
        workspace = load_workspace(workspace_id)
    except FileNotFoundError:
        raise AppError(
            ErrorCode.WORKSPACE_NOT_FOUND,
            f"Workspace '{workspace_id}' not found"
        )
    
    return {'workspace': workspace}
```

---

## Key Flask Concepts for Data Formulator

### 1. Blueprints for Modularity
- Organize routes by feature (auth, data, agents)
- Keep code clean and maintainable

### 2. Request/Response Cycle
- User → HTTP Request → Flask Route → Handler Function → Response → User

### 3. Sessions for State
- Store authentication tokens server-side
- Access via `session` dictionary

### 4. Error Handling
- Use global error handlers for consistency
- Always return proper error responses

### 5. Streaming (SSE)
- Use `Response(stream_with_context(generator()))` for streaming
- Critical for agent response streaming

### 6. Configuration
- Load from environment variables
- Store in `app.config`

### 7. Middleware & Lifecycle
- Request hooks: `@app.before_request`
- Response hooks: `@app.after_request`
- Great for logging, auth, request tracking

---

## Common Patterns in Data Formulator

### Pattern 1: Load Context, Do Work, Return Result

```python
@bp.route('/api/workspace/<id>', methods=['GET'])
def get_workspace(id):
    # 1. Load
    workspace = load_workspace(id)
    
    # 2. Work
    data = prepare_response(workspace)
    
    # 3. Return
    return jsonify(data)
```

### Pattern 2: Validate Input, Call Service, Handle Errors

```python
@bp.route('/api/agent/run', methods=['POST'])
def run_agent():
    try:
        # 1. Validate
        data = request.json
        validate_agent_input(data)
        
        # 2. Call service
        result = execute_agent(data)
        
        # 3. Return
        return json_ok({'result': result})
    except ValueError:
        raise AppError(ErrorCode.INVALID_REQUEST, "...")
    except Exception as e:
        raise AppError(ErrorCode.INTERNAL_ERROR, "...")
```

### Pattern 3: Stream Long-Running Operation

```python
@bp.route('/api/long-operation', methods=['POST'])
def long_operation():
    def generate():
        for status in execute_steps():
            yield f"data: {json.dumps(status)}\n\n"
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream'
    )
```

---

## Next Steps

### Learn More About Flask
1. Read the [official Flask documentation](https://flask.palletsprojects.com/)
2. Follow tutorials on REST API development
3. Study middleware and request lifecycle

### Understand Data Formulator Specifics
1. Read [BACKEND_ARCHITECTURE_GUIDE.md](BACKEND_ARCHITECTURE_GUIDE.md)
2. Study the blueprint files: `py-src/data_formulator/routes/`
3. Trace a request through the code:
   - Frontend sends POST `/api/agents/run`
   - Routes to `agent_bp.run_agent()` handler
   - Loads workspace, creates agent
   - Streams response via SSE

### Practice
1. Create a simple Flask app with multiple blueprints
2. Implement error handling
3. Add streaming endpoints
4. Study the data-formulator code and modify a route

---

## Quick Reference

### Flask Essentials

| Concept | Example |
|---------|---------|
| **Create App** | `app = Flask(__name__)` |
| **Route** | `@app.route('/path')` |
| **Request** | `request.json`, `request.args` |
| **Response** | `return jsonify({'key': 'value'})` |
| **Blueprint** | `bp = Blueprint('name', __name__)` |
| **Register** | `app.register_blueprint(bp)` |
| **Session** | `session['key'] = value` |
| **Error** | `abort(404)` or raise custom exception |
| **Middleware** | `@app.before_request` |
| **Streaming** | `Response(generate(), mimetype='text/event-stream')` |

### Data Formulator Patterns

| Pattern | File | Purpose |
|---------|------|---------|
| **Blueprint Setup** | `app.py` | Register all routes |
| **Auth Handler** | `auth/gateways/*.py` | OAuth/OIDC flows |
| **Data Route** | `routes/tables.py` | Data operations |
| **Agent Route** | `routes/agents.py` | LLM execution |
| **Error Handler** | `error_handler.py` | Unified error response |

---

**Conclusion**: Flask is simple at its core. Master these concepts, then explore the data-formulator codebase to see how they're combined to build a production AI application.
