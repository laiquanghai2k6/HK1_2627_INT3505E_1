import pytest

from product_api.extensions import db

ORDERS = "/api/v1/orders"
PRODUCTS = "/api/v1/products"


@pytest.fixture()
def two_products(make_product):
    make_product(sku="SKU-001", name="Laptop", price_cents=1000)
    make_product(sku="SKU-002", name="Mouse", price_cents=250)


# ─── POST /orders ───
def test_create_order_with_many_products(two_products, make_order):
    r = make_order(
        customer_name="An",
        items=[{"product_id": 1, "quantity": 2}, {"product_id": 2, "quantity": 4}],
    )
    assert r.status_code == 201
    data = r.get_json()
    assert data["customer_name"] == "An"
    assert len(data["items"]) == 2
    assert data["items"][0]["product_name"] == "Laptop"
    assert data["items"][1]["unit_price_cents"] == 250
    assert data["total_cents"] == 2 * 1000 + 4 * 250


def test_order_keeps_price_snapshot(two_products, make_order, client):
    make_order(items=[{"product_id": 1, "quantity": 1}])
    client.patch(f"{PRODUCTS}/1", json={"price_cents": 9999})
    data = client.get(f"{ORDERS}/1").get_json()
    assert data["items"][0]["unit_price_cents"] == 1000


def test_create_order_unknown_product_422(two_products, make_order):
    r = make_order(items=[{"product_id": 99, "quantity": 1}])
    assert r.status_code == 422
    assert r.get_json()["error"] == "validation_error"


def test_create_order_archived_product_422(two_products, make_order, client):
    client.delete(f"{PRODUCTS}/2")
    r = make_order(items=[{"product_id": 2, "quantity": 1}])
    assert r.status_code == 422


def test_create_order_duplicate_product_422(two_products, make_order):
    r = make_order(items=[{"product_id": 1, "quantity": 1}, {"product_id": 1, "quantity": 2}])
    assert r.status_code == 422


@pytest.mark.parametrize(
    "payload",
    [
        {"customer_name": "An", "items": []},
        {"customer_name": "", "items": [{"product_id": 1, "quantity": 1}]},
        {"items": [{"product_id": 1, "quantity": 1}]},
        {"customer_name": "An", "items": [{"product_id": 1, "quantity": 0}]},
    ],
)
def test_create_order_validation_422(two_products, client, payload):
    assert client.post(ORDERS, json=payload).status_code == 422


def test_create_order_bad_json_400(client):
    r = client.post(ORDERS, data="{ bad", content_type="application/json")
    assert r.status_code == 400


# ─── GET /orders/<id> ───
def test_get_order_and_404(two_products, make_order, client):
    make_order()
    assert client.get(f"{ORDERS}/1").status_code == 200
    r = client.get(f"{ORDERS}/999")
    assert r.status_code == 404
    assert r.get_json()["error"] == "not_found"


# ─── GET /orders: eager loading, kiem tra khong bi N+1 ───
def _selects(statements):
    return [s for s in statements if s.lstrip().upper().startswith("SELECT")]


@pytest.mark.parametrize("n_orders", [2, 10])
def test_list_orders_has_no_n_plus_1(two_products, make_order, client, count_queries, n_orders):
    for i in range(n_orders):
        make_order(
            customer_name=f"KH {i}",
            items=[{"product_id": 1, "quantity": 1}, {"product_id": 2, "quantity": 2}],
        )
    db.session.expire_all()  # xoa cache identity map de dem dung so query that

    with count_queries() as statements:
        r = client.get(ORDERS)

    data = r.get_json()
    assert r.status_code == 200
    assert data["total"] == n_orders
    assert len(data["items"]) == n_orders
    assert all(len(o["items"]) == 2 for o in data["items"])
    assert all(i["product_name"] for o in data["items"] for i in o["items"])

    # orders + count + items (selectinload) + products (selectinload) = 4,
    # KHONG phu thuoc so order. Neu lazy load se la 1 + N + 2N query.
    assert len(_selects(statements)) <= 4


def test_list_orders_pagination(two_products, make_order, client):
    for _ in range(5):
        make_order()
    data = client.get(f"{ORDERS}?page=2&size=2").get_json()
    assert (data["page"], data["size"], data["total"]) == (2, 2, 5)
    assert [o["id"] for o in data["items"]] == [3, 4]
