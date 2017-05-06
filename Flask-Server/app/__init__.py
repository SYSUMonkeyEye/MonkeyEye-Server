# *-* coding: utf-8 *-*
from api import api
from flask import Flask
from config import config
from models import db, User
from functools import wraps
from utils import MD5Twice, isAdmin
from admin.admin import admin, init_login, login

def swagger_login(func):
    @wraps(func)
    def login_pass(*args, **kwargs):
        return func(*args, **kwargs)

    if isAdmin() or func.func_name != 'specs':
        return login_pass
    return login.login_required(func)


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])  # 加载普通配置
    app.config.from_pyfile('config.py')  # 加载私密配置 instance/config.py
    config[config_name].init_app(app)

    # 创建数据表
    db.app = app
    db.init_app(app)
    db.create_all()

    if User.query.get(app.config['ADMIN'][0]) is None:
        user = User()
        user.id = app.config['ADMIN'][0]
        user.password = MD5Twice(app.config['ADMIN'][1])
        user.isAdmin = True
        user.nickname = '管理员'
        db.session.add(user)
        db.session.commit()

    init_login(app)
    admin.init_app(app)

    api.decorators = [swagger_login]  # swagger页面需要认证
    api.init_app(app)

    return app
