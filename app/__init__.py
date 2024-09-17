from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from celery import Celery
from config import Config

db = SQLAlchemy()
api = Api()
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    api.init_app(app)
    celery.conf.update(app.config)

    with app.app_context():
        from app import routes, models
        db.create_all()

    app.register_blueprint(routes.bp)

    return app
