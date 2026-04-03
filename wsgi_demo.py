from wsgiref.simple_server import make_server

PORT = 8082

class MiddlewareReverse:
    def __init__(self, app):
        self.wrapped_app = app
        print(f"Using Middleware...")
    
    def __call__(self, environ, start_response, *args, **kwargs):
        # Call the wrapped application
        wrapped_app_response = self.wrapped_app(environ, start_response)
        
        # Reverse each chunk of the response
        return [data[::-1] for data in wrapped_app_response]


def application(environ, start_response):
    # # Extract and format environment variables
    # response_body = [
    #     f'{key}: {value}' for key, value in sorted(environ.items())
    # ]
    # response_body = '\n'.join(response_body)
    
    response_body = f"Path: {environ['PATH_INFO']}"

    # Set response status and headers
    status = '200 OK'
    response_headers = [
        ('Content-type', 'text/plain'),
    ]
    
    # Call start_response with status and headers
    start_response(status, response_headers)
    
    # Return response body as bytes in an iterable
    return [response_body.encode('utf-8')]


server = make_server(
    'localhost', 
    PORT, 
    app=(application)
    # app=MiddlewareReverse(application)
)
print(f"Serving on http://localhost:{PORT}")
server.serve_forever()

# waitress-serve --listen=127.0.0.1:8082 app:app -> http://127.0.0.1:8082
# gunicorn app:app
