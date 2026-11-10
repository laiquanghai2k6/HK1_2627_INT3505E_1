from contextlib import contextmanager

import pytest
from sqlalchemy import event

from product_api.config import TestConfig
from product_api.extensions import db
from product_api.factory import create_app


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def make_product(client):
    def _make(**overrides):
        payload = {"sku": "SKU-001", "name": "Laptop", "price_cents": 1000, "qty_in_stock": 5}
        payload.update(overrides)
        return client.post("/api/v1/products", json=payload)

    return _make


@pytest.fixture()
def make_order(client):
    def _make(customer_name="An", items=None):
        payload = {
            "customer_name": customer_name,
            "items": items if items is not None else [{"product_id": 1, "quantity": 1}],
        }
        return client.post("/api/v1/orders", json=payload)

    return _make


@pytest.fixture()
def count_queries(app):
    """Context manager ghi lai cac cau SQL thuc su gui toi DB."""

    @contextmanager
    def _counter():
        statements = []

        def _before(conn, cursor, statement, parameters, context, executemany):
            statements.append(statement)

        event.listen(db.engine, "before_cursor_execute", _before)
        try:
            yield statements
        finally:
            event.remove(db.engine, "before_cursor_execute", _before)

    return _counter
