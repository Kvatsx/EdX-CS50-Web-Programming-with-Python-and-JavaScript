import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    create_tables()

    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:

        db.execute("INSERT INTO Books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)", {
            "isbn": isbn,
            "title": title,
            "author": author,
            "year": year
        })
    db.commit()


def create_tables():

    # Clean Database
    # db.execute("DROP TABLE Users;")
    # db.execute("DROP TABLE Books;")
    # db.execute("DROP TABLE Reviews;")

    # Create Tables
    db.execute('''
        CREATE TABLE Users (
            id SERIAL PRIMARY KEY,
            name VARCHAR NOT NULL,
            email VARCHAR NOT NULL UNIQUE,
            password VARCHAR NOT NULL
        );
    ''')

    db.execute('''
        CREATE TABLE Books (
            isbn VARCHAR PRIMARY KEY,
            title VARCHAR NOT NULL,
            author VARCHAR NOT NULL,
            year INTEGER NOT NULL
        );
    ''')

    db.execute('''
        CREATE TABLE Reviews (
            id SERIAL PRIMARY KEY,
            rating INTEGER NOT NULL,
            title VARCHAR NOT NULL,
            description VARCHAR NOT NULL,
            reviewer_id INTEGER NOT NULL,
            reviewer_name VARCHAR NOT NULL,
            isbn VARCHAR NOT NULL
        );
    ''')

    db.commit()

if __name__ == "__main__":
    main()