from flask import Blueprint

from .users_data import get_user

bp = Blueprint("v2", __name__)


@bp.get("/users/<int:uid>")
def read_user(uid):
    user = get_user(uid)
    if user is None:
        return {"error": "nf"}, 404
    return {"id": uid, **user}

