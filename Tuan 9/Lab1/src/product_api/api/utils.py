from flask import request

from ..errors import BadRequest, UnprocessableEntity


def json_body():
    body = request.get_json(silent=True)
    if body is None:
        raise BadRequest("body must be valid JSON with Content-Type: application/json")
    return body


def int_arg(name, default):
    raw = request.args.get(name, default)
    try:
        return int(raw)
    except (TypeError, ValueError):
        raise UnprocessableEntity({name: ["must be an integer"]})
