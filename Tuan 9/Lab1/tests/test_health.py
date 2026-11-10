from product_api.extensions import db


def test_liveness_ok(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.get_json() == {"status": "ok"}


def test_liveness_does_not_touch_db(client, count_queries):
    with count_queries() as statements:
        client.get("/healthz")
    assert statements == []


def test_readiness_ok(client):
    r = client.get("/ready")
    assert r.status_code == 200
    assert r.get_json() == {"status": "ok", "checks": {"db": "ok"}}


def test_readiness_503_when_db_down(client, monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("db down")

    monkeypatch.setattr(db.session, "execute", boom)
    r = client.get("/ready")
    assert r.status_code == 503
    assert r.get_json()["checks"]["db"] == "err"
    # liveness van song du DB chet -> 2 probe tach rieng
    assert client.get("/healthz").status_code == 200
