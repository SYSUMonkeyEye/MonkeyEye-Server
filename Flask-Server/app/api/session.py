# *-* coding: utf-8 *-*
from flask_restplus import Namespace, Resource

api = Namespace('session', description='会话模块')


@api.route('/')
class Session(Resource):
    @api.doc(parser=api.parser()
            .add_argument('mobile', type=str, required=True, help='手机号码', location='form')
            .add_argument('password', type=str, required=True, help='密码的MD5摘要', location='form'))
    def post(self):
        """用户登入"""
        return 'login', 200

    @api.doc(parser=api.parser().add_argument('mobile', type=str, required=True, help='手机号码',location='form'))
    def delete(self):
        """用户登出"""
        return 'logout', 200
