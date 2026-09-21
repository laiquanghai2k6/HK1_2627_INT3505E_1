

from flask import Flask, jsonify, request,make_response
app = Flask(__name__)
next_id = 1
BOOKS = []

@app.get("/books")
def list_books():
    return jsonify({
    "data": BOOKS,
    "total": len(BOOKS)
    }), 200

@app.get('/books/<int:bid>')
def get_book_from_id(bid):
    book = next((book for book in BOOKS if book['id']==bid),None)
    if book is None: return jsonify({"error":"notfound"}),404
    res = make_response(jsonify(book),200)
    res.headers['Cache-Control'] = 'max-age=120'
    return res

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