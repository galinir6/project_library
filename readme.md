# Library Management System

This is my Library Management System implemented using Flask, SQLAlchemy, and JWT for authentication , with html and js connecting to the server with axios. The system allows you to manage books, customers and loans.

## Features

1. **Add Book:**
   - Add a new book to the library database. Supports uploading a book picture.

2. **Loan Book:**
   - Loan a book to a customer. Calculates the return date based on the book type.

3. **Return Book:**
   - Return a book that is currently on loan.

4. **Get All data:**
   - Retrieve all books , users/customers , and loans from the library database , and display in html.

5. **Search Book by Name:**
   - Search for books by name.

6. **Search Customer by Name:**
   - Search for customers by name.

7. **User/customer Registration:**
   - Register a new customer account.

8. **User/customer Login/Logout:**
    - Log in to the system and obtain a JWT token.
    - Log out by removing token from storage.

9. **Show loans of logged in customer:**
    - uses the jwt identity to check who is currently logged in.
    - gets the relevant data and display loans made by that customer

## How to Use

1. **create and activate vitualenv:**
   - create and activate vitualenv to make sure you will only have the correct packages.

2. **Installation:**
   - Clone this repository.
   - Install dependencies: `pip install -r requirements.txt`.

3. **Run the Application:**
   - cd backend in terminal, make sure you are in the right folder.
   - Run `py app.py` in terminal to run server.

4. **use app:**
   - open `index.html` in default browser.
   - make sure to sign up and log in first to get token and use the app functions.
   - if you use the `sign up` unit test, log in with username: gali , and password:123

5. **after log in:**
   - after logging in you can use the unit tests to quickly add data.
   - or add data manually with the app functions. 
   - refresh page if you dont see the added data.


## included pydoc html file but it does not work like it should.



