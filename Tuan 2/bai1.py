

from flask import Flask, jsonify, request
app = Flask(__name__)
next_id = 1
BOOKS = []

@app.get("/books")
def list_books():
    return jsonify({
    "data": BOOKS,
    "total": len(BOOKS)
    }), 200
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

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)