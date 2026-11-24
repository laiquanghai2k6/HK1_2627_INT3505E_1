import os
from datetime import datetime, timezone

from flask import Flask, make_response, request

from blueprints.v1 import create_v1_blueprint
from blueprints.v2 import bp as v2_bp
from blueprints.users_data import get_user
from gateway import dispatch
from versioning import api_version

DEFAULT_SUNSET = "2026-12-31T23:59:59+00:00"


def create_app():
    app = Flask(__name__)
    app.json.ensure_ascii = False

    sunset = datetime.fromisoformat(os.getenv("V1_SUNSET", DEFAULT_SUNSET))
    if sunset.utcoffset() is None:
        raise ValueError("V1_SUNSET must include a UTC offset")
    app.config["V2_PERCENT"] = int(os.getenv("V2_PERCENT", "5"))
    if not 0 <= app.config["V2_PERCENT"] <= 100:
        raise ValueError("V2_PERCENT must be between 0 and 100")

    app.register_blueprint(
        create_v1_blueprint(sunset.astimezone(timezone.utc)), url_prefix="/api/v1"
    )
    app.register_blueprint(v2_bp, url_prefix="/api/v2")

    @app.get("/users/<int:uid>")
    @api_version()
    def get_user_by_header(version, uid):
        user = get_user(uid)
        if user is None:
            return {"error": "not found"}, 404
        if version == "1":
            return {"id": uid, "full_name": f"{user['first_name']} {user['last_name']}"}
        return {"id": uid, **user}

    @app.post("/orders")
    def create_order():
        body = request.get_json(silent=True)
        account = body.get("account_id") if isinstance(body, dict) else None
        if not isinstance(account, str) or not account.strip():
            return {"error": "account_id must be a non-empty string"}, 400

        cohort = request.headers.get("X-Cohort", "")
        version, result = dispatch(body, cohort, app.config["V2_PERCENT"])
        response = make_response(result, 201 if version == "v2" else 200)
        response.headers["X-Order-Handler"] = version
        return response

    return app


app = create_app()

