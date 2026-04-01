
import inspect

from parse import parse
from webob import Request, Response

class API:
    def __init__(self):
        self.routes = {}

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
        request = Request(environ)
        response = self.handle_request(request)
        return response(environ, start_response)

    def route_create(self, path):
        # # Check for duplicate routes
        # if path in self.routes:
        #     raise AssertionError("Such route already exists.")
        assert path not in self.routes, "Such route already exists."

        def wrapper(handler):
            self.routes[path] = handler
            return handler
        return wrapper
    
    def default_response(self, response):
        response.status_code = 404
        response.text = "Page not found"

    def find_handler(self, request_path):
        # 1 - simple path matching
        # for path, handler in self.routes.items():
        #     if path == request_path:
        #         return handler

        # 2 - path matching with parameters
        for path, handler in self.routes.items():
            parse_result = parse(path, request_path)
            if parse_result is not None:
                return handler, parse_result.named
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

        # 3 - for better maintainability
        # handler = self.find_handler(request_path=request.path)
        response = Response()
        handler, kwargs = self.find_handler(request_path=request.path)
        if handler:
            # handler(request, response)
            if inspect.isclass(handler):
                # # Get the appropriate method from the class
                # handler_instance = handler()  # Create instance
                # method_name = request.method.lower()  # 'GET' -> 'get'
                # handler_function = getattr(handler_instance, method_name, None)
                handler = getattr(handler(), request.method.lower(), None)
                if handler is None:
                    raise AttributeError("Method not allowed", request.method)
                handler(request, response, **kwargs)
            else:
                handler(request, response, **kwargs)
        else:
            self.default_response(response)
        return response

# 
