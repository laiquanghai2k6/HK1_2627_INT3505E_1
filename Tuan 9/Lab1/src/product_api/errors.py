"""Exception rieng + global error handler.

Moi loi tra ve JSON co dang: {"error": "<ma_loi>", "detail": ...}
"""
from flask import jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException


class ApiError(Exception):
    status_code = 500
    error = "internal_error"

    def __init__(self, detail="", error=None, status=None):
        super().__init__(detail)
        self.detail = detail
        if error:
            self.error = error
        if status:
            self.status_code = status


class BadRequest(ApiError):
    status_code = 400
    error = "bad_request"


class NotFound(ApiError):
    status_code = 404
    error = "not_found"


class Conflict(ApiError):
    status_code = 409
    error = "conflict"


class OutOfStock(Conflict):
    error = "out_of_stock"


class UnprocessableEntity(ApiError):
    status_code = 422
    error = "validation_error"


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def _on_api_error(err):
        return jsonify({"error": err.error, "detail": err.detail}), err.status_code

    @app.errorhandler(ValidationError)
    def _on_validation_error(err):
        # err.messages: dict {field: [thong bao, ...]}
        return jsonify({"error": "validation_error", "detail": err.messages}), 422

    @app.errorhandler(HTTPException)
    def _on_http_error(err):
        return (
            jsonify(
                {
                    "error": err.name.lower().replace(" ", "_"),
                    "detail": err.description,
                }
            ),
            err.code,
        )

    @app.errorhandler(Exception)
    def _on_unhandled(err):
        app.logger.exception("unhandled exception")
        return jsonify({"error": "internal_error", "detail": "unexpected server error"}), 500
