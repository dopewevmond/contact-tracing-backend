from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config
from flask_restful import Api

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.main import bp as main_bp
    from app.auth import bp as auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    return app