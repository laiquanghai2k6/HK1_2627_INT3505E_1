from flask import Flask, jsonify, request, make_response, render_template_string

app = Flask(__name__)
next_id = 1
BOOKS = []

OPENAPI_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "Books Management API",
        "version": "1.0.0",
        "description": "Flask REST API with Swagger UI Documentation"
    },
    "paths": {
        "/books": {
            "get": {
                "summary": "Lấy danh sách tất cả sách",
                "responses": {
                    "200": {
                        "description": "Thành công",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "data": {
                                            "type": "array",
                                            "items": {"$ref": "#/components/schemas/Book"}
                                        },
                                        "total": {"type": "integer"}
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "post": {
                "summary": "Tạo mới một quyển sách",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "author": {"type": "string"}
                                },
                                "required": ["title", "author"]
                            }
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "Đã tạo thành công",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Book"}
                            }
                        }
                    },
                    "415": {"description": "Expected JSON"},
                    "422": {"description": "Title và author là bắt buộc"}
                }
            }
        },
        "/books/{bid}": {
            "get": {
                "summary": "Lấy thông tin sách theo ID",
                "parameters": [
                    {"name": "bid", "in": "path", "required": True, "schema": {"type": "integer"}}
                ],
                "responses": {
                    "200": {
                        "description": "Thành công",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Book"}
                            }
                        }
                    },
                    "404": {"description": "Không tìm thấy sách"}
                }
            },
            "put": {
                "summary": "Cập nhật toàn bộ thông tin sách (PUT)",
                "parameters": [
                    {"name": "bid", "in": "path", "required": True, "schema": {"type": "integer"}}
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "t": {"type": "string", "description": "Title mới"},
                                    "a": {"type": "string", "description": "Author mới"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Cập nhật thành công"},
                    "404": {"description": "Không tìm thấy sách"}
                }
            },
            "patch": {
                "summary": "Cập nhật một phần thông tin sách (PATCH)",
                "parameters": [
                    {"name": "bid", "in": "path", "required": True, "schema": {"type": "integer"}}
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "author": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Cập nhật thành công"},
                    "404": {"description": "Không tìm thấy sách"}
                }
            },
            "delete": {
                "summary": "Xóa sách theo ID",
                "parameters": [
                    {"name": "bid", "in": "path", "required": True, "schema": {"type": "integer"}}
                ],
                "responses": {
                    "204": {"description": "Xóa thành công"},
                    "404": {"description": "Không tìm thấy sách"}
                }
            }
        }
    },
    "components": {
        "schemas": {
            "Book": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "author": {"type": "string"},
                    "title": {"type": "string"}
                }
            }
        }
    }
}

@app.get("/openapi.json")
def openapi_spec():
    return jsonify(OPENAPI_SPEC), 200

@app.get("/docs")
def swagger_ui():
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Swagger UI - Books API</title>
        <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
        <style>
            html { box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }
            body { background: #fafafa; margin: 0; }
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js" charset="UTF-8"></script>
        <script>
            window.onload = () => {
                window.ui = SwaggerUIBundle({
                    url: '/openapi.json',
                    dom_id: '#swagger-ui',
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIBundle.SwaggerUIStandalonePreset
                    ],
                    layout: "BaseLayout"
                });
            };
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template), 200


@app.get("/books")
def list_books():
    return jsonify({
        "data": BOOKS,
        "total": len(BOOKS)
    }), 200

@app.get('/books/<int:bid>')
def get_book_from_id(bid):
    book = next((book for book in BOOKS if book['id'] == bid), None)
    if book is None: return jsonify({"error": "notfound"}), 404
    res = make_response(jsonify(book), 200)
    res.headers['Cache-Control'] = 'max-age=120'
    return res

@app.post("/books")
def create_book():
    global next_id
    if not request.is_json:
        return jsonify(error="expected JSON"), 415
    p = request.get_json(silent=True) or {}
    t = (p.get("title") or "").strip()
    a = (p.get("author") or "").strip()
    if not t or not a:
        return jsonify(error="title va author require"), 422
    book = {"id": next_id, "author": a, "title": t}
    next_id += 1
    BOOKS.append(book)
    return jsonify(book), 201

@app.put('/books/<int:bid>')
def put_book(bid):
    i = next((key for key, item in enumerate(BOOKS) if item['id'] == bid), None)
    if i is None: return jsonify({"error": "notfound"}), 404
    body = request.get_json(silent=True) or {}
    a, t = body.get('a'), body.get('t')
    BOOKS[i] = {"id": bid, "author": a, "title": t}
    return jsonify(BOOKS[i]), 200

@app.patch('/books/<int:bid>')
def patch_book(bid):
    i = next((key for key, item in enumerate(BOOKS) if item['id'] == bid), None)
    if i is None: return jsonify({"error": "notfound"}), 404
    body = request.get_json(silent=True) / {} if False else (request.get_json(silent=True) or {})
    for key in "author title".split():
        if key in body:
            BOOKS[i][key] = body[key]
    return jsonify(BOOKS[i]), 200

@app.delete('/books/<int:bid>')
def delete_book(bid):
    i = next((key for key, item in enumerate(BOOKS) if item['id'] == bid), None)
    if i is None: return jsonify({"error": "notfound"}), 404
    BOOKS.pop(i)  # Đã sửa lỗi .pops() thành .pop()
    return "", 204

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)