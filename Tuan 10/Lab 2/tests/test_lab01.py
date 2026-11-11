"""LAB 1 — add your five tests here. Do not delete the smoke tests.

A. GET /books, empty database -> HTTP 200 and []
B. GET /books/9999 -> HTTP 404, JSON code == NOT_FOUND
C. POST /books with only author -> HTTP 400, errors contains title
D. POST valid book, DELETE it, GET same id -> HTTP 404
BONUS. Validate a Book response using JSON Schema; add an unknown
       field to a *copy* of the response and assert ValidationError.

Useful imports:
    from jsonschema import validate, ValidationError
    import pytest
    from tools import get_book_schema

Do not depend on test execution order. Fixtures: client, app, sample_book.
"""

import copy

import pytest
from jsonschema import ValidationError, validate

from tools import get_book_schema


def test_list_books_empty_returns_empty_array(client):
    response = client.get("/books")
    assert response.status_code == 200
    assert response.get_json() == []


def test_get_missing_book_returns_404_not_found(client):
    response = client.get("/books/9999")
    assert response.status_code == 404
    assert response.get_json()["code"] == "NOT_FOUND"


def test_create_book_without_title_returns_400(client):
    response = client.post("/books", json={"author": "Only Author"})
    assert response.status_code == 400
    body = response.get_json()
    assert any(err["field"] == "title" for err in body["errors"])


def test_deleted_book_is_gone(client):
    created = client.post("/books", json={"title": "Temp", "author": "Someone"})
    assert created.status_code == 201
    book_id = created.get_json()["id"]

    deleted = client.delete(f"/books/{book_id}")
    assert deleted.status_code == 204

    response = client.get(f"/books/{book_id}")
    assert response.status_code == 404



def test_response_extra_field_blocked(client, sample_book):
    schema = get_book_schema()
#     {
#     "type": "object",
#     "additionalProperties": False,
#     "required": ["id", "title", "author", "year", "isbn"],
#     "properties": {
#         "id": {"type": "integer", "minimum": 1},
#         "title": {"type": "string", "minLength": 1, "maxLength": 200},
#         "author": {"type": "string", "minLength": 1, "maxLength": 200},
#         "year": {"type": "string", "nullable": True},
#         "isbn": {"type": "string", "pattern": r"^\d{13}$", "nullable": True},
#     },
# }
    schema["properties"]["year"]["type"] = "integer"

    for prop in schema["properties"].values():
        if prop.pop("nullable", False):
            prop["type"] = [prop["type"], "null"]
    
    body = client.get(f"/books/{sample_book}").get_json()

    validate(body, schema)  

    leaked = copy.deepcopy(body)
    leaked["password_hash"] = "abc123"  
    with pytest.raises(ValidationError):
        validate(leaked, schema)

        