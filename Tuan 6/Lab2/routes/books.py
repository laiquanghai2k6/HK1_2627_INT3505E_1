import json
import base64
from flask import Blueprint, request, jsonify, abort
from sqlalchemy import select, tuple_
from models import db, Book, Author, BookAuthor, Review

bp = Blueprint("books", __name__, url_prefix="/api/v1/books")

# 1. Whitelist sort keys chống SQL injection (không bao giờ dùng raw tên cột)
SORT_MAP = {
    "id": Book.id,
    "price": Book.price_vnd,
    "title": Book.title
}

def _enc(s):
    return base64.urlsafe_b64encode(json.dumps(s).encode()).decode().rstrip("=")

def _dec(t):
    pad = "=" * (-len(t) % 4)
    return json.loads(base64.urlsafe_b64decode(t + pad).decode())

# --- PHASE 1: Parse Sort & Whitelist ---
def parse_sort(raw):
    if not raw:
        raw = "-id"
    desc = raw.startswith("-")
    key = raw.lstrip("-")
    if key not in SORT_MAP:
        return None, None, 400
    p = SORT_MAP[key]
    # Composite sort: Sắp xếp theo cột chính + tie-break bằng Book.id để tránh trùng lặp[cite: 23, 28]
    cols = [
        p.desc() if desc else p.asc(),
        Book.id.desc() if desc else Book.id.asc()
    ]
    return p, cols, desc

# --- PHASE 2: Apply Cursor ---
def apply_cursor(q, raw, sort, p, desc):
    if not raw:
        return q, None, 200
    try:
        c = _dec(raw)
        if c.get("s") != sort:
            return None, "sort_chg", 400 # Lỗi khi thay đổi sort giữa chừng
        v, i = c["v"], c["i"]
        op = "<" if desc else ">"
        # Điều kiện con trỏ hỗn hợp (Composite cursor)[cite: 23, 24]
        condition = tuple_(p, Book.id).op(op)((v, i))
        return q.filter(condition), None, 200
    except Exception:
        return None, "invalid_cursor", 400

# --- PHASE 3: Build Response ---
def build_response(items, lim, sort, p, more):
    nxt = None
    if items and more:
        last = items[-1]
        nxt = _enc({
            "s": sort,
            "v": getattr(last, p.key),
            "i": last.id
        })
    return jsonify({
        "data": [b.to_dict() for b in items],
        "page": {"next": nxt, "more": more}
    })

# --- ROUTE CHÍNH ---
@bp.get("")
def list_books():
    raw_cursor = request.args.get("cursor")
    lim = min(request.args.get("limit", 20, type=int), 100)
    sort_raw = request.args.get("sort", "-id")
    cat_id = request.args.get("category", type=int)

    # 1. Parse sort
    p, cols, desc = parse_sort(sort_raw)
    if p is None:
        return jsonify({"error": "bad_sort", "message": "Sort key không hợp lệ"}), 400

    q = select(Book).order_by(*cols)

    # 2. Filter theo category nếu có
    if cat_id:
        q = q.filter(Book.category_id == cat_id)

    # 3. Áp dụng Cursor pagination
    q, err, code = apply_cursor(q, raw_cursor, sort_raw, p, desc)
    if err:
        return jsonify({"error": err}), code

    # Lấy dư 1 item (+1 trick) để kiểm tra has_more[cite: 21, 24]
    rows = db.session.scalars(q.limit(lim + 1)).all()
    has_more = len(rows) > lim
    items = rows[:lim]

    return build_response(items, lim, sort_raw, p, has_more)