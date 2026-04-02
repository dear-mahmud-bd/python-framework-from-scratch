
import pytest
from api import API

@pytest.fixture
def api():
    return API()

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

# pytest test_dearmahmud.py
