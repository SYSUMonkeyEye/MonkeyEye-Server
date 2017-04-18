# *-* coding: utf-8 *-*
from flask import Flask
from database import db
from database import models
from api.user import user
from api.smscode import smscode
from config import config


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])  # 加载普通配置
    app.config.from_pyfile('config.py')  # 加载私密配置 instance/config.py
    config[config_name].init_app(app)

    app.register_blueprint(user)
    app.register_blueprint(smscode)

    # 创建数据表
    db.app = app
    db.init_app(app)
    db.create_all()

    return app
