# *-* coding: utf-8 *-*
import models
from api import api
from admin import admin
from flask import Flask
from config import config
from functools import wraps
from flask_httpauth import HTTPBasicAuth


def __swagger_auth(app):
    """返回一个装饰器, swagger页面需要认证, 其他页面不做处理"""
    __auth = HTTPBasicAuth()

    # 身份验证
    @__auth.verify_password
    def verify_password(username, password):
        return (username, password) == app.config['ADMIN_CREDENTIALS']

    def swagger_login(func):
        @wraps(func)
        def login_pass(*args, **kwargs):
            return func(*args, **kwargs)

        @wraps(func)
        @__auth.login_required
        def login_required(*args, **kwargs):
            return func(*args, **kwargs)

        return login_required if func.func_name == 'specs' else login_pass

    return swagger_login


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])  # 加载普通配置
    app.config.from_pyfile('config.py')  # 加载私密配置 instance/config.py
    config[config_name].init_app(app)

    # 创建数据表
    models.db.app = app
    models.db.init_app(app)
    models.db.create_all()



    admin.init_app(app)

    api.decorators = [__swagger_auth(app)]  # swagger页面需要认证
    api.init_app(app)

    return app
