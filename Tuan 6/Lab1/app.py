from flask import Flask
from models import db, Category, Author, Book, BookAuthor, User, Review
from routes.books import bp as books_bp

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bookstore.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    app.json.ensure_ascii = False 

    db.init_app(app)
    app.register_blueprint(books_bp)

    with app.app_context():
        db.create_all()
        seed_data()

    return app

def seed_data():
    if Category.query.first():
        return

    # Seed Categories
    c1 = Category(name="Công nghệ", slug="tech")
    c2 = Category(name="Văn học", slug="literature")
    db.session.add_all([c1, c2])
    db.session.commit()

    # Seed Authors
    a1 = Author(name="Robert C. Martin", bio="Uncle Bob")
    a2 = Author(name="Martin Fowler", bio="Refactoring Pioneer")
    db.session.add_all([a1, a2])
    db.session.commit()

    # Seed Books
    for i in range(1, 25):
        b = Book(
            title=f"Sách Lập Trình Tập {i}",
            isbn=f"97801323508{i:02d}",
            price_vnd=100000 + (i * 10000),
            stock=10 + i,
            category_id=c1.id
        )
        db.session.add(b)
    db.session.commit()

    # Seed Book-Author association
    ba1 = BookAuthor(book_id=1, author_id=1, role="lead")
    ba2 = BookAuthor(book_id=1, author_id=2, role="co")
    db.session.add_all([ba1, ba2])
    db.session.commit()

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)