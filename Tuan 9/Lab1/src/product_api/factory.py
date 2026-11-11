import logging
import os

import click
from flask import Flask

from .api.health import health_bp
from .api.orders import orders_bp
from .api.products import products_bp
from .config import DefaultConfig
from .errors import register_error_handlers
from .extensions import db, migrate


def create_app(config=None):
    app = Flask(__name__)
    # config: class/object, hoac chuoi "module.Class", hoac lay tu APP_CONFIG
    app.config.from_object(config or os.environ.get("APP_CONFIG") or DefaultConfig)

    logging.basicConfig(level=app.config.get("LOG_LEVEL", "INFO"))

    db.init_app(app)
    migrate.init_app(app, db)

    # import de Alembic / create_all nhin thay model
    from . import models  # noqa: F401

    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(health_bp)
    register_error_handlers(app)

    @app.cli.command("init-db")
    def init_db():
        """Tao cac bang con thieu (idempotent). Dung cho Docker lan chay dau."""
        db.create_all()
        click.echo("database ready")

    return app
# flask --app wsgi init-db          # tạo bảng products, orders, order_items
# pytest -v  
# flask --app wsgi run
# $base = "http://127.0.0.1:5000/api/v1"
# $host_url = "http://127.0.0.1:5000"
# Tạo (201)
# '{"sku":"IP15","name":"iPhone 15","price_cents":2000000,"qty_in_stock":5}' | curl.exe -i -X POST "$base/products" -H "Content-Type: application/json" -d '@-'

# Trùng sku (409)
# '{"sku":"IP15","name":"Trung","price_cents":1}' | curl.exe -i -X POST "$base/products" -H "Content-Type: application/json" -d '@-'

# # Dữ liệu sai (422)
# '{"sku":"ab","name":"","price_cents":-1}' | curl.exe -i -X POST "$base/products" -H "Content-Type: application/json" -d '@-'

# # Danh sách phân trang (200)
# curl.exe -i "$base/products`?page=1&size=20"

# # Lấy một sản phẩm (200) và không tồn tại (404)
# curl.exe -i "$base/products/1"
# curl.exe -i "$base/products/9999"

# # Reserve: đủ hàng (200), vượt tồn kho (409)
# '{"qty":2}' | curl.exe -i -X POST "$base/products/1/reserve" -H "Content-Type: application/json" -d '@-'
# '{"qty":999}' | curl.exe -i -X POST "$base/products/1/reserve" -H "Content-Type: application/json" -d '@-'

# # Cập nhật một phần (200)
# '{"price_cents":1900000}' | curl.exe -i -X PATCH "$base/products/1" -H "Content-Type: application/json" -d '@-'
#soft delete
# '{"sku":"TMP1","name":"Tam","price_cents":100}' | curl.exe -i -X POST "$base/products" -H "Content-Type: application/json" -d '@-'
# curl.exe -i -X DELETE "$base/products/3"      # 204 (đổi 3 thành id vừa tạo)
# curl.exe -i "$base/products/3"                # 404 (đã archived)
# curl.exe -i "$base/products"                  # không còn hiện sản phẩm đã xóa
#demo order
# '{"sku":"MOUSE1","name":"Mouse","price_cents":250,"qty_in_stock":10}' | curl.exe -i -X POST "$base/products" -H "Content-Type: application/json" -d '@-'

# # Tạo đơn nhiều sản phẩm (201)
# '{"customer_name":"An","items":[{"product_id":1,"quantity":2},{"product_id":2,"quantity":1}]}' | curl.exe -i -X POST "$base/orders" -H "Content-Type: application/json" -d '@-'

# Xem đơn / danh sách đơn
# curl.exe -i "$base/orders/1"
# curl.exe -i "$base/orders`?page=1&size=20"

# # Lỗi: product không tồn tại (422), trùng product (422), đơn không có (404)
# '{"customer_name":"An","items":[{"product_id":9999,"quantity":1}]}' | curl.exe -i -X POST "$base/orders" -H "Content-Type: application/json" -d '@-'
# '{"customer_name":"An","items":[{"product_id":1,"quantity":1},{"product_id":1,"quantity":2}]}' | curl.exe -i -X POST "$base/orders" -H "Content-Type: application/json" -d '@-'
# curl.exe -i "$base/orders/9999"
#health check
# curl.exe -i "$host_url/healthz"     # 200, không dùng DB
# curl.exe -i "$host_url/ready"       # 200, kiểm tra DB
#docker compose up --build            # build và chạy API + Postgres