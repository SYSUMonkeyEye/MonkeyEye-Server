# *-* coding: utf-8 *-*
from flask_restplus import Namespace, Resource

api = Namespace('session', description='会话模块')


@api.route('/<user_id>')
@api.doc(params={'user_id': '用户id(手机号码)'})
class Session(Resource):
    def post(self, user_id):
        """用户登录"""

        return '%s login' % user_id, 200

    def delete(self, user_id):
        """退出登录"""

        return 'logout', 200
