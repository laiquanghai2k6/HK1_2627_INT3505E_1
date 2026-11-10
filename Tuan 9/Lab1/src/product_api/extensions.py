from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Khoi tao o module-level, gan vao app bang init_app() trong factory
db = SQLAlchemy()
migrate = Migrate()
