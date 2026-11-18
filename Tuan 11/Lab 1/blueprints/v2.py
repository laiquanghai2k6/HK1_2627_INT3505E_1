from flask import Blueprint, jsonify

from users_data import get_user


bp = Blueprint("v2", __name__)


@bp.route("/users/<int:uid>")
def get_user_v2(uid):
    user = get_user(uid)
    if user is None:
        return jsonify(error="nf", code=404), 404
    return {
        "id": uid,
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "email": user["email"],
    }
