# -*- coding: utf-8 -*-
from hashlib import md5
from ..models import db, User
from flask import request
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
        if new_password is None and len(new_password) == 0:
            return {'message': 'Invalid password'}, 400

        if not current_user.isAdmin:
            user = User.query.get(current_user.id)
            user.password = md5(new_password).hexdigest()
            db.session.commit()
            logout_user()

        return {'message': 'Modify successful. Please login again'}, 200