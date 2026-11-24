from flask import Blueprint

from sunset import deprecate_at
from .users_data import get_user


def create_v1_blueprint(sunset_date):
    bp = Blueprint("v1", __name__)

    @bp.get("/users/<int:uid>")
    @deprecate_at(sunset_date, replacement="/api/v2/users/{uid}")
    def read_user(uid):
        user = get_user(uid)
        if user is None:
            return {"error": "nf"}, 404
        return {
            "id": uid,
            "full_name": f"{user['first_name']} {user['last_name']}",
            "email": user["email"],
        }

    return bp

