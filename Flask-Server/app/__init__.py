from flask import Flask
from config import config
from api.user import user
from api.smsnum import smsnum
from flask_sqlalchemy import SQLAlchemy


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])
    app.config.from_pyfile("config.py")
    config[config_name].init_app(app)
    db = SQLAlchemy()
    db.init_app(app)
    app.register_blueprint(user)
    app.register_blueprint(smsnum)
    return app
