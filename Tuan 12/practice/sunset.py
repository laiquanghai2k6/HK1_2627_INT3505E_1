import logging
from datetime import datetime, timezone
from email.utils import format_datetime
from functools import wraps

from flask import make_response, request

log = logging.getLogger("sunset")


def deprecate_at(sunset_date, replacement=None):
    sunset_header = format_datetime(sunset_date.astimezone(timezone.utc), usegmt=True)

    def decorate(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            successor = replacement.format(**kwargs) if replacement else None
            log.warning("deprecated_call %s %s", request.path, request.remote_addr)
            if datetime.now(timezone.utc) >= sunset_date:
                return {"error": "gone", "sunset": sunset_header, "use_instead": successor}, 410

            response = make_response(view(*args, **kwargs))
            response.headers["Sunset"] = sunset_header
            response.headers["Deprecation"] = "true"
            if successor:
                response.headers["Link"] = f'<{successor}>; rel="successor-version"'
            return response

        return wrapper

    return decorate

