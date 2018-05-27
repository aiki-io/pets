from flask import Flask
from flask_bcrypt import Bcrypt
from flask_mongoengine import MongoEngine
from config import BaseConfig

db = MongoEngine()
bcrypt = Bcrypt()


def create_app(config_class=BaseConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    bcrypt.init_app(app)

    from app.main import bp as bp_main
    app.register_blueprint(bp_main)

    from app.api import bp as bp_api
    app.register_blueprint(bp_api, url_prefix='/api')

    return app
