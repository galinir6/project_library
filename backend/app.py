from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
import datetime
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app = Flask(__name__, static_url_path='/static')

# Configure JWT settings
app.config["JWT_SECRET_KEY"] = "your-secret-key"  
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(
    hours=1
)  #the expiration time for token
app.config["JWT_ALGORITHM"] = "HS256"  # the algorithm for token

# Initialize JWT extension
jwt = JWTManager(app)

app.secret_key = "mykey"

bcrypt = Bcrypt(app)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

CORS(app)

# create table for books
class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    year_published = db.Column(db.Integer, nullable=False)
    type = db.Column(db.Integer)
    picture = db.Column(db.String(255))  

# create table for customers
class Customers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer)
    password = db.Column(db.String(255), nullable=False)

# create table for loans
class Loans(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cust_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    loan_date = db.Column(db.Date)
    return_date = db.Column(db.Date)

    # Define the relationships
    customer = db.relationship('Customers', backref='loans')
    book = db.relationship('Books', backref='loans')

# Create the database tables if dont exist
with app.app_context():
    db.create_all()


# adding new book
@app.route("/addBook", methods=['POST'])
@jwt_required()
def addBook():
    if request.method == 'POST':
        name = request.form['name']
        author = request.form['author']
        year_published = request.form['year_published']
        type = request.form['type']

        # Handle file upload
        picture = None
        if 'picture' in request.files:
            picture_file = request.files['picture']
            if picture_file:
                picture_path = f"static/uploads/{picture_file.filename}"
                picture_file.save(picture_path)
                picture = picture_path

        # If picture is not provided, use a default picture URL
        if picture is None:
            picture = "static/uploads/harrypotter.jpg"

        # Create a new book including the picture path
        new_book = Books(name=name, author=author, year_published=year_published, type=type, picture=picture)
        db.session.add(new_book)
        db.session.commit()

    return {"add": "done"}


# adding new loan
@app.route("/loanBook", methods=['POST'])
@jwt_required()
def loanBook():
    if request.method == 'POST':
        cust_name = request.form['cust_name']
        book_name = request.form['book_name']

        # Check if the customer and book exist
        customer = Customers.query.filter_by(name=cust_name).first()
        book = Books.query.filter_by(name=book_name).first()

        if customer is None or book is None:
            return jsonify({"error": "Customer or Book not found"}), 404

        # Check if the book is available for loan
        if Loans.query.filter_by(book_id=book.id).first():
            return jsonify({"error": "Book is already on loan"}), 400

        # Calculate the return date based on the book type
        if book.type == 1:
            return_date = datetime.datetime.now() + timedelta(days=10)
        elif book.type == 2:
            return_date = datetime.datetime.now() + timedelta(days=5)
        elif book.type == 3:
            return_date = datetime.datetime.now() + timedelta(days=2)
        else:
            return jsonify({"error": "Invalid book type"}), 400

        # Create a new loan 
        new_loan = Loans(cust_id=customer.id, book_id=book.id, loan_date=datetime.datetime.now(), return_date=return_date)
        db.session.add(new_loan)
        db.session.commit()

        return {"loan_status": "success", "return_date": return_date.strftime("%Y-%m-%d")}


# returning a book
@app.route("/returnBook", methods=['POST'])
@jwt_required()
def returnBook():
    if request.method == 'POST':
        cust_name = request.form['cust_name']
        book_name = request.form['book_name']

        # Check if the customer and book exist
        customer = Customers.query.filter_by(name=cust_name).first()
        book = Books.query.filter_by(name=book_name).first()

        if customer is None or book is None:
            return jsonify({"error": "Customer or Book not found"}), 404

        # Check if the book is on loan to the customer
        loan = Loans.query.filter_by(cust_id=customer.id, book_id=book.id).first()

        if loan is None:
            return jsonify({"error": "Book is not on loan to this customer"}), 400

        # Update the return date to the current date
        loan.return_date = datetime.datetime.now()
        db.session.commit()

        # Remove from the Loans table
        db.session.delete(loan)
        db.session.commit()

        return {"return_status": "success"}


# getting all data from books table
@app.route("/getAllBooks", methods=['GET'])
@jwt_required()
def getAllBooks():
    # get all books from the database
    all_books = Books.query.all()

    # Prepare the response data
    books_data = []
    for book in all_books:
        books_data.append({
            'id': book.id,
            'name': book.name,
            'author': book.author,
            'year_published': book.year_published,
            'type': book.type,
            'picture': book.picture})

    return jsonify(books_data)



# getting all data from books table (FOR RENDER)
@app.route("/", methods=['GET'])
def get_render():
    # get all books from the database
    all_books = Books.query.all()

    # Prepare the response data
    books_data = []
    for book in all_books:
        books_data.append({
            'id': book.id,
            'name': book.name,
            'author': book.author,
            'year_published': book.year_published,
            'type': book.type,
            'picture': book.picture})

    return jsonify(books_data)




# getting all data from customres table
@app.route("/getAllCustomers", methods=['GET'])
@jwt_required()
def getAllCustomers():
    # get all customers from the database
    all_customers = Customers.query.all()

    # Prepare the response data
    customers_data = []
    for customer in all_customers:
        customers_data.append({
            'id': customer.id,
            'name': customer.name,
            'city': customer.city,
            'age': customer.age
        })

    return jsonify(customers_data)


# getting all data from loans table
@app.route("/getAllLoans", methods=['GET'])
@jwt_required()
def getAllLoans():
    # get all loans from the database, including book and customer details
    all_loans = db.session.query(Loans, Books.name.label('book_name'), Customers.name.label('customer_name')) \
        .join(Books, Loans.book_id == Books.id) \
        .join(Customers, Loans.cust_id == Customers.id) \
        .all()

    # Prepare the response data
    loans_data = []
    for loan, book_name, customer_name in all_loans:
        loans_data.append({
            'id': loan.id,
            'customer_name': customer_name,
            'book_name': book_name,
            'loan_date': loan.loan_date.strftime("%Y-%m-%d"),
            'return_date': loan.return_date.strftime("%Y-%m-%d") if loan.return_date else None
        })

    return jsonify(loans_data)


# adding new user 
@app.route("/signup", methods=["POST"])
def signup():
    name = request.form.get("name")
    city = request.form.get("city")
    age = request.form.get("age")
    password = request.form.get("password")

    # Check if customer already exists
    existing_customer = Customers.query.filter_by(name=name).first()
    if existing_customer:
        return (
            jsonify({"error": "Customer already exists! Please choose a different name."}),
            400,
        )

    # Hash the password before storing it
    hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

    # Add new customer to the database
    new_customer = Customers(name=name, city=city, age=age, password=hashed_pw)
    db.session.add(new_customer)
    db.session.commit()

    return jsonify(
        {
            "message": f"Successfully signed up! Welcome, {name}.",
            "redirect": "login.html",
        }
    )


# login and getting token
@app.route("/login", methods=["POST"])
def login():
    name = request.form.get("name")
    password = request.form.get("password")

    # Check if the customer exists
    customer = Customers.query.filter_by(name=name).first()

    if customer and bcrypt.check_password_hash(customer.password, password):
        # Generate access token
        access_token = create_access_token(identity=name)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"error": "Invalid name or password"}), 401


# search book by name
@app.route("/searchBookByName", methods=['GET'])
@jwt_required()
def searchBookByName():
    # Get the book name from the query parameters
    book_name = request.args.get('name')

    if not book_name:
        return jsonify({"error": "Book name parameter is required"}), 400

    # Search for books by name
    matching_books = Books.query.filter(Books.name.ilike(f"%{book_name}%")).all()

    # Prepare the response data
    books_data = []
    for book in matching_books:
        books_data.append({
            'id': book.id,
            'name': book.name,
            'author': book.author,
            'year_published': book.year_published,
            'type': book.type,
            'picture': book.picture
        })

    return jsonify(books_data)


# search customer by name
@app.route("/searchCustomerByName", methods=['GET'])
@jwt_required()
def searchCustomerByName():
    # Get the customer name from the query parameters
    customer_name = request.args.get('name')

    if not customer_name:
        return jsonify({"error": "Customer name parameter is required"}), 400

    # Search for customers by name
    matching_customers = Customers.query.filter(Customers.name.ilike(f"%{customer_name}%")).all()

    # Prepare the response data
    customers_data = []
    for customer in matching_customers:
        customers_data.append({
            'id': customer.id,
            'name': customer.name,
            'city': customer.city,
            'age': customer.age
        })

    return jsonify(customers_data)


# function to get loans of customer that is logged in
@app.route("/customerLoanHistory", methods=['GET'])
@jwt_required()
def customerLoanHistory():
    # Get the customer's identity from the JWT token
    customer_identity = get_jwt_identity()

    # Find the customer in the database
    customer = Customers.query.filter_by(name=customer_identity).first()
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    # Query for loans associated with the customer
    customer_loans = Loans.query.filter_by(cust_id=customer.id).all()

    # Prepare the response data
    loans_history = []
    for loan in customer_loans:
        book = Books.query.get(loan.book_id)
        loans_history.append({
            'loan_id': loan.id,
            'book_name': book.name,
            'loan_date': loan.loan_date.strftime("%Y-%m-%d"),
            'return_date': loan.return_date.strftime("%Y-%m-%d") if loan.return_date else None
        })

    return jsonify(loans_history)


if __name__ == '__main__':
    app.run(debug=True)