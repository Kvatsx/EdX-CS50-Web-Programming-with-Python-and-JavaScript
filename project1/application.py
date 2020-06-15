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

        user = db.execute("SELECT id, name FROM Users WHERE email = :email AND password = :password",{"email": email, "password": password}).fetchone()
        if user != None:
            user = list(user)
            print(user)
            session['user'] = user
            print(session)
            return redirect(url_for("home"))
        else:
            return redirect(url_for('error', message="Wrong Credentials."))
    return render_template("login.html")

@app.route("/home", methods=["GET", "POST"])
def home():
    table_caption = "List of all the books"
    if request.method == "POST":
        search = request.form.get("searchQuery")
        books = db.execute("SELECT * from Books WHERE LOWER(isbn) LIKE :search OR LOWER(title) LIKE :search OR LOWER(author) LIKE :search OR CAST(year AS TEXT) LIKE :search", {"search": '%{}%'.format(search.lower())}).fetchall()
        if len(books) == 0:
            table_caption = "No results found."
        else:
            table_caption = "List of all the books with search query: {}".format(search)
        return render_template("home.html", user_name=session.get('user')[1], books=books ,table_caption=table_caption)
    else:
        print("Logged in:", session)
        if 'user' not in session:
            print("Login now!")
            return redirect(url_for("login"))
        books = db.execute("SELECT * from Books").fetchall()
        print("Book Count:", len(books))
        return render_template("home.html", user_name=session.get('user')[1], books=books ,table_caption=table_caption)

@app.route("/error")
def error():
    return render_template("error.html", message=request.args.get('message'))

@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/logout")
def logout():
    print("[INFO] Logout called!")
    print(session)
    session.pop("user", None)
    print(session)
    return redirect(url_for('index'))


@app.route("/book/<isbn>", methods=["GET", "POST"])
def book(isbn):
    if 'user' not in session:
        return redirect(url_for('error', message="Please Login First"))

    if isbn == None:
        return redirect(url_for('error', message="Invalid Isbn."))
    #  add a review to table
    if request.method == "POST":
        review_title = request.form.get("reviewTitle")
        review_desc = request.form.get("reviewDescription")
        review_rating = request.form.get("rating")
        if review_title == None or review_desc == None or review_rating == None:
            return redirect(url_for("error", message=request.args.get('message')))
        db.execute("INSERT INTO Reviews (rating, title, description, reviewer_id, reviewer_name, isbn) VALUES (:rating, :title, :description, :reviewer_id, :reviewer_name, :isbn)",{
                "rating": int(review_rating), 
                "title": review_title, 
                "description": review_desc,
                "reviewer_id": session.get('user')[0],
                "reviewer_name": session.get('user')[1],
                "isbn": isbn
                })
        db.commit()
    
    add_review = db.execute("SELECT * from Reviews WHERE reviewer_id = :user_id AND isbn = :isbn", {"user_id": session.get("user")[0], "isbn": isbn}).fetchone()
    if add_review == None:
        add_review = True
    else:
        add_review = False
    book = db.execute("SELECT * from Books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    if book == None:
        return redirect(url_for('error', message="No book exists with this isbn: {}.".format(isbn)))
    reviews = db.execute("SELECT * from Reviews WHERE isbn = :isbn", {"isbn": isbn})
    ratings = getRequiredRatingData(isbn)
    if ratings == None:
        return redirect(url_for('error', message="Goodreads Api not working"))
    return render_template("book.html", add_review=add_review, user_name=session.get('user')[1], book=book, reviews=reviews, ratings=ratings)



# API
@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404

@app.route("/api/<isbn>", methods=["GET"])
def api(isbn):
    if isbn == None:
        abort(404, description="isbn is None")
    book = db.execute("SELECT * from Books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    if book == None:
        abort(404, description="No book exist with this isbn: {} number".format(isbn))
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
