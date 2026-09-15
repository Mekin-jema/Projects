# Flask Learning Path for Data Formulator

**A structured guide to learning Flask by exploring the data-formulator codebase**

---

## Your Learning Journey

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: FLASK FUNDAMENTALS                                │
│ (1-2 hours)                                                 │
│ What is Flask? Routes, requests, responses, blueprints     │
│ ┌─────────────────────────────────────────────────────────┐
│ │ Read: FLASK_FUNDAMENTALS_GUIDE.md                        │
│ │ Sections: 1-9                                            │
│ │ Focus: Core concepts, simple examples                    │
│ └─────────────────────────────────────────────────────────┘
│ Then: Quick reference with FLASK_QUICK_REFERENCE.md       │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│ PHASE 2: REAL-WORLD PATTERNS                               │
│ (1-2 hours)                                                 │
│ How Flask is used in production code                       │
│ ┌─────────────────────────────────────────────────────────┐
│ │ Read: FLASK_IN_DATAFORMULATOR.md                         │
│ │ Sections: Application setup, Authentication, Streaming  │
│ │ Focus: Real code examples, patterns, architecture       │
│ └─────────────────────────────────────────────────────────┘
│ Study: Actual code in py-src/data_formulator/             │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│ PHASE 3: CODEBASE EXPLORATION                              │
│ (2-4 hours)                                                 │
│ Read source code with Flask knowledge                      │
│ ┌─────────────────────────────────────────────────────────┐
│ │ Files to study:                                          │
│ │ • py-src/data_formulator/app.py                          │
│ │ • py-src/data_formulator/routes/                         │
│ │ • py-src/data_formulator/auth/                           │
│ │ • py-src/data_formulator/error_handler.py                │
│ │ • py-src/data_formulator/data_connector.py               │
│ └─────────────────────────────────────────────────────────┘
│ Reference: BACKEND_ARCHITECTURE_GUIDE.md                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│ PHASE 4: HANDS-ON DEVELOPMENT                              │
│ (Ongoing)                                                   │
│ Modify code, add features, debug issues                    │
│ ┌─────────────────────────────────────────────────────────┐
│ │ Tasks:                                                   │
│ │ • Add a new API endpoint                                 │
│ │ • Trace a request from frontend to backend              │
│ │ • Implement a new data connector                        │
│ │ • Fix a bug in a route handler                          │
│ └─────────────────────────────────────────────────────────┘
│ Reference: COMPREHENSIVE_CODEBASE_GUIDE.md                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Flask Fundamentals (1-2 hours)

### What You'll Learn

1. **What is Flask?**
   - Lightweight web framework
   - Handles HTTP requests/responses
   - Maps URLs to Python functions

2. **Core Concepts**
   - `Flask` app object
   - `@app.route()` decorators
   - `request` object (GET, POST, JSON, headers)
   - Response types (JSON, HTML, files, streaming)

3. **Blueprints**
   - Modular organization
   - `url_prefix` for grouping routes
   - `app.register_blueprint()` to combine

4. **Request/Response Cycle**
   - User sends HTTP request
   - Flask matches route
   - Function executes
   - Response returned

### Study Guide

**Step 1**: Read [FLASK_FUNDAMENTALS_GUIDE.md](FLASK_FUNDAMENTALS_GUIDE.md)
- Sections 1-9: Core concepts with simple examples
- Time: ~1 hour
- Take notes on concepts you don't understand

**Step 2**: Keep [FLASK_QUICK_REFERENCE.md](FLASK_QUICK_REFERENCE.md) open
- Visual cheat sheet for quick lookup
- Use when reading code examples
- Reference HTTP methods, status codes, patterns

**Step 3**: Simple practice exercise

```python
# Create a simple Flask app
from flask import Flask, request, jsonify

app = Flask(__name__)

# Route 1: Simple GET
@app.route('/')
def home():
    return {'message': 'Hello World'}

# Route 2: GET with parameter
@app.route('/greet/<name>')
def greet(name):
    return {'greeting': f'Hello, {name}!'}

# Route 3: POST with JSON
@app.route('/create', methods=['POST'])
def create():
    data = request.json
    return {'created': data}, 201

# Route 4: Query parameter
@app.route('/search')
def search():
    query = request.args.get('q')
    return {'results': [...]}

if __name__ == '__main__':
    app.run(debug=True)
```

Test it:
```bash
# Terminal 1
python app.py

# Terminal 2 - Test endpoints
curl http://localhost:5000/
curl http://localhost:5000/greet/alice
curl -X POST http://localhost:5000/create -d '{"name":"test"}' -H "Content-Type: application/json"
curl "http://localhost:5000/search?q=flask"
```

---

## Phase 2: Real-World Patterns (1-2 hours)

### What You'll Learn

1. **Application Setup**
   - Configuration management
   - Blueprint registration
   - Error handler setup

2. **Authentication**
   - OAuth2/OIDC flows
   - Session management
   - State/CSRF protection

3. **Data Operations**
   - Input validation
   - Database/API calls
   - Response formatting

4. **Streaming**
   - Server-Sent Events (SSE)
   - Progressive responses
   - Generator functions

5. **Error Handling**
   - Global error handlers
   - Custom exceptions
   - Error response format

### Study Guide

**Step 1**: Read [FLASK_IN_DATAFORMULATOR.md](FLASK_IN_DATAFORMULATOR.md)
- Real code from the project
- Understand patterns used in production
- See how concepts combine

**Step 2**: Open side-by-side with actual code

| Section | File to Read | Concept |
|---------|--------------|---------|
| Application Setup | `py-src/data_formulator/app.py` | Creating app, registering blueprints |
| Authentication | `py-src/data_formulator/auth/gateways/oidc_gateway.py` | OAuth flow |
| Data Loading | Search: `load_table`, `create_table` | POST with validation |
| Streaming | `py-src/data_formulator/routes/agents.py` | SSE responses |
| Errors | `py-src/data_formulator/error_handler.py` | Error handler pattern |

**Step 3**: Trace a request

1. Open [FLASK_IN_DATAFORMULATOR.md](FLASK_IN_DATAFORMULATOR.md) → Data Loading section
2. Open `py-src/data_formulator/routes/tables.py`
3. Follow the code:
   - Route decorator
   - Request parsing
   - Error handling
   - Response formatting

---

## Phase 3: Codebase Exploration (2-4 hours)

### Critical Files to Understand

#### 1. Application Setup (`app.py`)

**What to focus on**:
- How Flask app is created
- Configuration from environment
- Blueprint lazy-loading
- Error handler registration

**Reading guide**:
```python
# Line 1-100: App creation and config
- Creates Flask(__name__)
- Sets session storage (filesystem)
- Configures JSON encoding
- Stores CLI args in app.config

# Line 200-300: _register_blueprints()
- Imports blueprints lazily
- Registers them with app.register_blueprint()
- Initializes auth provider
```

#### 2. Blueprint Examples (`routes/` directory)

**Structure**:
```
routes/
├── tables.py        # Data loading & querying
├── agents.py        # AI agent execution
├── sessions.py      # Workspace management
└── logs.py          # Server logs
```

**Study pattern**:
```python
# 1. Create blueprint
bp = Blueprint('name', __name__, url_prefix='/api/path')

# 2. Define routes
@bp.route('/', methods=['GET'])
def handler():
    # Parse request
    # Validate input
    # Call service
    # Return response
    return jsonify({'data': ...})
```

#### 3. Authentication (`auth/` directory)

**Components**:
- `identity.py`: Provider selection (OIDC, GitHub, etc.)
- `providers/`: OAuth providers (OIDC, GitHub)
- `gateways/`: Request handlers for OAuth flow
- `token_store.py`: Session-based token storage

**Key flow**:
```
User clicks "Login"
  ↓
Redirect to OAuth provider
  ↓
User authenticates with provider
  ↓
Provider redirects back to /auth/callback
  ↓
App exchanges code for tokens
  ↓
Tokens stored in server session
  ↓
User sees authenticated UI
```

#### 4. Error Handling (`error_handler.py`)

**Pattern**:
```python
# Custom exception
class AppError(Exception):
    def __init__(self, code: ErrorCode, message: str):
        self.code = code
        self.message = message

# Global handler catches all AppErrors
@app.errorhandler(AppError)
def handle(error):
    return {
        'success': False,
        'error': {'code': error.code.name, 'message': error.message}
    }, 200  # Always 200!

# Use in routes
@app.route('/data')
def get_data():
    try:
        workspace = load_workspace(id)
    except FileNotFoundError:
        raise AppError(ErrorCode.WORKSPACE_NOT_FOUND, "...")
```

### Questions to Answer

As you explore, try to answer:

1. **How does a request flow through the system?**
   - User sends request → Flask routes → Handler → Response

2. **How are blueprints organized?**
   - By feature/domain (auth, data, agents)
   - Each blueprint has `url_prefix`

3. **How is authentication handled?**
   - OAuth flow, tokens stored in session
   - Middleware checks session before protected routes

4. **How are errors handled?**
   - Custom AppError exceptions
   - Global error handler returns JSON
   - Always HTTP 200 with error in body

5. **How is streaming implemented?**
   - Generator function yields events
   - Response with `mimetype='text/event-stream'`

---

## Phase 4: Hands-On Development

### Practice Tasks

#### Task 1: Add a Simple GET Endpoint

**Goal**: Create a new route that returns data

```python
# Add to py-src/data_formulator/routes/tables.py

@tables_bp.route('/health')
def health_check():
    """Simple health check endpoint."""
    return jsonify({
        'status': 'ok',
        'version': '0.8.0b1'
    })
```

Test it:
```bash
curl http://localhost:5567/api/tables/health
```

#### Task 2: Trace a Request

**Goal**: Follow a request from start to finish

1. User clicks "Load Data" button
2. Frontend sends: `POST /api/tables` with credentials
3. Frontend: See `src/app/App.tsx` or similar
4. Backend: Find handler in `py-src/data_formulator/routes/tables.py`
5. Handler loads data, saves, returns response
6. Frontend: Receives response, updates Redux
7. UI: Re-renders with new data

**Write out the flow**:
- Frontend file that sends request: `___`
- Backend route handler: `___`
- Data loading code: `___`
- Response format: `___`

#### Task 3: Understand Error Flow

**Goal**: See how errors are handled

1. Open `py-src/data_formulator/error_handler.py`
2. Find `@app.errorhandler(AppError)`
3. Find one place that `raise AppError()`
4. Trace: Error raised → Handler catches → Returns JSON → Frontend receives
5. Draw the flow

#### Task 4: Add Error Handling

**Goal**: Make a route more robust

```python
# Before: Minimal error handling
@tables_bp.route('/info')
def get_table_info():
    table_id = request.args.get('table_id')
    table = load_table(table_id)  # What if not found?
    return jsonify({'table': table})

# After: Proper error handling
@tables_bp.route('/info')
def get_table_info():
    table_id = request.args.get('table_id')
    
    # Validate input
    if not table_id:
        raise AppError(
            ErrorCode.INVALID_REQUEST,
            "table_id query parameter required"
        )
    
    # Handle errors
    try:
        table = load_table(table_id)
    except FileNotFoundError:
        raise AppError(
            ErrorCode.TABLE_NOT_FOUND,
            f"Table '{table_id}' not found"
        )
    
    # Return response
    return jsonify({'table': table})
```

#### Task 5: Study a Complex Flow

**Goal**: Understand agent execution with streaming

1. Open `FLASK_IN_DATAFORMULATOR.md` → "Agent Execution & Streaming"
2. Read the code examples
3. Open `py-src/data_formulator/routes/agents.py` (if exists)
4. Find the actual SSE streaming code
5. Answer:
   - What does the generator yield?
   - What mimetype is used?
   - How does frontend receive events?
   - What headers are set and why?

---

## Key Concepts Checklist

### Concepts You Should Know

- [ ] What a Flask app is and how to create one
- [ ] How to define routes with `@app.route()`
- [ ] Difference between GET, POST, PUT, DELETE
- [ ] How to parse request data (JSON, query params, headers)
- [ ] How to return different response types
- [ ] What blueprints are and why they're useful
- [ ] How sessions work (server-side storage)
- [ ] What middleware is and when it runs
- [ ] How error handling works (global handlers)
- [ ] What SSE is and how to stream responses

### Flask Concepts in Data Formulator

- [ ] Blueprint organization (auth, data, agents)
- [ ] OAuth/OIDC authentication flow
- [ ] Error response format (always HTTP 200)
- [ ] AppError exception pattern
- [ ] Request ID middleware for logging
- [ ] SSE streaming for agent responses
- [ ] Session for storing OAuth tokens
- [ ] Configuration from environment

---

## Common Issues & Solutions

### Issue: "Module not found"

```python
# Error: ImportError: cannot import name 'tables_bp'
# Cause: Blueprint not registered

# Solution: Check app.py for app.register_blueprint()
```

### Issue: "Request data is None"

```python
# Issue: request.json is None even though data was sent
# Cause: Content-Type header not set

# Solution: Set header in request
# curl -X POST http://... \
#   -H "Content-Type: application/json" \
#   -d '{"key": "value"}'
```

### Issue: "Session data lost after refresh"

```python
# Issue: session['token'] is None after page reload
# Cause: Session not configured for persistence

# Solution: Check app.py for SESSION_TYPE = 'cachelib'
# and SESSION_PERMANENT = True
```

### Issue: "Streaming not working"

```python
# Issue: Event stream doesn't start
# Cause: Missing MIME type or headers

# Solution: Return Response with mimetype='text/event-stream'
# and headers={'Cache-Control': 'no-cache'}
```

---

## Quick Reference During Development

### File Locations

```
py-src/data_formulator/
├── app.py                          # App creation, blueprint registration
├── error_handler.py                # Global error handlers
├── errors.py                       # Error codes and AppError
│
├── routes/                         # API blueprints
│   ├── tables.py
│   ├── agents.py
│   └── sessions.py
│
├── auth/                           # Authentication
│   ├── identity.py
│   ├── providers/                  # OAuth providers
│   ├── gateways/                   # Request handlers
│   └── token_store.py
│
└── data_connector.py               # Data source abstraction
```

### Common Patterns

| Task | Pattern |
|------|---------|
| **Create route** | `@bp.route('/path', methods=['GET', 'POST'])` |
| **Get request data** | `request.json`, `request.args.get()` |
| **Return JSON** | `return jsonify({'key': value})` |
| **Return with status** | `return data, 201` |
| **Raise error** | `raise AppError(ErrorCode.X, "message")` |
| **Stream response** | `return Response(generate(), mimetype='text/event-stream')` |
| **Access session** | `session['key'] = value` or `session.get('key')` |
| **Register blueprint** | `app.register_blueprint(bp)` |

---

## Next Steps

1. **Read the guides in order**
   - [FLASK_FUNDAMENTALS_GUIDE.md](FLASK_FUNDAMENTALS_GUIDE.md) (Fundamentals)
   - [FLASK_QUICK_REFERENCE.md](FLASK_QUICK_REFERENCE.md) (Quick reference)
   - [FLASK_IN_DATAFORMULATOR.md](FLASK_IN_DATAFORMULATOR.md) (Real code)

2. **Explore the codebase**
   - Start with `app.py`
   - Trace a request to a blueprint
   - Read authentication code
   - Study error handling

3. **Practice**
   - Modify an endpoint
   - Add error handling
   - Implement a new route
   - Debug issues using logs

4. **Dive deeper**
   - Read [BACKEND_ARCHITECTURE_GUIDE.md](BACKEND_ARCHITECTURE_GUIDE.md)
   - Study data loaders
   - Understand agent system
   - Learn deployment

---

## Resources

**Official Documentation**
- [Flask Official Docs](https://flask.palletsprojects.com/)
- [Flask Quick Start](https://flask.palletsprojects.com/quickstart/)
- [Jinja2 Templates](https://jinja.palletsprojects.com/)

**Related Tools**
- [HTTP Methods & Status Codes](https://developer.mozilla.org/en-US/docs/Web/HTTP)
- [JSON Format](https://www.json.org/)
- [OAuth 2.0 Flow](https://oauth.net/2/)

**In This Project**
- [COMPREHENSIVE_CODEBASE_GUIDE.md](COMPREHENSIVE_CODEBASE_GUIDE.md)
- [BACKEND_ARCHITECTURE_GUIDE.md](BACKEND_ARCHITECTURE_GUIDE.md)
- [FRONTEND_ARCHITECTURE.md](FRONTEND_ARCHITECTURE.md)

---

## Estimate Your Learning Time

| Phase | Time | What You'll Know |
|-------|------|------------------|
| **Phase 1** | 1-2 hrs | Flask basics, simple routes, blueprints |
| **Phase 2** | 1-2 hrs | Real patterns, auth, streaming, errors |
| **Phase 3** | 2-4 hrs | Full codebase structure, can read code |
| **Phase 4** | Ongoing | Can modify, debug, add features |

**Total**: ~5-8 hours to feel comfortable with the codebase

---

**Happy learning! You've got this! 🚀**

For questions:
1. Check the quick reference guides
2. Search the codebase
3. Trace the code flow
4. Read the comprehensive architecture guides

Good luck! 💪
