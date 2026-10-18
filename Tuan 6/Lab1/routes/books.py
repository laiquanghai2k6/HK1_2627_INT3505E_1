import json
import base64
from flask import Blueprint, request, jsonify, abort
from jsonschema import validate, ValidationError
from sqlalchemy import select, tuple_
from models import db, Book, Author, BookAuthor, Review

bp = Blueprint("books", __name__, url_prefix="/api/v1/books")

with open("schemas/book.json", "r") as f:
    BOOK_SCHEMA = json.load(f)

SORT_MAP = {
    "id": Book.id,
    "price": Book.price_vnd,
    "title": Book.title
}


def _encode_cursor(data: dict) -> str:
    return base64.urlsafe_b64encode(json.dumps(data).encode()).decode().rstrip("=")

def _decode_cursor(token: str) -> dict:
    pad = "=" * (-len(token) % 4)
    return json.loads(base64.urlsafe_b64encode(token + pad).decode())

def parse_sort(raw_sort: str):
    desc = raw_sort.startswith("-")
    key = raw_sort.lstrip("-")
    
    if key not in SORT_MAP:
        return None, None, False
    
    prop = SORT_MAP[key]
    cols = [
        prop.desc() if desc else prop.asc(),
        Book.id.desc() if desc else Book.id.asc()
    ]
    return prop, cols, desc

def apply_cursor(q, cursor_raw: str, sort_param: str, prop, desc: bool):
    if not cursor_raw:
        return q, None
    try:
        c = _decode_cursor(cursor_raw)
        if c.get("s") != sort_param:
            return None, ("sort_mismatch", "Con trỏ không khớp với kiểu sắp xếp hiện tại", 400)
        
        val, last_id = c["v"], c["i"]
        op = "<" if desc else ">"
        
        condition = tuple_(prop, Book.id).op(op)((val, last_id))
        return q.filter(condition), None
    except Exception:
        return None, ("invalid_cursor", "Mã cursor không hợp lệ", 400)

def build_response(items, limit: int, sort_param: str, prop, has_more: bool):
    next_cursor = None
    if items and has_more:
        last = items[-1]
        next_cursor = _encode_cursor({
            "s": sort_param,
            "v": getattr(last, prop.key),
            "i": last.id
        })
    
    return jsonify({
        "data": [b.to_dict() for b in items],
        "pagination": {
            "next_cursor": next_cursor,
            "has_more": has_more,
            "limit": limit
        }
    })


@bp.get("")
def list_books():
    cursor_raw = request.args.get("cursor")
    limit = min(request.args.get("limit", 20, type=int), 100)
    sort_param = request.args.get("sort", "-id")
    category_id = request.args.get("category", type=int)
    
    prop, cols, desc = parse_sort(sort_param)
    if prop is None:
        return jsonify({"error": "invalid_sort", "message": f"Sort key không hợp lệ. Cho phép: {list(SORT_MAP.keys())}"}), 400
    
    q = select(Book).order_by(*cols)
    
    if category_id:
        q = q.filter(Book.category_id == category_id)
        
    q, err = apply_cursor(q, cursor_raw, sort_param, prop, desc)
    if err:
        return jsonify({"error": err[0], "message": err[1]}), err[2]
        
    rows = db.session.scalars(q.limit(limit + 1)).all()
    has_more = len(rows) > limit
    items = rows[:limit]
    
    return build_response(items, limit, sort_param, prop, has_more)

@bp.post("")
def create_book():
    payload = request.get_json(silent=True) or {}
    try:
        validate(instance=payload, schema=BOOK_SCHEMA)
    except ValidationError as e:
        return jsonify({
            "error": "validation_failed",
            "field": list(e.path),
            "message": e.message
        }), 400
        
    book = Book(
        title=payload["title"],
        isbn=payload.get("isbn"),
        price_vnd=payload["price_vnd"],
        stock=payload.get("stock", 0),
        category_id=payload["category_id"]
    )
    db.session.add(book)
    db.session.commit()
    return jsonify(book.to_dict()), 201

@bp.get("/<int:bid>")
def get_book(bid):
    book = db.session.get(Book, bid)
    if not book:
        abort(404)
    return jsonify(book.to_dict())

@bp.get("/<int:bid>/reviews")
def list_book_reviews(bid):
    book = db.session.get(Book, bid)
    if not book:
        abort(404)
    return jsonify([r.to_dict() for r in book.reviews])

@bp.post("/<int:bid>/authors")
def add_author_to_book(bid):
    book = db.session.get(Book, bid)
    if not book:
        abort(404)
    
    payload = request.get_json(silent=True) or {}
    author_id = payload.get("author_id")
    role = payload.get("role", "co")
    
    if not author_id or not db.session.get(Author, author_id):
        return jsonify({"error": "invalid_author", "message": "Author ID không tồn tại"}), 400
        
    assoc = BookAuthor(book_id=bid, author_id=author_id, role=role)
    db.session.add(assoc)
    db.session.commit()
    
    return jsonify({"message": "Gắn tác giả thành công", "book_id": bid, "author_id": author_id, "role": role}), 201