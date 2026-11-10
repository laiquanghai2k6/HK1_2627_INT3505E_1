import logging
import os

import click
from flask import Flask

from .api.health import health_bp
from .api.orders import orders_bp
from .api.products import products_bp
from .config import DefaultConfig
from .errors import register_error_handlers
from .extensions import db, migrate


def create_app(config=None):
    app = Flask(__name__)
    # config: class/object, hoac chuoi "module.Class", hoac lay tu APP_CONFIG
    app.config.from_object(config or os.environ.get("APP_CONFIG") or DefaultConfig)

    logging.basicConfig(level=app.config.get("LOG_LEVEL", "INFO"))

    db.init_app(app)
    migrate.init_app(app, db)

    # import de Alembic / create_all nhin thay model
    from . import models  # noqa: F401

    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(health_bp)
    register_error_handlers(app)

    @app.cli.command("init-db")
    def init_db():
        """Tao cac bang con thieu (idempotent). Dung cho Docker lan chay dau."""
        db.create_all()
        click.echo("database ready")

    return app
