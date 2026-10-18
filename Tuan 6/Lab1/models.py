from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Table, Column, Integer, String, Text, DateTime, func

db = SQLAlchemy()

class BookAuthor(db.Model):
    __tablename__ = 'book_authors'
    
    book_id: Mapped[int] = mapped_column(ForeignKey('books.id'), primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey('authors.id'), primary_key=True)
    role: Mapped[str] = mapped_column(String(50), default='co') 

    book: Mapped["Book"] = relationship(back_populates="author_associations")
    author: Mapped["Author"] = relationship(back_populates="book_associations")


class Category(db.Model):
    __tablename__ = 'categories'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    books: Mapped[list["Book"]] = relationship(back_populates="category")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "slug": self.slug}


class Author(db.Model):
    __tablename__ = 'authors'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    bio: Mapped[str] = mapped_column(Text, nullable=True)

    book_associations: Mapped[list["BookAuthor"]] = relationship(back_populates="author")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "bio": self.bio}


class User(db.Model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)

    reviews: Mapped[list["Review"]] = relationship(back_populates="user")

    def to_dict(self):
        return {"id": self.id, "email": self.email, "display_name": self.display_name}


class Book(db.Model):
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    isbn: Mapped[str] = mapped_column(String(13), nullable=True)
    price_vnd: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'), nullable=False)

    category: Mapped["Category"] = relationship(back_populates="books")
    author_associations: Mapped[list["BookAuthor"]] = relationship(back_populates="book", cascade="all, delete-orphan")
    reviews: Mapped[list["Review"]] = relationship(back_populates="book", cascade="all, delete-orphan")

    def to_dict(self, fields=None):
        full = {
            "id": f"book_{self.id}",
            "numeric_id": self.id,
            "title": self.title,
            "isbn": self.isbn,
            "price_vnd": self.price_vnd,
            "stock": self.stock,
            "category": self.category.to_dict() if self.category else None,
            "authors": [
                {"id": ba.author.id, "name": ba.author.name, "role": ba.role}
                for ba in self.author_associations
            ]
        }
        if fields is None:
            return full
        return {k: v for k, v in full.items() if k in fields}


class Review(db.Model):
    __tablename__ = 'reviews'

    id: Mapped[int] = mapped_column(primary_key=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    book_id: Mapped[int] = mapped_column(ForeignKey('books.id'), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

    book: Mapped["Book"] = relationship(back_populates="reviews")
    user: Mapped["User"] = relationship(back_populates="reviews")

    def to_dict(self):
        return {
            "id": self.id,
            "rating": self.rating,
            "content": self.content,
            "book_id": self.book_id,
            "user_id": self.user_id
        }