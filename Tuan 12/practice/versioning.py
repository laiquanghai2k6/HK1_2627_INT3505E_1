from functools import wraps

from flask import make_response, request

LATEST = "2"
SUPPORTED = frozenset({"1", "2", "2024-06-20"})


def api_version(supported=SUPPORTED, default=LATEST):
    def decorate(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            version = request.headers.get("X-API-Version", default)
            if version not in supported:
                response = make_response({"error": "unsupported version"}, 400)
            else:
                response = make_response(view(version, *args, **kwargs))
                response.headers["X-API-Version-Served"] = version
            response.vary.add("X-API-Version")
            return response

        return wrapper

    return decorate

