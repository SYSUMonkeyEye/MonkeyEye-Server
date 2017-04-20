# *-* coding: utf-8 *-*
from api import api
from flask import Flask
from database import db
from config import config
from database import models


def __swagger_auth(app):
    """返回一个装饰器, swagger页面需要认证, 其他页面不做处理"""
    from functools import wraps
    from flask_httpauth import HTTPBasicAuth
    auth = HTTPBasicAuth()

    # 身份验证
    @auth.verify_password
    def verify_password(username, password):
        return username == app.config['ADMIN_USERNAME'] and \
               password == app.config['ADMIN_PASSWORD']

    def swagger_login(func):
        @wraps(func)
        def login_pass(*args, **kwargs):
            return func(*args, **kwargs)

        @wraps(func)
        @auth.login_required
        def login_required(*args, **kwargs):
            return func(*args, **kwargs)

        return login_required if func.func_name == 'specs' else login_pass

    return swagger_login


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])  # 加载普通配置
    app.config.from_pyfile('config.py')  # 加载私密配置 instance/config.py
    config[config_name].init_app(app)

    api.decorators = [__swagger_auth(app)]  # swagger页面需要认证
    api.init_app(app)

    # 创建数据表
    db.app = app
    db.init_app(app)
    db.create_all()

    return app
