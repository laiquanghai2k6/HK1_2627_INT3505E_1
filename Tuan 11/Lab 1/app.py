from flask import Flask

from blueprints.v1 import bp as v1_bp
from blueprints.v2 import bp as v2_bp


app = Flask(__name__)
app.json.ensure_ascii = False

app.register_blueprint(v1_bp, url_prefix="/api/v1")
app.register_blueprint(v2_bp, url_prefix="/api/v2")


@app.get("/")
def index():
    return {
        "versions": ["/api/v1", "/api/v2"],
        "example": "/api/v1/users/42",
    }


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
