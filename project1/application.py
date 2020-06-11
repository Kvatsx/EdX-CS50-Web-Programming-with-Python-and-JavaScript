import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *

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
    return render_template("index.html")


@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("RegisterFullName")
    email = request.form.get("RegisterInputEmail")
    password = request.form.get("RegisterInputPassword")

    # TODO: Check for existing user
    user = User(name=name, email=email, password=password)
    db.add(user)
    db.commit()
    user.print_info()
    return render_template("success.html")


@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("LoginInputEmail")
    password = request.form.get("LoginInputPassword")
    user = User.query.filter_by(email == email).first()
    print(user.id)
    return render_template("success.html")