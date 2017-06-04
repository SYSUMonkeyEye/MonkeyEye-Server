# *-* coding: utf-8 *-*
import pickle
from api import api
from redis import Redis
from flask import Flask
from config import config
import flask_login as login
from models import db, User
from functools import wraps
from datetime import timedelta
from instance.config import ADMIN, REDIS
from utils import MD5Twice, isAdmin, UUID
from werkzeug.datastructures import CallbackDict
from flask.sessions import SessionInterface, SessionMixin


class RedisSession(CallbackDict, SessionMixin):
    def __init__(self, initial=None, sid=None, new=False):
        def on_update(self):
            self.modified = True
        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.new = new
        self.modified = False


class RedisSessionInterface(SessionInterface):
    serializer = pickle
    session_class = RedisSession

    def __init__(self, redis=None, prefix='session:'):
        if redis is None:
            self.redis = Redis(host=REDIS[0], password=REDIS[1])
        else:
            self.redis = redis
        self.prefix = prefix

    def generate_sid(self):
        return UUID()

    def get_redis_expiration_time(self, app, session, permanent=False):
        if permanent:
            return timedelta(minutes=10)
        return app.permanent_session_lifetime

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        if not sid:
            return self.session_class(sid=self.generate_sid(), new=True)
        val = self.redis.get(self.prefix + sid)
        if val is not None:
            data = self.serializer.loads(val)
            return self.session_class(data, sid=sid)
        return self.session_class(sid=sid, new=True)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        if not session:
            self.redis.delete(self.prefix + session.sid)
            if session.modified:
                response.delete_cookie(app.session_cookie_name, domain=domain)
            return
        redis_exp = self.get_redis_expiration_time(app, session)
        cookie_exp = self.get_expiration_time(app, session)
        val = self.serializer.dumps(dict(session))
        self.redis.setex(self.prefix + session.sid, val,
                         int(redis_exp.total_seconds()))
        response.set_cookie(app.session_cookie_name, session.sid,
                            expires=cookie_exp, httponly=True, domain=domain)


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

    if User.query.get(ADMIN[0]) is None:
        user = User()
        user.id = ADMIN[0]
        user.password = MD5Twice(ADMIN[1])
        user.isAdmin = True
        user.nickname = '管理员'
        db.session.add(user)
        db.session.commit()

    from admin.admin import admin, init_login

    init_login(app)
    admin.init_app(app)

    api.decorators = [swagger_login]  # swagger页面需要认证
    api.init_app(app)
    app.session_interface = RedisSessionInterface()

    return app
