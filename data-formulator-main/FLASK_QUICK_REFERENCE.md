# Flask Quick Reference: Visual Cheat Sheet

A visual guide to Flask concepts with side-by-side comparisons

---

## 1. Flask Application Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│ 1. CREATE APP                                               │
│    app = Flask(__name__)                                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│ 2. CONFIGURE                                                │
│    app.config['DEBUG'] = True                               │
│    app.secret_key = 'secret'                                │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│ 3. DEFINE ROUTES & HANDLERS                                 │
│    @app.route('/') → def home(): return 'Hello'             │
│    @app.route('/user/<name>')  → def greet(name): ...       │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│ 4. RUN SERVER                                               │
│    app.run() or gunicorn app                                │
│    Listening on http://localhost:5000                       │
└────────────────────────────────────────────────────────────┘
```

---

## 2. Request-Response Flow

```
USER's BROWSER                          FLASK SERVER

    │                                       │
    │ 1. User visits: /user/alice           │
    ├──────── HTTP GET ────────────────────→ │
    │                                       │
    │                          2. Flask matches route:
    │                             @app.route('/user/<name>')
    │                                       │
    │                          3. Call handler with name='alice':
    │                             def greet(name):
    │                                 return f'Hello {name}'
    │                                       │
    │ ← ─ ─ ─ HTTP 200 "Hello alice" ─ ─ ─ ┤
    │                                       │
```

---

## 3. HTTP Methods Mapping

```
Method    Purpose        CRUD        Example
─────────────────────────────────────────────────────────────
GET       Retrieve       Read        GET /api/users/1
POST      Create         Create      POST /api/users
PUT       Replace        Update      PUT /api/users/1
PATCH     Partial update Update      PATCH /api/users/1
DELETE    Remove         Delete      DELETE /api/users/1
```

### In Flask

```python
# Flask CRUD Pattern
@app.route('/api/users', methods=['GET'])
def list_users():
    return {'users': [...]}  # GET

@app.route('/api/users', methods=['POST'])
def create_user():
    return {'id': 1}, 201    # POST

@app.route('/api/users/<id>', methods=['GET'])
def get_user(id):
    return {'id': id}        # GET

@app.route('/api/users/<id>', methods=['PUT'])
def update_user(id):
    return {'id': id}        # PUT

@app.route('/api/users/<id>', methods=['DELETE'])
def delete_user(id):
    return {}, 204           # DELETE
```

---

## 4. Request Data Sources

```
Incoming Request
    │
    ├─ Query String: ?key=value ────→ request.args.get('key')
    │
    ├─ Path Parameter: /user/42 ────→ def route(id): ...
    │
    ├─ JSON Body: {"name":"Alice"} ─→ request.json.get('name')
    │
    ├─ Form Data: name=Alice ───────→ request.form.get('name')
    │
    ├─ Headers: Authorization: ... → request.headers.get('Authorization')
    │
    └─ Cookies: session=xyz... ─────→ request.cookies.get('session')
```

### Quick Examples

```python
# GET /api/users?page=2&limit=10
page = request.args.get('page', default=1, type=int)      # 2
limit = request.args.get('limit', default=10, type=int)   # 10

# POST /api/users with JSON body {"name":"Alice","email":"alice@..."}
data = request.json
name = data['name']                    # 'Alice'

# GET /user/42
@app.route('/user/<int:id>')
def get_user(id):                      # id = 42 (integer)
    return {'id': id}

# GET /files/docs/readme.txt
@app.route('/files/<path:filepath>')
def get_file(filepath):                # filepath = 'docs/readme.txt'
    return send_file(filepath)
```

---

## 5. Response Types

```
┌─────────────────────┬──────────────────────┬─────────────────┐
│ Response Type       │ Code                 │ Content-Type    │
├─────────────────────┼──────────────────────┼─────────────────┤
│ JSON                │ return jsonify(dict) │ application/json│
│ Plain Text          │ return "text"        │ text/plain      │
│ HTML                │ return "<html>...</html>"               │
│ File Download       │ return send_file()   │ (varies)        │
│ Streaming           │ return Response()    │ text/event-stream│
│ Redirect            │ return redirect()    │ (redirect)      │
└─────────────────────┴──────────────────────┴─────────────────┘
```

### With Status Codes

```python
return data, 200                    # OK
return data, 201                    # Created
return data, 204                    # No Content
return data, 400                    # Bad Request
return data, 401                    # Unauthorized
return data, 403                    # Forbidden
return data, 404                    # Not Found
return data, 500                    # Server Error
```

---

## 6. Blueprints (Organization)

### Without Blueprints (Bad)
```
app.py (3000+ lines)  ❌
├── @app.route('/auth/login')
├── @app.route('/auth/logout')
├── @app.route('/users')
├── @app.route('/posts')
├── @app.route('/comments')
└── ...all mixed together
```

### With Blueprints (Good)
```
app.py (just registration)  ✓
│
├── auth/
│   └── routes.py ← @auth_bp.route('/login'), ('/logout')
│
├── users/
│   └── routes.py ← @users_bp.route(''), ('/profile')
│
└── posts/
    └── routes.py ← @posts_bp.route(''), ('/search')
```

### Creating & Using

```python
# 1. Create blueprint (auth/routes.py)
from flask import Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    return {'token': 'xyz'}

# 2. Register blueprint (app.py)
from auth.routes import auth_bp
app.register_blueprint(auth_bp)

# Result: Endpoint is /api/auth/login
```

---

## 7. Stateful Communication Patterns

### Pattern 1: Simple Request-Response

```
Browser                    Server
  │
  ├─ POST /api/login ──────→ ├─ Parse credentials
  │   {user, password}      ├─ Validate
  │                         └─ Return token
  │ ← ─ 200 {token} ─ ─ ─ ─┤
  │
```

### Pattern 2: Server-Sent Events (SSE) Streaming

```
Browser                    Server
  │
  ├─ POST /api/agents/run ──→ ├─ Start long operation
  │  Accept: text/event-stream
  │                         ├─ Send: data: {"type":"init"}
  │ ← ─ ─ ─ ─ data: ─ ─ ─ ─┤
  │                         ├─ Send: data: {"type":"message"}
  │ ← ─ ─ ─ ─ data: ─ ─ ─ ─┤
  │                         ├─ Send: data: {"type":"complete"}
  │ ← ─ ─ ─ ─ data: ─ ─ ─ ─┤
  │                         └─ Close stream
  │
```

---

## 8. Session vs Cookies Comparison

```
┌──────────────────────────────────────────────────────────┐
│                   SESSION                                │
├──────────────────────────────────────────────────────────┤
│ Storage:    Server (memory, database, filesystem)        │
│ Security:   ✓ High (data never sent to client)           │
│ Size:       ✓ Large (no size limit)                      │
│ Speed:      ~ Slower (server lookup needed)              │
│ Use Case:   Storing sensitive data (tokens, user info)   │
│                                                          │
│ Code:       session['key'] = value                       │
│             value = session.get('key')                   │
└──────────────────────────────────────────────────────────┘

                          vs

┌──────────────────────────────────────────────────────────┐
│                   COOKIES                                │
├──────────────────────────────────────────────────────────┤
│ Storage:    Browser (client machine)                     │
│ Security:   ~ Medium (can be read by JavaScript)         │
│ Size:       Limited (~4KB)                               │
│ Speed:      ✓ Fast (data already on client)              │
│ Use Case:   UI preferences, tracking, non-sensitive info │
│                                                          │
│ Code:       resp.set_cookie('key', value)                │
│             value = request.cookies.get('key')           │
└──────────────────────────────────────────────────────────┘
```

---

## 9. Error Handling Patterns

### Pattern 1: Using abort()

```python
from flask import abort

@app.route('/user/<int:id>')
def get_user(id):
    if id < 1:
        abort(400)  # Bad Request
    
    user = find_user(id)
    if not user:
        abort(404)  # Not Found
    
    if not has_permission(user):
        abort(403)  # Forbidden
    
    return user
```

### Pattern 2: Global Error Handler

```python
@app.errorhandler(404)
def not_found(error):
    return {'error': 'Page not found'}, 404

@app.errorhandler(500)
def server_error(error):
    return {'error': 'Server error'}, 500
```

### Pattern 3: Custom Exceptions

```python
class ValidationError(Exception):
    pass

@app.errorhandler(ValidationError)
def handle_validation(error):
    return {'error': str(error)}, 400

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    if not data.get('name'):
        raise ValidationError("Name is required")
    return {'status': 'ok'}
```

---

## 10. Middleware & Request Hooks

```
User Request
    ↓
┌─────────────────────────────┐
│ @app.before_request         │  ← Add request ID, check auth
└─────────────────────────────┘
    ↓
┌─────────────────────────────┐
│ Route Handler               │  ← Do work
└─────────────────────────────┘
    ↓
┌─────────────────────────────┐
│ @app.after_request          │  ← Add headers, log duration
└─────────────────────────────┘
    ↓
Response to User
```

### Example

```python
from flask import g
import time

@app.before_request
def before():
    g.start_time = time.time()
    g.user = get_user_from_token()

@app.route('/api/data')
def handler():
    return g.user.data  # Access g.user

@app.after_request
def after(response):
    elapsed = time.time() - g.start_time
    response.headers['X-Process-Time'] = elapsed
    return response
```

---

## 11. Common Status Codes

```
1xx - Informational
    100 Continue
    101 Switching Protocols

2xx - Success
    200 OK              (request succeeded)
    201 Created         (resource created)
    204 No Content      (success, no data)

3xx - Redirection
    301 Moved Permanently
    302 Found
    304 Not Modified

4xx - Client Error
    400 Bad Request     (invalid input)
    401 Unauthorized    (need login)
    403 Forbidden       (no permission)
    404 Not Found       (doesn't exist)
    429 Too Many Requests

5xx - Server Error
    500 Internal Server Error
    502 Bad Gateway
    503 Service Unavailable
```

---

## 12. Data Formulator Specific Patterns

### Pattern: Always Return 200 with Error Envelope

```python
# ❌ WRONG (return error status)
@app.route('/api/data')
def get_data():
    return {'error': 'Not found'}, 404

# ✓ CORRECT (return 200 with error in body)
@app.route('/api/data')
def get_data():
    return jsonify({
        'success': False,
        'error': {
            'code': 'NOT_FOUND',
            'message': 'Data not found',
            'request_id': request_id
        }
    }), 200
```

### Pattern: Blueprint with SSE Streaming

```python
from flask import Response, stream_with_context
import json

bp = Blueprint('agent', __name__, url_prefix='/api/agents')

@bp.route('/run', methods=['POST'])
def run_agent():
    def generate():
        try:
            for event in execute_agent():
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream'
    )
```

---

## 13. File Structure for Data Formulator Style

```
project/
├── app.py                          # Flask app creation & registration
├── __main__.py                     # Entry point
│
├── routes/                         # API blueprints
│   ├── __init__.py
│   ├── tables.py                   # Tables blueprint
│   ├── agents.py                   # Agents blueprint
│   └── sessions.py                 # Sessions blueprint
│
├── auth/                           # Authentication
│   ├── __init__.py
│   ├── identity.py                 # Provider selection
│   ├── providers/
│   │   ├── oidc.py
│   │   └── github_oauth.py
│   └── gateways/
│       ├── oidc_gateway.py
│       └── github_gateway.py
│
├── errors.py                       # Error codes & exceptions
├── error_handler.py                # Global error handlers
│
├── data_connector.py               # Data source abstraction
├── model_registry.py               # LLM provider registry
│
└── tests/
    ├── test_routes.py
    ├── test_auth.py
    └── test_errors.py
```

---

## 14. Quick Command Reference

```bash
# Development
python app.py                      # Run development server
FLASK_DEBUG=1 python app.py        # With debugger
uv run data_formulator             # Data Formulator specific

# Production
gunicorn app:app                   # With gunicorn
gunicorn -w 4 app:app              # With 4 workers

# Testing
pytest tests/                      # Run tests
pytest tests/test_routes.py -v     # Verbose
pytest --cov                       # With coverage

# Check routes
flask routes                       # List all routes
```

---

## 15. When to Use Each Flask Feature

```
Feature          When to Use              Example
──────────────────────────────────────────────────────────
Routes           Map URLs to handlers     /api/users
Blueprints       Organize large apps      Separate auth, data, agents
Session          Store server-side data   OAuth tokens, user info
Cookies          Small client-side data   UI preferences
Middleware       Pre/post request work    Logging, auth checks
Streaming        Long operations          AI agent execution, file download
Error Handlers   Consistent errors        Unified error responses
```

---

## Debugging Checklist

When your Flask route isn't working:

```
□ Route registered? Check @app.route() or app.register_blueprint()
□ HTTP method correct? @app.route('/path', methods=['POST'])
□ Request data accessible? request.json, request.args, etc.
□ Response format correct? return jsonify(), return dict, or return str
□ Status code right? return data, 200 / 201 / 400 / 500
□ CORS enabled? Use flask_cors.CORS(app)
□ Error handler catching it? Check @app.errorhandler()
□ Middleware interfering? Check @app.before_request, @app.after_request
□ Logs show the request? Check print() or logging
□ Browser cache? Hard refresh (Ctrl+Shift+R)
```

---

**Now you're ready to explore the data-formulator codebase!** 🚀

Start with [FLASK_FUNDAMENTALS_GUIDE.md](FLASK_FUNDAMENTALS_GUIDE.md) for detailed explanations, then reference this cheat sheet while reading the code.
