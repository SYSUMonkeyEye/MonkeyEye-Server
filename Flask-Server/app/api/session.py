# *-* coding: utf-8 *-*
from flask import request
from ..models import User
from ..utils import MD5
from flask_restplus import Namespace, Resource
from flask_login import login_user, logout_user, login_required, current_user

api = Namespace('session', description='会话模块')


@api.route('/')
class Session(Resource):
    @api.doc(parser=api.parser().add_argument(
        'id', type=str, required=True, help='手机号码', location='form')
        .add_argument(
        'password', type=str, required=True, help='密码的md5值', location='form')
    )
    def post(self):
        """用户登入"""
        form = request.form
        mobile = form.get('id', '')

        user = User.query.get(mobile)
        if user is None:
            return {'message': '用户不存在'}, 233

        password = form.get('password', '')
        if user.password != MD5(password):
            return {'message': '密码错误'}, 233

        login_user(user, True)
        return {'message': '登录成功'}, 200

    @login_required
    def delete(self):
        """用户登出(需登录)"""
        if not current_user.isAdmin:
            logout_user()
        return {'message': '退出登录成功'}, 200
