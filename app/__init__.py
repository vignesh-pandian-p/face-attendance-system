from flask import Flask
from config import Config
from .extensions import db
from flask_migrate import Migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)

    # Register blueprints
    from .routes.main import main_bp
    app.register_blueprint(main_bp)

    # Import models
    from . import models

    from .utils import format_datetime
    app.jinja_env.filters['datetime'] = format_datetime

    return app
