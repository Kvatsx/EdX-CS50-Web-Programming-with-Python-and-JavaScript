import os, requests

from flask import Flask, session, render_template, request, redirect, url_for, abort, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("RegisterFullName")
        email = request.form.get("RegisterInputEmail")
        password = request.form.get("RegisterInputPassword")

        # Check for empty fileds
        if name == "" or email == "" or password == "":
            return redirect(url_for('error', message="Empty fields are not allowed."))

        # Check if user already exist with this email id
        user_id = db.execute("SELECT id FROM Users WHERE email = :email",{"email": email}).fetchone()
        if user_id != None:
            return redirect(url_for('error', message="User already exist with this email id."))

        # else create a new user
        else:
            db.execute("INSERT INTO Users (name, email, password) VALUES (:name, :email, :password)",{
                "name": name, 
                "email": email, 
                "password": password})
            db.commit()
            return redirect(url_for("success"), code=302)
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("LoginInputEmail")
        password = request.form.get("LoginInputPassword")

        # Check for empty fileds
        if email == "" or password == "":
            return redirect(url_for('error', message="Empty fields are not allowed."))

        user = db.execute("SELECT id, name, email FROM Users WHERE email = :email AND password = :password",{"email": email, "password": password}).fetchone()
        if user != None:
            user = list(user)
            print(user)
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['user_email'] = user[2]
            print(session)
            return redirect(url_for("home"))
        else:
            return redirect(url_for('error', message="Wrong Credentials."))
    return render_template("login.html")

@app.route("/home", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        search = request.form.get("searchQuery")
        try:
            search = int(search)
            books = db.execute("SELECT * from Books WHERE CAST(year AS TEXT) LIKE :search", {"search": '%{}%'.format(search)}).fetchall()
            return render_template("home.html", user_name=session.get('user_name'), books=books)
        except ValueError:
            books = db.execute("SELECT * from Books WHERE LOWER(isbn) LIKE :search OR LOWER(title) LIKE :search OR LOWER(author) LIKE :search", {"search": '%{}%'.format(search)}).fetchall()
            return render_template("home.html", user_name=session.get('user_name'), books=books)
    else:
        print("Logged in:", session)
        if session.get('user_id') == None:
            print("Login now!")
            return redirect(url_for("login"))
        books = db.execute("SELECT * from Books").fetchall()
        print("Book Count:", len(books))
        return render_template("home.html", user_name=session.get('user_name'), books=books)

@app.route("/error")
def error():
    return render_template("error.html", message=request.args.get('message'))

@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/logout")
def logout():
    # session.pop("id", None)
    # session.pop("user_name", None)
    # session.pop("user_email", None)
    session['user_id'] = None
    session['user_name'] = None
    session['user_email'] = None
    return redirect(url_for('index'))


@app.route("/book/<isbn>")
def book(isbn):
    if isbn == None:
        return redirect(url_for('error', message="Invalid Isbn."))
    book = db.execute("SELECT * from Books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    if book == None:
        return redirect(url_for('error', message="No book exists with this isbn: {}.".format(isbn)))
    reviews = db.execute("SELECT * from Reviews WHERE isbn = :isbn", {"isbn": isbn})
    ratings = getRequiredRatingData(isbn)
    if ratings == None:
        return redirect(url_for('error', message="Goodreads Api not working"))
    return render_template("book.html", book=book, reviews=reviews, ratings=ratings)



# API
@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404

@app.route("/api/<isbn>")
def api(isbn):
    if isbn == None:
        abort(404, description="isbn is None")
    book = db.execute("SELECT * from Books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    if book == None:
        abort(404, description="No book exist with this isbn:{} number".format(isbn))
    reviews = db.execute("SELECT COUNT(*) from Reviews WHERE isbn = :isbn", {"isbn": isbn}).fetchall()
    rating = getRequiredRatingData(isbn)
    return jsonify({
            "title": book.title,
            "author": book.author,
            "year": book.year,
            "isbn": book.isbn,
            "review_count": list(reviews[0])[0],
            "average_score": float(rating['average_rating'])
        })


def getRequiredRatingData(isbn):
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"isbns": isbn, "key": 'QRkPc39JGyW3XkL49JaHQ'})
    if res.status_code != 200:
        return None
    output = {}
    data = res.json()['books'][0]
    if 'average_rating' in data:
        output['average_rating'] = data['average_rating']
    else:
        output['average_rating'] = -1
    if 'work_ratings_count' in data:
        output['work_ratings_count'] = data['work_ratings_count']
    else:
        output['work_ratings_count'] = -1
    return output
