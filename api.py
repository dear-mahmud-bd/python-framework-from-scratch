
import os
import inspect
from parse import parse
from whitenoise import WhiteNoise
from middleware import Middleware
from webob import Request, Response
from requests import Session as RequestsSession
from jinja2 import Environment, FileSystemLoader
from wsgiadapter import WSGIAdapter as RequestsWSGIAdapter

class API:
    def __init__(self, templates_dir="templates", static_dir="static"):
        self.routes = {}
        # Initialize Jinja2 environment
        self.templates_env = Environment(
            loader=FileSystemLoader(os.path.abspath(templates_dir))
        )
        self.exception_handler = None
        # Initialize WhiteNoise for static file serving
        self.whitenoise = WhiteNoise(self.wsgi_app, root=static_dir)
        self.middleware = Middleware(self)  # middleware instance

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.handle_request(request)
        return response(environ, start_response)  

    def __call__(self, environ, start_response):
        # 1 - WSGI compliant,
        # response_body = b"Hello, Mahmud!"
        # status = "200 OK"
        # start_response(status, headers=[])
        # return iter([response_body])
        
        #  2 - WebOb compliant
        # request = Request(environ)
        # response = Response()
        # response.text = "Hello, World..!"
        # return response(environ, start_response)

        # 3 - WebOb compliant with user agent
        # request = Request(environ)
        # response = self.handle_request(request)
        # return response(environ, start_response)

        # 4 - Serve static files with WhiteNoise
        # return self.whitenoise(environ, start_response)
        
        path_info = environ["PATH_INFO"]

        if path_info.startswith("/static"):
            environ["PATH_INFO"] = path_info[len("/static"):]
            return self.whitenoise(environ, start_response)
        # Use middleware instead of direct handling
        return self.middleware(environ, start_response)  

    
    def add_middleware(self, middleware_cls):
        self.middleware.add(middleware_cls)

    def add_exception_handler(self, exception_handler):
        self.exception_handler = exception_handler

    def route_create(self, path, allowed_methods=None):
        # # Check for duplicate routes
        # if path in self.routes:
        #     raise AssertionError("Such route already exists.")
        def wrapper(handler):
            self.add_route(path, handler, allowed_methods)  # Reuse add_route logic
            return handler
        return wrapper
    
    # Django-style class-based views
    # api.py - Update the add_route method
    def add_route(self, path, handler, allowed_methods=None):
        assert path not in self.routes, "Such route already exists."
        if allowed_methods is None:
            allowed_methods = ["get", "post", "put", "patch", "delete", "options"]
        self.routes[path] = {"handler": handler, "allowed_methods": [method.lower() for method in allowed_methods]}


    def route(self, path, allowed_methods=None):
        def wrapper(handler):
            self.add_route(path, handler, allowed_methods) # Reuse add_route logic
            return handler
        return wrapper

    def default_response(self, response):
        response.status_code = 404
        response.text = "Request Not found"

    # def find_handler(self, request_path):
    #     # 1 - simple path matching
    #     # for path, handler in self.routes.items():
    #     #     if path == request_path:
    #     #         return handler

    #     # 2 - path matching with parameters
    #     # for path, handler in self.routes.items():
    #     #     parse_result = parse(path, request_path)
    #     #     if parse_result is not None:
    #     #         return handler, parse_result.named
    #     # return None, None
    
    def find_handler(self, request_path):
        for path, handler_data in self.routes.items():
            parse_result = parse(path, request_path)
            if parse_result is not None:
                return handler_data, parse_result.named
        return None, None


    def handle_request(self, request):
        # 1 - WSGI compliant
        # user_agent = request.environ.get("HTTP_USER_AGENT", "No User Agent Found")
        # response = Response()
        # response.text = f"Hello, my friend with this user agent: {user_agent}"
        # return response

        # 2 - WebOb compliant with routing
        # response = Response()
        # for path, handler in self.routes.items():
        #     if path == request.path:
        #         handler(request, response)
        #         return response
        # self.default_response(response)
        # return response

        # # 3 - for better maintainability
        # # handler = self.find_handler(request_path=request.path)
        # response = Response()
        # handler, kwargs = self.find_handler(request_path=request.path)
        # if handler:
        #     # handler(request, response)
        #     if inspect.isclass(handler):
        #         # # Get the appropriate method from the class
        #         # handler_instance = handler()  # Create instance
        #         # method_name = request.method.lower()  # 'GET' -> 'get'
        #         # handler_function = getattr(handler_instance, method_name, None)
        #         handler = getattr(handler(), request.method.lower(), None)
        #         if handler is None:
        #             raise AttributeError("Method not allowed", request.method)
        #         handler(request, response, **kwargs)
        #     else:
        #         handler(request, response, **kwargs)
        # else:
        #     self.default_response(response)
        # return response


        # 4. Handle exceptions with a custom handler
        # response = Response()
        # handler, kwargs = self.find_handler(request_path=request.path)
        
        # try:
        #     if handler is not None:
        #         if inspect.isclass(handler):
        #             handler = getattr(handler(), request.method.lower(), None)
        #             if handler is None:
        #                 raise AttributeError("Method not allowed", request.method)
        #         handler(request, response, **kwargs)
        #     else:
        #         self.default_response(response)
        # except Exception as e:
        #     if self.exception_handler is None:
        #         raise e  # Re-raise if no custom handler
        #     else:
        #         self.exception_handler(request, response, e)
        # return response


        # 5. Use middleware for request/response processing and exception handling
        response = Response()
        handler_data, kwargs = self.find_handler(request_path=request.path)
        
        try:
            if handler_data is not None:
                handler = handler_data["handler"]
                allowed_methods = handler_data["allowed_methods"]
                
                if inspect.isclass(handler):
                    # Class-based handler - existing logic
                    handler = getattr(handler(), request.method.lower(), None)
                    if handler is None:
                        raise AttributeError("Method not allowed", request.method)
                else:
                    # Function-based handler - new method validation
                    if request.method.lower() not in allowed_methods:
                        raise AttributeError("Method not allowed", request.method)
                
                handler(request, response, **kwargs)
            else:
                self.default_response(response)
        except Exception as e:
            if self.exception_handler is None:
                raise e
            else:
                self.exception_handler(request, response, e)
        
        return response


    def test_session(self, base_url="http://127.0.0.1:8082"):
        session = RequestsSession()
        session.mount(prefix=base_url, adapter=RequestsWSGIAdapter(self))
        return session

    def template(self, template_name, context=None):
        if context is None:
            context = {}
        
        return self.templates_env.get_template(template_name).render(**context)

