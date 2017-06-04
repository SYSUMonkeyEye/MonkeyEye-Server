# -*- coding: utf-8 -*-
import smtplib
from flask import request
from ..models import db, User
from email.mime.text import MIMEText
from flask_restplus import Resource, Namespace
from instance.config import MAILKEY, MAILSERVER
from ..utils import checkPassword, MD5, isValid
from flask_login import login_required, current_user, logout_user

api = Namespace('password', description='密码模块')


@api.route('/loginPassword')
class Password(Resource):
    @api.doc(parser=api.parser().add_argument(
      'password', type=str, required=True, help='原密码md5值', location='form')
      .add_argument(
      'new_password', type=str, required=True, help='新密码md5值', location='form')
    )
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
    @api.doc(parser=api.parser().add_argument(
        'payPassword', type=str, required=True, help='原支付密码md5值', location='form')
        .add_argument(
        'new_payPassword', type=str, required=True, help='新支付密码md5值', location='form')
    )
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


@api.hide
@api.route('/reset')
class ResetResource(Resource):
    def sendEmail(self, key, From, To, type):
        try:
            s = '支付' if type == 'pay' else ''
            msg = MIMEText('请访问以下连接重置%s密码，链接有效期30分钟。如非本人操作，请忽略此邮件。\n' % s,
                           'plain', 'utf-8')
            msg["Subject"] = '【MonkeyEye】 %s密码重置' % s
            msg["From"] = From
            msg["To"] = To

            s = smtplib.SMTP_SSL("smtp.qq.com", 465)
            s.login(From, key)

            s.sendmail(From, To, msg.as_string())
            s.close()
            return True
        except Exception:
            return False

    @api.doc(parser=api.parser().add_argument(
        'id', type=str, required=True, help='手机号码', location='form')
        .add_argument(
        'type', type=str, required=True, help='密码类型(login/pay)', location='form')
    )
    def post(self):
        """重置密码"""
        form = request.form
        id = form.get('id', '')
        type = form.get('type', '')
        if not isValid(id, 11):
            return {'message': '手机号码非法'}, 233

        if type not in ['login', 'pay']:
            return {'message': '密码类型非法'}, 233

        u = User.query.get(id)
        if u is None:
            return {'message': '用户不存在'}, 233

        if self.sendEmail(MAILKEY, MAILSERVER, u.email, type):
            return {'message': '重置邮件已发送'}, 200
        return {'message': '邮件发送失败，请稍后再试'}, 233
