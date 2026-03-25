from api import API

# 1 - WSGI compliant
# def app(environ, start_response):
#     response_body = b"Hello, World!"
#     status = "200 OK"
#     start_response(status, headers=[])
#     return iter([response_body])


app = API()


@app.route("/")
def home(request, response):
    response.text = "Welcome to the <b>deramahmud</b> Python Framework, full of mistakes💥"

@app.route("/home")
def home(request, response):
    response.text = "Hello from the HOME page"

@app.route("/about")
def about(request, response):
    response.text = "Hello from the ABOUT page"
