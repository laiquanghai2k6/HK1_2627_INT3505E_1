URL = "/api/v1/products"


# ─── POST ───
def test_create_ok(make_product):
    r = make_product()
    assert r.status_code == 201
    data = r.get_json()
    assert data["id"] == 1 and data["sku"] == "SKU-001"
    assert data["qty_in_stock"] == 5 and data["archived"] is False


def test_create_default_qty_is_zero(client):
    r = client.post(URL, json={"sku": "ABC", "name": "x", "price_cents": 0})
    assert r.status_code == 201
    assert r.get_json()["qty_in_stock"] == 0


def test_create_duplicate_sku_409(make_product):
    make_product()
    r = make_product()
    assert r.status_code == 409
    assert r.get_json()["error"] == "sku_conflict"


def test_create_validation_422(client):
    r = client.post(URL, json={"sku": "ab", "name": "", "price_cents": -1})
    assert r.status_code == 422
    body = r.get_json()
    assert body["error"] == "validation_error"
    assert set(body["detail"]) == {"sku", "name", "price_cents"}


def test_create_missing_fields_422(client):
    assert client.post(URL, json={}).status_code == 422


def test_create_bad_json_400(client):
    r = client.post(URL, data="{ bad json", content_type="application/json")
    assert r.status_code == 400
    assert r.get_json()["error"] == "bad_request"


# ─── GET list / one ───
def test_list_pagination(make_product, client):
    for i in range(5):
        make_product(sku=f"SKU-{i:03d}")
    r = client.get(f"{URL}?page=2&size=2")
    data = r.get_json()
    assert r.status_code == 200
    assert (data["page"], data["size"], data["total"]) == (2, 2, 5)
    assert [p["id"] for p in data["items"]] == [3, 4]


def test_list_defaults(client):
    data = client.get(URL).get_json()
    assert data == {"items": [], "page": 1, "size": 20, "total": 0}


def test_list_invalid_page_422(client):
    assert client.get(f"{URL}?page=abc").status_code == 422


def test_get_one_and_404(make_product, client):
    make_product()
    assert client.get(f"{URL}/1").status_code == 200
    r = client.get(f"{URL}/9999")
    assert r.status_code == 404
    assert r.get_json()["error"] == "not_found"


# ─── PATCH ───
def test_patch_only_changes_given_fields(make_product, client):
    make_product()
    r = client.patch(f"{URL}/1", json={"price_cents": 777})
    data = r.get_json()
    assert r.status_code == 200
    assert data["price_cents"] == 777
    assert data["name"] == "Laptop" and data["qty_in_stock"] == 5


def test_patch_unknown_field_422(make_product, client):
    make_product()
    assert client.patch(f"{URL}/1", json={"sku": "NEW"}).status_code == 422


def test_patch_404(client):
    assert client.patch(f"{URL}/1", json={"name": "x"}).status_code == 404


# ─── DELETE (soft) ───
def test_soft_delete_hides_product(make_product, client):
    make_product()
    assert client.delete(f"{URL}/1").status_code == 204
    assert client.get(f"{URL}/1").status_code == 404
    assert client.get(URL).get_json()["total"] == 0
    # van ton tai trong DB, chi bi danh dau archived
    from product_api.extensions import db
    from product_api.models import Product

    assert db.session.get(Product, 1).archived is True


def test_delete_404(client):
    assert client.delete(f"{URL}/42").status_code == 404


# ─── reserve ───
def test_reserve_decreases_stock(make_product, client):
    make_product(qty_in_stock=5)
    r = client.post(f"{URL}/1/reserve", json={"qty": 2})
    assert r.status_code == 200
    assert r.get_json()["qty_in_stock"] == 3


def test_reserve_exact_stock_to_zero(make_product, client):
    make_product(qty_in_stock=2)
    r = client.post(f"{URL}/1/reserve", json={"qty": 2})
    assert r.get_json()["qty_in_stock"] == 0


def test_reserve_out_of_stock_409_and_unchanged(make_product, client):
    make_product(qty_in_stock=1)
    r = client.post(f"{URL}/1/reserve", json={"qty": 2})
    assert r.status_code == 409
    assert r.get_json()["error"] == "out_of_stock"
    assert client.get(f"{URL}/1").get_json()["qty_in_stock"] == 1


def test_reserve_invalid_qty_422(make_product, client):
    make_product()
    assert client.post(f"{URL}/1/reserve", json={"qty": 0}).status_code == 422
    assert client.post(f"{URL}/1/reserve", json={}).status_code == 422


def test_reserve_404(client):
    assert client.post(f"{URL}/1/reserve", json={"qty": 1}).status_code == 404
