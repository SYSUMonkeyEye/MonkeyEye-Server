# *-* coding: utf-8 *-*
from api import api
from models import *
from flask import Flask
from config import config
from utils import MD5Twice
from functools import wraps
from admin import admin, init_login, login


def __swagger_auth(app):
    def swagger_login(func):
        @wraps(func)
        def login_pass(*args, **kwargs):
            return func(*args, **kwargs)

        @wraps(func)
        @login.login_required
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
    db.app = app
    db.init_app(app)
    db.create_all()

    if User.query.filter_by(id=app.config['ADMIN_CREDENTIALS'][0]).first() is None:
        user = User()
        user.id = app.config['ADMIN_CREDENTIALS'][0]
        user.password = MD5Twice(app.config['ADMIN_CREDENTIALS'][1])
        user.isAdmin = 1
        user.nickname = '管理员'
        db.session.add(user)
        db.session.commit()

    init_login(app)
    admin.init_app(app)

    api.decorators = [__swagger_auth(app)]  # swagger页面需要认证
    api.init_app(app)

    return app
