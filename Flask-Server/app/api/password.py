# -*- coding: utf-8 -*-
from flask import request
from ..models import db, User
from ..utils import checkPassword, MD5
from flask_restplus import Resource, Namespace
from flask_login import login_required, current_user, logout_user

api = Namespace('password', description='密码模块')


@api.route('/loginPassword')
class Password(Resource):
    @api.doc(parser=api.parser()
             .add_argument('password', type=str, required=True, help='原密码md5值', location='form')
             .add_argument('new_password', type=str, required=True, help='新密码md5值', location='form'))
    @login_required
    def patch(self):
        """修改密码(需登录)"""
        form = request.form
        password = form.get('password', '')
        new_password = form.get('new_password', '')

        if MD5(password) != current_user.password:
            return {'message': '密码错误'}, 233

        if not checkPassword(new_password):
            return {'message': '新的密码非法'}, 233

        if not current_user.isAdmin:
            current_user.password = MD5(new_password)
            db.session.commit()
            logout_user()

        return {'message': '密码修改成功，请重新登录'}, 200


@api.route('/payPassword')
class PayPassword(Resource):
    @api.doc(parser=api.parser()
                    .add_argument('payPassword', type=str, required=True, help='新支付密码md5值', location='form')
                    .add_argument('new_payPassword', type=str, required=True, help='新支付密码md5值', location='form'))
    @login_required
    def patch(self):
        """修改支付密码(需登录)"""
        form = request.form
        payPassword = form.get('payPassword', '')
        new_payPassword = form.get('new_payPassword', '')

        if MD5(payPassword) != current_user.payPassword:
            return {'message': '支付密码错误'}, 233

        if not checkPassword(new_payPassword):
            return {'message': '新的支付密码非法'}, 233

        current_user.payPassword = MD5(new_payPassword)
        db.session.commit()

        return {'message': '支付密码修改成功'}, 200