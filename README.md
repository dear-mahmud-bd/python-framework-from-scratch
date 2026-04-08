# [MahmudCore](https://pypi.org/project/MahmudCore/0.0.1/)

![Purpose](https://img.shields.io/badge/purpose-learning-green.svg)
![PyPI](https://img.shields.io/pypi/v/MahmudCore.svg)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-alpha-orange.svg)

**MahmudCore** is a Python web framework built from scratch for exploring and understanding the core concepts that power every modern web framework. It is a WSGI-compliant framework that can be used with any WSGI application server such as Gunicorn or Waitress.

> Built by **Md. Mahmudul Hasan** - layer by layer, from raw WSGI to a fully-featured framework.

---

## Table of Contents

- [Why MahmudCore?](#why-mahmudcore)
- [Architecture Overview](#architecture-overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Features](#features)
  - [Routing](#routing)
  - [Class-Based Handlers](#class-based-handlers)
  - [HTTP Method Control](#http-method-control)
  - [Template Rendering](#template-rendering)
  - [Static Files](#static-files)
  - [Middleware](#middleware)
  - [Exception Handling](#exception-handling)
  - [Custom Response](#custom-response)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [What I Learned Building This](#what-i-learned-building-this)
- [License](#license)

---

## Why MahmudCore?

Most developers use Flask or Django without understanding what happens underneath. MahmudCore was built to answer the question: **what is a web framework actually doing?**

Every feature in MahmudCore was built from first principles:

- Starting from the raw WSGI spec (`environ`, `start_response`)
- Adding routing, then dynamic routing, then class-based handlers
- Integrating Jinja2 for templates, WhiteNoise for static files
- Building a middleware pipeline from scratch
- Packaging and publishing to PyPI

If you want to understand how Flask, Django, or FastAPI work under the hood - reading MahmudCore is a great place to start.

---

## Architecture Overview

```
Incoming HTTP Request
        │
        ▼
   __call__  (WSGI entry point)
        │
        ├─── /static/* ──► WhiteNoise ──► serve file from disk
        │
        └─── everything else
                │
                ▼
        Middleware pipeline
        (LoggingMiddleware → AuthMiddleware → ...)
                │
                ▼
        handle_request
                │
                ├─── find_handler (parse URL pattern)
                │
                ├─── class-based handler?
                │       └─── getattr(Handler(), 'get' / 'post' / ...)
                │
                ├─── function-based handler?
                │       └─── check allowed_methods list
                │
                └─── default_response (404)
                        │
                        ▼
                Response object
                (json / html / text / body)
                        │
                        ▼
              response(environ, start_response)
```

---

## Installation

```bash
pip install MahmudCore
```

Install with development tools:

```bash
pip install MahmudCore[dev]
```

---

## Quick Start

Create `app.py`:

```python
from mahmudcore.api import API

app = API()

@app.route("/")
def home(request, response):
    response.text = "Hello from MahmudCore!"

@app.route("/hello/{name}")
def greet(request, response, name):
    response.text = f"Hello, {name}!"
```

Run with Gunicorn:

```bash
gunicorn app:app
```

Or Waitress (Windows-friendly):

```bash
waitress-serve --listen=127.0.0.1:8080 app:app
```

Visit `http://localhost:8000` in your browser.

---

## Features

### Routing

MahmudCore supports two routing styles - Flask-style decorators and Django-style explicit registration.

**Decorator style:**

```python
@app.route("/home")
def home(request, response):
    response.text = "Hello from HOME"
```

**Django style:**

```python
def home(request, response):
    response.text = "Hello from HOME"

app.add_route("/home", home)
```

Both styles use the same underlying `self.routes` dictionary and share the same duplicate detection:

```python
@app.route("/home")
def home_v1(request, response): ...

@app.route("/home")          # ← AssertionError: Route '/home' already exists.
def home_v2(request, response): ...
```

**Dynamic URL parameters** using the `parse` library:

```python
@app.route("/hello/{name}")
def greet(request, response, name):
    response.text = f"Hello, {name}!"

@app.route("/books/{id:d}")       # :d = digits only
def book_detail(request, response, id):
    response.text = f"Book #{id}"

@app.route("/users/{username:w}/profile")   # :w = word characters
def profile(request, response, username):
    response.text = f"{username}'s profile"
```

---

### Class-Based Handlers

Organise multiple HTTP methods for the same URL into a single class - similar to Django's class-based views:

```python
@app.route("/books")
class BooksResource:
    def get(self, req, resp):
        resp.json = {"books": ["Book 1", "Book 2"]}

    def post(self, req, resp):
        resp.json = {"message": "Book created"}

@app.route("/users/{id:d}")
class UserResource:
    def get(self, req, resp, id):
        resp.text = f"Get user {id}"

    def put(self, req, resp, id):
        resp.text = f"Update user {id}"

    def delete(self, req, resp, id):
        resp.status_code = 204
```

Calling an HTTP method not defined on the class raises `AttributeError("Method not allowed")`.

---

### HTTP Method Control

Restrict which HTTP methods a function-based handler accepts:

```python
@app.route("/api/users", allowed_methods=["get", "post"])
def users_api(request, response):
    if request.method == "GET":
        response.json = {"users": []}
    elif request.method == "POST":
        response.json = {"message": "User created"}

@app.route("/api/report", allowed_methods=["get"])
def report(request, response):
    response.text = "Quarterly report"
```

If a disallowed method is used, `AttributeError` is raised, which can be caught by your exception handler.

---

### Template Rendering

MahmudCore integrates **Jinja2** for dynamic HTML generation:

```python
app = API(templates_dir="templates")

@app.route("/page")
def page(request, response):
    response.html = app.template("index.html", context={
        "title": "My Page",
        "username": "Mahmud",
        "items": ["Python", "WSGI", "Frameworks"],
    })
```

`templates/index.html`:

```html
<html>
  <head><title>{{ title }}</title></head>
  <body>
    <h1>Welcome, {{ username }}</h1>
    <ul>
      {% for item in items %}
        <li>{{ item }}</li>
      {% endfor %}
    </ul>
  </body>
</html>
```

---

### Static Files

MahmudCore uses **WhiteNoise** to serve static assets. Place your files inside the `static/` folder and reference them with the `/static/` URL prefix:

```python
app = API(static_dir="static")
```

```
static/
├── main.css
├── app.js
└── logo.png
```

In HTML:

```html
<link rel="stylesheet" href="static/main.css">
<script src="static/app.js"></script>
```

The framework automatically strips the `/static` prefix and passes the request to WhiteNoise for file serving.

---

### Middleware

Create reusable components that run before and after every request. Middleware is the right place for cross-cutting concerns like logging, authentication, timing, and CORS.

**Creating middleware:**

```python
from mahmudcore.middleware import Middleware

class LoggingMiddleware(Middleware):
    def process_request(self, req):
        print(f"→ {req.method} {req.url}")

    def process_response(self, req, resp):
        print(f"← {resp.status_code}")


class RequestTimingMiddleware(Middleware):
    def process_request(self, req):
        import time
        req.start_time = time.time()

    def process_response(self, req, resp):
        duration = time.time() - req.start_time
        resp.headers["X-Response-Time"] = f"{duration:.4f}s"
```

**Registering middleware:**

```python
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestTimingMiddleware)
```

Middleware is chained as nested wrappers. The last registered middleware runs first on incoming requests. Each middleware calls `process_request` before passing the request down, and `process_response` on the way back up.

**The pipeline looks like this:**

```
Request → RequestTimingMiddleware → LoggingMiddleware → API
Response ← RequestTimingMiddleware ← LoggingMiddleware ← API
```

---

### Exception Handling

Register a custom exception handler to catch any unhandled error that occurs inside a route handler:

```python
def on_error(request, response, exception):
    response.status_code = 500
    response.json = {
        "error": type(exception).__name__,
        "message": str(exception),
    }

app.add_exception_handler(on_error)

@app.route("/risky")
def risky_handler(request, response):
    raise ValueError("Something went wrong")
# → Returns JSON error instead of crashing
```

Custom exception classes work too:

```python
class UnauthorizedException(Exception):
    pass

def on_error(request, response, exc):
    if isinstance(exc, UnauthorizedException):
        response.status_code = 401
        response.text = "Unauthorized"
    else:
        response.status_code = 500
        response.text = "Internal Server Error"

app.add_exception_handler(on_error)
```

---

### Custom Response

The `Response` object provides clean, type-specific helpers that handle encoding and content-type automatically:

```python
# JSON response - automatic serialization + application/json header
@app.route("/api/data")
def data(req, resp):
    resp.json = {"name": "MahmudCore", "version": "0.0.1"}


# HTML response - automatic encoding + text/html header
@app.route("/page")
def page(req, resp):
    resp.html = app.template("index.html", context={"title": "Home"})


# Plain text response - automatic text/plain header
@app.route("/ping")
def ping(req, resp):
    resp.text = "pong"


# Raw bytes - manual content type required
@app.route("/raw")
def raw(req, resp):
    resp.body = b"raw bytes"
    resp.content_type = "application/octet-stream"


# Set status code
@app.route("/created")
def created(req, resp):
    resp.json = {"id": 1}
    resp.status_code = 201


# Set custom headers
@app.route("/cors")
def cors(req, resp):
    resp.text = "OK"
    resp.headers["Access-Control-Allow-Origin"] = "*"
```

---

## Running the Application

**Gunicorn (recommended for Linux/macOS):**

```bash
gunicorn app:app
gunicorn app:app --bind 0.0.0.0:8080 --workers 4
```

**Waitress (recommended for Windows):**

```bash
waitress-serve --listen=127.0.0.1:8080 app:app
```

---

## Testing

MahmudCore includes a built-in test client that sends requests directly to the WSGI app - no running server needed:

```python
# conftest.py
import pytest
from mahmudcore.api import API

@pytest.fixture
def api():
    return API()

@pytest.fixture
def client(api):
    return api.test_session()
```

```python
# test_app.py
def test_home_returns_200(api, client):
    @api.route("/home")
    def home(req, resp):
        resp.text = "Hello"

    response = client.get("http://testserver/home")
    assert response.status_code == 200
    assert response.text == "Hello"


def test_404_for_unknown_route(client):
    response = client.get("http://testserver/nonexistent")
    assert response.status_code == 404


def test_duplicate_route_raises(api):
    @api.route("/test")
    def handler(req, resp): pass

    import pytest
    with pytest.raises(AssertionError):
        @api.route("/test")
        def handler2(req, resp): pass


def test_method_not_allowed(api, client):
    @api.route("/read-only", allowed_methods=["get"])
    def handler(req, resp):
        resp.text = "OK"

    import pytest
    with pytest.raises(AttributeError):
        client.post("http://testserver/read-only")
```

Run tests:

```bash
pytest
pytest --cov=mahmudcore        # with coverage
pytest --cov=mahmudcore --cov-report=html   # HTML report
```

---

## Project Structure

```
mahmudcore/
├── mahmudcore/
│   ├── __init__.py
│   ├── api.py          # Core API class - routing, WSGI entry point
│   ├── middleware.py   # Base Middleware class and pipeline
│   └── response.py     # Custom Response class
├── templates/          # Jinja2 HTML templates
├── static/             # Static assets (CSS, JS, images)
├── app.py              # Your application
├── test_app.py         # Tests
├── conftest.py         # Pytest fixtures
├── setup.py            # Package configuration
└── README.md
```

---

## Dependencies

| Package | Purpose |
|---|---|
| `webob` | WSGI Request/Response objects |
| `jinja2` | HTML template engine |
| `parse` | URL parameter extraction |
| `whitenoise` | Static file serving |
| `requests` | HTTP client (used in test session) |
| `requests-wsgi-adapter` | Connects requests to WSGI for testing |

Install all at once:

```bash
pip install webob jinja2 parse whitenoise requests requests-wsgi-adapter
```

---

## What I Learned Building This

Building MahmudCore from scratch across open-secrete labs😉 taught me how every Python web framework actually works:

**WSGI** is just a contract: your app must be a callable that accepts `(environ, start_response)` and returns an iterable of bytes. Everything else - routing, templates, middleware - is built on top of that single rule.

**`__call__`** on a class makes it behave like a function. This is how the `API` class, every middleware, and WhiteNoise all work together as WSGI callables.

**Middleware is just wrapping**. `Reverseware(app)`, `WhiteNoise(app)`, `AuthMiddleware(app)` - they all follow the same pattern: receive a request, optionally do something, call the inner app, optionally do something to the response.

**`inspect.isclass(handler)`** is how function-based and class-based handlers are distinguished. `getattr(Handler(), request.method.lower(), None)` is how class-based method routing works.

**`parse` library** does the heavy lifting for dynamic URL patterns like `/users/{id:d}`. Flask uses a similar approach with Werkzeug's routing.

**WhiteNoise as WSGI middleware** wraps `wsgi_app` and intercepts static file requests before they reach the routing logic.

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

*Built with curiosity by [Md. Mahmudul Hasan](mailto:dearmahmud.bd@gmail.com)*
