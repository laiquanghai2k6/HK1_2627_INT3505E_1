from flask import Blueprint, jsonify
from sqlalchemy.orm import selectinload

from ..errors import NotFound, UnprocessableEntity
from ..extensions import db
from ..models import Order, OrderItem, Product
from ..schemas import OrderIn, OrderOut
from .utils import int_arg, json_body

orders_bp = Blueprint("orders", __name__, url_prefix="/api/v1/orders")

MAX_PAGE_SIZE = 100


def _with_items():
    """Eager load Order -> items -> product bang selectinload (tranh N+1)."""
    return selectinload(Order.items).selectinload(OrderItem.product)


def _get_order_or_404(order_id):
    order = db.session.execute(
        db.select(Order).options(_with_items()).where(Order.id == order_id)
    ).scalar_one_or_none()
    if order is None:
        raise NotFound(f"order {order_id} not found")
    return order


# ─── POST /api/v1/orders ───
@orders_bp.post("")
def create_order():
    body = OrderIn().load(json_body())
    ids = [i["product_id"] for i in body["items"]]

    # 1 query lay tat ca san pham can dat (chua archived)
    products = {
        p.id: p
        for p in db.session.execute(
            db.select(Product).where(Product.id.in_(ids), Product.archived.is_(False))
        ).scalars()
    }
    missing = [pid for pid in ids if pid not in products]
    if missing:
        raise UnprocessableEntity({"items": [f"product not found: {missing}"]})

    order = Order(
        customer_name=body["customer_name"],
        items=[
            OrderItem(
                product_id=i["product_id"],
                quantity=i["quantity"],
                unit_price_cents=products[i["product_id"]].price_cents,
            )
            for i in body["items"]
        ],
    )
    db.session.add(order)
    db.session.commit()
    return OrderOut().dump(_get_order_or_404(order.id)), 201


# ─── GET /api/v1/orders?page=1&size=20 ───
@orders_bp.get("")
def list_orders():
    page = max(1, int_arg("page", 1))
    size = min(MAX_PAGE_SIZE, max(1, int_arg("size", 20)))

    rows = (
        db.session.execute(
            db.select(Order)
            .options(_with_items())
            .order_by(Order.id)
            .offset((page - 1) * size)
            .limit(size)
        )
        .scalars()
        .all()
    )
    total = db.session.scalar(db.select(db.func.count()).select_from(Order))
    return (
        jsonify(
            {
                "items": OrderOut(many=True).dump(rows),
                "page": page,
                "size": size,
                "total": total,
            }
        ),
        200,
    )


# ─── GET /api/v1/orders/<id> ───
@orders_bp.get("/<int:id>")
def get_order(id):
    return OrderOut().dump(_get_order_or_404(id)), 200
