from marshmallow import Schema, ValidationError, fields, validate, validates_schema


# ─── output ───
class ProductOut(Schema):
    id = fields.Int()
    sku = fields.Str()
    name = fields.Str()
    description = fields.Str(allow_none=True)
    price_cents = fields.Int()
    qty_in_stock = fields.Int()
    archived = fields.Bool()


# ─── input: tao moi (POST /products) ───
class ProductIn(Schema):
    sku = fields.Str(required=True, validate=validate.Length(min=3, max=32))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(
        load_default=None, allow_none=True, validate=validate.Length(max=2000)
    )
    price_cents = fields.Int(required=True, validate=validate.Range(min=0))
    qty_in_stock = fields.Int(load_default=0, validate=validate.Range(min=0))


# ─── input: cap nhat mot phan (PATCH /products/<id>) ───
class ProductPatch(Schema):
    name = fields.Str(validate=validate.Length(min=1, max=255))
    description = fields.Str(allow_none=True, validate=validate.Length(max=2000))
    price_cents = fields.Int(validate=validate.Range(min=0))
    qty_in_stock = fields.Int(validate=validate.Range(min=0))


# ─── input: dat truoc (POST /products/<id>/reserve) ───
class ReserveIn(Schema):
    qty = fields.Int(required=True, validate=validate.Range(min=1))


# ═══════════════ Order / OrderItem ═══════════════
class OrderItemIn(Schema):
    product_id = fields.Int(required=True, validate=validate.Range(min=1))
    quantity = fields.Int(required=True, validate=validate.Range(min=1))


class OrderIn(Schema):
    customer_name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    items = fields.List(
        fields.Nested(OrderItemIn), required=True, validate=validate.Length(min=1)
    )

    @validates_schema
    def _no_duplicate_products(self, data, **kwargs):
        ids = [i["product_id"] for i in data["items"]]
        if len(ids) != len(set(ids)):
            raise ValidationError("duplicate product_id", "items")


class OrderItemOut(Schema):
    id = fields.Int()
    product_id = fields.Int()
    product_name = fields.Str(attribute="product.name")
    quantity = fields.Int()
    unit_price_cents = fields.Int()


class OrderOut(Schema):
    id = fields.Int()
    customer_name = fields.Str()
    items = fields.Nested(OrderItemOut, many=True)
    total_cents = fields.Int()
    created_at = fields.DateTime()
