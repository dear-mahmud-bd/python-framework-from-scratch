
import time
from api import API
from middleware import Middleware


app = API()

@app.route("/")
def home(request, response):
    response.text = f"Welcome to the <b>deramahmud</b> Python Framework, full of mistakes💥!"

@app.route("/hello/{name}")
def hello(request, response, name):
    response.text = f"Hello, This is {name}!"

@app.route("/home")  # This overwrites the first handler! -> thats a problem
def home2(request, response):
    response.text = "Hello from the SECOND HOME page"

# Django-style class-based views 
@app.route("/books")
class BooksResource:
    def get(self, request, response):
        response.json = {"books": ["Book 1", "Book 2", "Book 3"]}
    def post(self, request, response):
        response.json = {"message": "Book created successfully"}
        
@app.route("/users/{id:d}")
class UserResource:
    def get(self, request, response, id):
        response.text = f"Get user {id}"
    def put(self, request, response, id):
        response.text = f"Update user {id}"
    def delete(self, request, response, id):
        response.text = f"Delete user {id}"

# New Django-style route
def sample_handler(request, response):
    response.text = "Django-style route example"
app.add_route("/django-sample", sample_handler)

def books_handler(request, response):
    response.text = "All books from Django-style route"
app.add_route("/django-books", books_handler)

def custom_exception_handler(request, response, exception_cls):
    response.text = f"Error occurred: {str(exception_cls)}"
app.add_exception_handler(custom_exception_handler)

@app.route("/exception")
def exception_throwing_handler(request, response):
    raise AssertionError("This handler should not be used.")

# Use Middleware for request/response processing
class SimpleCustomMiddleware(Middleware):
    def process_request(self, request):
        print("Processing request", request.url)

    def process_response(self, request, response):
        print("Processing response", request.url)
app.add_middleware(SimpleCustomMiddleware)

class RequestTimingMiddleware(Middleware):
    def process_request(self, request):
        request.start_time = time.time()
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            response.headers['X-Response-Time'] = f"{duration:.4f}s"
app.add_middleware(RequestTimingMiddleware)


# Function-based handlers with method control
@app.route("/api/products", allowed_methods=["GET", "POST"])
def products_api(request, response):
    if request.method == "GET":
        response.text = "List products"
    elif request.method == "POST":
        response.text = "Create product"

@app.route("/api/orders", allowed_methods=["GET"])
def orders_api(request, response):
    response.text = "List orders"

# Django-style route with method control
def admin_handler(request, response):
    response.text = "Admin panel - PATCH only"
app.add_route("/api/admin", admin_handler, allowed_methods=["PATCH"])


@app.route("/api/template")
def template_handler(request, response):
    response.html = app.template(
        "index.html", 
        context={
            "name": "dearmahmud", 
            "title": "Mahmud's Framework"
        }
    )

@app.route("/api/json")
def json_handler(request, response):
    response.json = {
        "name": "data", 
        "type": "JSON"
    }

@app.route("/api/text")
def text_handler(request, response):
    response.text = "This is a simple text"

# Add this API endpoint to show complex JSON responses
@app.route("/api/users")
def users_api(request, response):
    users = [
        {"id": 1, "name": "Mahmud", "email": "dearmahmud.bd@gmail.com"},
        {"id": 2, "name": "Tuntuni", "email": "tuntuni.hira@example.com"},
        {"id": 3, "name": "Tawsif", "email": "taway.seka@example.com"},
        {"id": 4, "name": "Didar", "email": "dider.pagla@mymenshing.com"}
    ]
    response.json = {"users": users, "total": len(users)}

