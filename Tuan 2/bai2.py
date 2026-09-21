

from flask import Flask, jsonify, request,make_response
app = Flask(__name__)
next_id = 1
BOOKS = []
DEFAULT_SIZE = 10
MAX_SIZE = 100
BOOKS = []  # Danh sách dữ liệu mẫu


@app.get("/books")
def list_books():
    try:
        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", DEFAULT_SIZE))
    except ValueError:
        return jsonify(error="page va size phai interger"), 400

    page = max(page, 1)
    size = max(min(size, MAX_SIZE), 1)

    author = request.args.get("author")
    q = (request.args.get("q") or "").strip().lower()

    flt = BOOKS
    if author:
        flt = [b for b in flt if b.get("author", "").lower() == author.lower()]
    if q:
        flt = [b for b in flt if q in b.get("title", "").lower()]

    total = len(flt)
    start = (page - 1) * size
    end = start + size
    items = flt[start:end]
    last = (total + size - 1) // size if total > 0 else 1

    def make_url(p):
        query_params = f"page={p}&size={size}"
        if author:
            query_params += f"&author={author}"
        if q:
            query_params += f"&q={q}"
        return f"/books?{query_params}"

    links = {
        "self": {"href": make_url(page)},
        "first": {"href": make_url(1)},
        "last": {"href": make_url(last)},
    }
    if page > 1:
        links["prev"] = {"href": make_url(page - 1)}
    if end < total:
        links["next"] = {"href": make_url(page + 1)}

    body = {
        "data": items,
        "pagination": {
            "page": page,
            "size": size,
            "total": total,
            "total_pages": last,
        },
        "_links": links,
    }

    resp = make_response(jsonify(body), 200)
    resp.headers["Cache-Control"] = "public, max-age=30"
    return resp

@app.post("/books")
def create_book():
    if not request.is_json:
        return jsonify(error="expected JSON"), 415
    p = request.get_json(silent=True) or {}
    t = (p.get("title") or"").strip()
    a = (p.get("author") or"").strip()
    if not t or not a:
        return jsonify(error="title va author require"), 422
    book = {"id":next_id,"author":a,"title":t}
    next_id+=1
    BOOKS.append(book)
    return jsonify(book),201

@app.put('/books/<int:bid>')
def put_book(bid):
    i = next((key for key,item in enumerate(BOOKS) if item['id']==bid),None)
    if i is None: return jsonify({"error":"notfound"}),404
    body = request.get_json(silent=True) or {}
    a,t = body.get('a'),body.get('t')
    BOOKS[i] = {"id":bid,"author":a,"title":t}
    return jsonify(BOOKS[i]), 200

@app.patch('/books/<int:bid>')
def patch_book(bid):
    i = next((key for key,item in enumerate(BOOKS) if item['id']==bid),None)
    if i is None: return jsonify({"error":"notfound"}),404
    body = request.get_json(silent=True) or {}
    for key in "author title".split():
        if key in body:
            BOOKS[i][key] = body[key]
    return jsonify(BOOKS[i]), 200

@app.delete('/books/<int:bid>')
def delete_book(bid):
    i = next((key for key,item in enumerate(BOOKS) if item['id']==bid),None)
    if i is None: return jsonify({"error":"notfound"}),404
    BOOKS.pops(i)
    return "", 204

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)