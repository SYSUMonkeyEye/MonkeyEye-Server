# -*- coding: utf-8 -*-
from flask import request
from ..models import db, User
from ..utils import checkPassword, MD5
from flask_restplus import Resource, Namespace
from flask_login import login_required, current_user, logout_user

api = Namespace('password', description='密码模块')


@api.route('/')
class Password(Resource):
    @api.doc(parser=api.parser().add_argument('new_password', type=str, required=True, help='新密码md5值', location='form'))
    @login_required
    def patch(self):
        """修改密码"""
        form = request.form
        new_password = form.get('new_password', None)
        if not checkPassword(new_password):
            return {'message': 'Invalid password'}, 400

        if not current_user.isAdmin:
            user = User.query.get(current_user.id)
            user.password = MD5(new_password)
            db.session.commit()
            logout_user()

        return {'message': 'Modify password successful. Please login again'}, 200


@api.route('/payPassword')
class PayPassword(Resource):
    @api.doc(parser=api.parser().add_argument('new_payPassword', type=str, required=True, help='新支付密码密码md5值', location='form'))
    @login_required
    def patch(self):
        """修改密码"""
        form = request.form
        new_payPassword = form.get('new_payPassword', None)
        if not checkPassword(new_payPassword):
            return {'message': 'Invalid payPassword'}, 400

        user = User.query.get(current_user.id)
        user.payPassword = MD5(new_payPassword)
        db.session.commit()

        return {'message': 'Modify payPassword successful.'}, 200