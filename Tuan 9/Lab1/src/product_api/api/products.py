from flask import Blueprint, jsonify
from sqlalchemy.exc import IntegrityError

from ..errors import Conflict, NotFound, OutOfStock
from ..extensions import db
from ..models import Product
from ..schemas import ProductIn, ProductOut, ProductPatch, ReserveIn
from .utils import int_arg as _int_arg
from .utils import json_body as _json_body

products_bp = Blueprint("products", __name__, url_prefix="/api/v1/products")

MAX_PAGE_SIZE = 100


# ─── helper ───
def _get_active_or_404(product_id):
    """Lay san pham chua bi archived, neu khong co -> 404."""
    p = db.session.get(Product, product_id)
    if p is None or p.archived:
        raise NotFound(f"product {product_id} not found")
    return p


# ─── GET /api/v1/products?page=1&size=20 ───
@products_bp.get("")
def list_products():
    page = max(1, _int_arg("page", 1))
    size = min(MAX_PAGE_SIZE, max(1, _int_arg("size", 20)))

    not_archived = Product.archived.is_(False)
    rows = (
        db.session.execute(
            db.select(Product)
            .where(not_archived)
            .order_by(Product.id)
            .offset((page - 1) * size)
            .limit(size)
        )
        .scalars()
        .all()
    )
    total = db.session.scalar(
        db.select(db.func.count()).select_from(Product).where(not_archived)
    )
    return (
        jsonify(
            {
                "items": ProductOut(many=True).dump(rows),
                "page": page,
                "size": size,
                "total": total,
            }
        ),
        200,
    )


# ─── GET /api/v1/products/<id> ───
@products_bp.get("/<int:id>")
def get_product(id):
    return ProductOut().dump(_get_active_or_404(id)), 200


# ─── POST /api/v1/products ───
@products_bp.post("")
def create_product():
    body = ProductIn().load(_json_body())
    p = Product(**body)
    db.session.add(p)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Conflict("sku already exists", error="sku_conflict")
    return ProductOut().dump(p), 201


# ─── POST /api/v1/products/<id>/reserve ───
@products_bp.post("/<int:id>/reserve")
def reserve_product(id):
    qty = ReserveIn().load(_json_body())["qty"]
    p = _get_active_or_404(id)

    # UPDATE co dieu kien: giam ton kho va khong cho < 0 ngay trong 1 cau lenh
    # (tranh race condition khi 2 request dat truoc cung luc).
    result = db.session.execute(
        db.update(Product)
        .where(Product.id == id, Product.qty_in_stock >= qty)
        .values(qty_in_stock=Product.qty_in_stock - qty)
    )
    if result.rowcount == 0:
        db.session.rollback()
        raise OutOfStock(f"only {p.qty_in_stock} left, requested {qty}")
    db.session.commit()
    db.session.refresh(p)
    return ProductOut().dump(p), 200


# ─── PATCH /api/v1/products/<id> ───
@products_bp.patch("/<int:id>")
def patch_product(id):
    body = ProductPatch().load(_json_body(), partial=True)
    p = _get_active_or_404(id)
    for key, value in body.items():  # chi field co trong body moi doi
        setattr(p, key, value)
    db.session.commit()
    return ProductOut().dump(p), 200


# ─── DELETE /api/v1/products/<id>  (soft delete) ───
@products_bp.delete("/<int:id>")
def delete_product(id):
    p = _get_active_or_404(id)
    p.archived = True
    db.session.commit()
    return "", 204
