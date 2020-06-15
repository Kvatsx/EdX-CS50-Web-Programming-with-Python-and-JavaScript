# Project 1

Web Programming with Python and JavaScript

Directory Structure
```
project1
│   README.md
│   requirements.txt
|   books.csv    
|   imports.py
|   application.py
│
└───templates
│   │   layout.html
│   │   login.html
│   │   register.html
│   │   home.html
│   │   book.html
│   │   success.html
│   │   error.html
│   
└───static
    │   forms.css
    │   home.css
    |   book.css
```

Database-

`import.py` - Funtions in this file create a database with 3 tables (User, Books and Reviews). To run this file `python3 import.py`.


Description-

`application.py` - Initialize a flask application. Set database parameters. Contains all the functions with routes.

Explanation of each function with their corresponding html file and css file.
- `index()` - It redirects the user to "/login" route (Login page).
- `login()` - This function renders login page. For post request, it checks for the record with email id and password in User Table and redirects the user to "/home" page if credentials were correct.
    - HTML_File - `login.html`
    - CSS_FILE - `forms.css`
    - route - `/login`

- `register()` - This function registers a new user. It also checks if user with same email id exists in database or not. 
    - HTML_FILE - `register.html`
    - CSS_FILE - `forms.css`
    - route - `/register`

- `home()` - It renders the page with all the books in the database. It also provides a search box where a user can search for the books with the isbn number, title, author or year. If no book found based on search query, page renders and shows that no results were found with this query.
    - HTML_FILE - `home.html`
    - CSS_FILE - `home.css`
    - route - `/home`

- `book(isbn)` - This html file renders the page with book details like title, author, year, isbn, ratings from the api call. It contains a review form for the book. It shows all the previous reviews as well.
    - HTML_FILE - `book.html`
    - CSS_FILE - `book.css`
    - route - `/book/<isbn>`

- `getRequiredRatingData(isbn)` - This functions does an api call using goodreads api and key. It returns a json object with average_rating and work_rating_count.

- `api(isbn)` - This function does multiple query to the database. First query is to get the details of the book from books table using the given isbn number. Second query is to get reviews from Reviews table using the given isbn number. This function also handles all the possible errors and return the 404 with an error description.
    - route - `/api/<isbn>`

- `error()` - This functions renders the error page with proper error description.
    - HTML_FILE - `error.html`
    - route - `/error`

- `success()` - This functions renders the success page with the proper message.
    - HTML_FILE - `success.html`
    - route - `/success`

