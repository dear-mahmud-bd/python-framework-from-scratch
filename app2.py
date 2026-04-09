# app.py

from MahmudCore.api import API
from storage import QuestionStorage
from auth import login_required, TokenMiddleware, STATIC_TOKEN, on_exception


app = API()
question_storage = QuestionStorage()

# Add the token middleware to the API
app.add_middleware(TokenMiddleware)
# Set the exception handler
app.add_exception_handler(on_exception)



# Create sample data
question_storage.create(
    title="What is Python?",
    content="Can someone explain Python in simple terms?",
    author="Mahmud"
)
question_storage.create(
    title="What is WSGI?",
    content="I want to understand how WSGI works in Python web frameworks.",
    author="Hasan"
)
question_storage.create(
    title="What is MVC?",
    content="Can someone explain the MVC pattern with a simple example?",
    author="Rahim"
)
question_storage.create(
    title="What is an API?",
    content="I often hear about APIs in web development. What exactly is an API?",
    author="Karim"
)



@app.route("/", allowed_methods=["get"])
def index(req, resp):
    resp.html = app.template("home.html")

@app.route("/questions", allowed_methods=["get"])
def index(req, resp):
    questions = question_storage.all()
    resp.html = app.template("questions.html", context={"questions": questions})



@app.route("/questions/login", allowed_methods=["post"])
def login(req, resp):
    resp.json = {"token": STATIC_TOKEN}

@app.route("/questions/question", allowed_methods=["post"])
@login_required
def create_book(req, resp):
    book = question_storage.create(**req.POST)
    
    resp.status_code = 201
    resp.json = book._asdict()

@app.route("/questions/question/{id:d}", allowed_methods=["delete"])
@login_required
def delete_book(req, resp, id):
    question_storage.delete(id)
    resp.status_code = 204

# waitress-serve --listen=127.0.0.1:8082 app2:appstatus_code = 204

# waitress-serve --listen=127.0.0.1:8082 app2:app