import json
import base64
from flask import Blueprint, request, jsonify
from sqlalchemy import select, func
from models import db, Book, Category

bp = Blueprint("books", __name__, url_prefix="/api/v1/books")

ALLOWED_SORT_FIELDS = {
    "id": Book.id,
    "price": Book.price_vnd,
    "title": Book.title,
    "stock": Book.stock
}

def _enc(s):
    return base64.urlsafe_b64encode(json.dumps(s).encode()).decode().rstrip("=")

def _dec(t):
    pad = "=" * (-len(t) % 4)
    return json.loads(base64.urlsafe_b64decode(t + pad).decode())

def parse_multi_sort(raw_sort):
    if not raw_sort:
        raw_sort = "-id"
    
    cols = []
    for s in raw_sort.split(","):
        s = s.strip()
        desc = s.startswith("-")
        key = s.lstrip("-")
        
        if key not in ALLOWED_SORT_FIELDS:
            return None, 400
            
        col = ALLOWED_SORT_FIELDS[key]
        cols.append(col.desc() if desc else col.asc())
        
    if not any(k.lstrip("-") == "id" for k in raw_sort.split(",")):
        cols.append(Book.id.desc())
        
    return cols, 200

@bp.get("")
def list_books():
    strategy = request.args.get("strategy", "cursor") 
    limit = min(request.args.get("limit", 20, type=int), 100)
    sort_raw = request.args.get("sort", "-id")
    genre = request.args.get("genre")  

    cols, code = parse_multi_sort(sort_raw)
    if code != 200:
        return jsonify({"error": "bad_sort", "message": "Sort key không hợp lệ trong whitelist"}), 400

    q = select(Book).order_by(*cols)

    if genre:
        q = q.join(Book.category).filter(Category.slug == genre)

    if strategy == "offset":
        offset = request.args.get("offset", 0, type=int)
        total = db.session.scalar(select(func.count(Book.id)).select_from(Book))
        
        if genre:
            count_q = select(func.count(Book.id)).join(Book.category).filter(Category.slug == genre)
            total = db.session.scalar(count_q)

        rows = db.session.scalars(q.offset(offset).limit(limit)).all()
        
        return jsonify({
            "data": [b.to_dict() for b in rows],
            "pagination": {
                "strategy": "offset",
                "offset": offset,
                "limit": limit,
                "total": total,
                "has_next": offset + limit < total
            }
        })
        
    else:
        cursor_raw = request.args.get("cursor")
        
        if cursor_raw:
            try:
                cursor_data = _dec(cursor_raw)
                last_id = cursor_data.get("id")
                q = q.filter(Book.id > last_id)
            except Exception:
                return jsonify({"error": "invalid_cursor", "message": "Cursor không hợp lệ"}), 400

        rows = db.session.scalars(q.limit(limit + 1)).all()
        has_more = len(rows) > limit
        items = rows[:limit]

        next_cursor = None
        if items and has_more:
            next_cursor = _enc({"id": items[-1].id})

        return jsonify({
            "data": [b.to_dict() for b in items],
            "pagination": {
                "strategy": "cursor",
                "next_cursor": next_cursor,
                "has_more": has_more,
                "limit": limit
            }
        })