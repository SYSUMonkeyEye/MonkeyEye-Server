# *-* coding: utf-8 *-*
from flask import request
from app.models import User
from app.utils import isValid, md5
from flask_restplus import Namespace, Resource
from flask_login import login_user, logout_user, login_required, current_user

api = Namespace('session', description='会话模块')


@api.route('/')
class Session(Resource):
    @api.doc(parser=api.parser()
            .add_argument('id', type=str, required=True, help='手机号码', location='form')
            .add_argument('password', type=str, required=True, help='密码的MD5摘要', location='form'))
    def post(self):
        """用户登入"""
        form = request.form
        mobile = form.get('id', '')
        hash = form.get('password', '')

        if not isValid(mobile, 11):
            return {'message':'Invalid user name'}, 400

        user = User.query.get(mobile)
        if user is None:
            return {'message':'User does not exist'}, 400

        if user.password != md5(hash).hexdigest():
            return {'message':'Wrong password'}, 400

        login_user(user)
        return {'message': 'Login successfully'}, 200


    @login_required
    def delete(self):
        """用户登出"""
        if not current_user.isAdmin:
            logout_user()
        return {'message': 'Logout successfully'}, 200
