
# Unit Testing 
import pytest

# from api import API

# @pytest.fixture
# def api():
#     return API()

def test_basic_route_adding(api):
    @api.route_create("/home")  # This overwrites the first handler! -> thats a problem
    def home2(request, response):
        response.text = "Hello from the SECOND HOME page test"
    assert "/home" in api.routes
    assert api.routes["/home"] == home2


def test_duplicate_route_throws_exception(api):
    @api.route_create("/test")
    def test(request, response):
        response.text = "Hello from the HOME page test"

    with pytest.raises(AssertionError):
        @api.route_create("/test")  # This should raise an exception because the route already exists
        def test(request, response):
            response.text = "Hello from the SECOND HOME page test"


def test_client_can_send_requests(api, client):
    RESPONSE_TEXT = "Hello from test client"

    @api.route_create("/test")
    def test_handler(request, response):
        response.text = RESPONSE_TEXT

    response = client.get("http://127.0.0.1:8082/test")
    assert response.text == RESPONSE_TEXT


def test_parameterized_route(api, client):
    @api.route_create("/hello/{name}")
    def hello(request, response, name):
        response.text = f"Hello, {name}!"

    # Test multiple parameter values
    assert client.get("http://127.0.0.1:8082/hello/Alice").text == "Hello, Alice!"
    assert client.get("http://127.0.0.1:8082/hello/Bob").text == "Hello, Bob!"
    assert client.get("http://127.0.0.1:8082/hello/Charlie").text == "Hello, Charlie!"


def test_default_404_response(client):
    response = client.get("http://127.0.0.1:8082/nonexistent")
    
    assert response.status_code == 404
    assert response.text == "Request Not found"


def test_class_based_handler_get(api, client):
    response_text = "This is a GET request"
    @api.route_create("/books")
    class BookResource:
        def get(self, request, response):
            response.text = response_text

    response = client.get("http://127.0.0.1:8082/books")
    assert response.text == response_text

def test_class_based_handler_post(api, client):
    response_text = "This is a POST request"

    @api.route_create("/books")
    class BookResource:
        def post(self, request, response):
            response.text = response_text

    response = client.post("http://127.0.0.1:8082/books")
    assert response.text == response_text

def test_class_based_handler_not_allowed_method(api, client):
    @api.route_create("/books")
    class BookResource:
        def post(self, request, response):
            response.text = "Only POST allowed."

    # This should raise AttributeError (method not implemented)
    with pytest.raises(AttributeError):
        client.get("http://127.0.0.1:8082/books")


def test_alternative_route(api, client):
    response_text = "Alternative way to add a route"

    def home(req, resp):
        resp.text = response_text

    api.add_route("/alternative", home)

    assert client.get("http://127.0.0.1:8082/alternative").text == response_text


def test_template(api, client):
    @api.route("/html")
    def html_handler(req, resp):
        resp.body = api.template("index.html", context={
            "title": "Some Title", 
            "name": "Some Name"
        }).encode()

    response = client.get("http://127.0.0.1:8082/html")

    assert "text/html" in response.headers["Content-Type"]
    assert "Some Title" in response.text
    assert "Some Name" in response.text


def test_custom_exception_handler(api, client):
    def on_exception(req, resp, exc):
        resp.text = "AttributeErrorHappened"

    api.add_exception_handler(on_exception)

    @api.route("/")
    def index(req, resp):
        raise AttributeError()

    response = client.get("http://127.0.0.1:8082/")

    assert response.text == "AttributeErrorHappened"


# pytest test_dearmahmud.py
# pytest test_dearmahmud.py::test_template
# pytest test_dearmahmud.py::test_custom_exception_handler
# pytest --cov=. test_dearmahmud.py
# pytest --cov=. --cov-report=html test_dearmahmud.py


