from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_httpauth import HTTPBasicAuth
import os

auth = HTTPBasicAuth()
# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)


# Product  Class/Model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    author = db.Column(db.String(30))
    pages = db.Column(db.Integer)
    price = db.Column(db.Float)

    def __init__(self, title, author, pages, price):
        self.title = title
        self.author = author
        self.pages = pages
        self.price = price


# Book Schema
class BookSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'author', 'pages', 'price')


# Init Schema
book_schema = BookSchema(strict=True)
books_schema = BookSchema(many=True, strict=True)


# Create a Book
@app.route('/Book', methods=['POST'])
def add_book():
    title = request.json['title']
    author = request.json['author']
    pages = request.json['pages']
    price = request.json['price']

    new_book = Book(title, author, pages, price)

    db.session.add(new_book)
    db.session.commit()

    return book_schema.jsonify(new_book)


# Get all books
@app.route('/Books', methods=['GET'])
@auth.login_required
def get_books():
    all_books = Book.query.all()
    result = books_schema.dump(all_books)
    return jsonify(result.data)


# Get single book
@app.route('/Book/<id>', methods=['GET'])
def get_book(id):
    book = Book.query.get(id)
    return book_schema.jsonify(book)


# Update a Book
@app.route('/Book/<id>', methods=['PUT'])
def update_book(id):
    book = Book.query.get(id)

    title = request.json['title']
    author = request.json['author']
    pages = request.json['pages']
    price = request.json['price']

    book.title = title
    book.author = author
    book.pages = pages
    book.price = price

    db.session.commit()

    return book_schema.jsonify(book)


# Delete single book
@app.route('/Book/<id>', methods=['DELETE'])
def delete_book(id):
    book = Book.query.get(id)
    db.session.delete(book)
    db.session.commit()

    return book_schema.jsonify(book)


# Migration
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db_migrate', MigrateCommand)


@auth.get_password
def get_password(username):
    if username == 'Admin':
        return 'python'
    return None


@auth.error_handler
def authorized():
    return make_response(jsonify({'error':'Unauthorized access'}), 401)


# Run server
if __name__ == '__main__':
    app.run(debug=True)

