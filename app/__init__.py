from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config
from flask_restful import Api
from elasticsearch import Elasticsearch
from flasgger import Swagger
from flask_mail import Mail

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()

SWAGGER_TEMPLATE = {"securityDefinitions": {"APIKeyHeader": {"type": "apiKey", "name": "x-access-tokens", "in": "header"}}}
swagger = Swagger(template=SWAGGER_TEMPLATE)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.elasticsearch = Elasticsearch(app.config['ELASTICSEARCH_URL']) \
        if app.config['ELASTICSEARCH_URL'] else None

    db.init_app(app)
    migrate.init_app(app, db)
    swagger.init_app(app)
    mail.init_app(app)

    with app.app_context():
        db.create_all()
    
    from app.main import bp as main_bp
    from app.auth import bp as auth_bp
    from app.errors import bp as errors_bp
    from app.admin import bp as admin_bp
    from app.aws import bp as aws_bp
    from app.dummy import bp as dummy_bp

    app.register_blueprint(errors_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(aws_bp)
    app.register_blueprint(dummy_bp)

    return app