# *-* coding: utf-8 *-*
from flask import request, current_app
from flask_restplus import Namespace, Resource

api = Namespace('user', description='用户模块')


@api.route('/')
class Users(Resource):
    @api.doc(parser=api.parser()
             .add_argument('mobile', required=True, help='手机号码', location='form')
             .add_argument('password', required=True, help='密码的MD5摘要', location='form')
             .add_argument('smscode', required=True, help='短信验证码', location='form'))
    def post(self):
        """用户注册"""
        print request.form
        return 'register', 200

    def get(self):
        """获取用户列表"""
        return ['user1', 'user2'], 200

@api.route('/<user_id>')
@api.doc(params={'user_id':'手机号码'})
class User(Resource):
    def get(self, user_id):
        """获取用户信息"""
        return 'get user %s info' % user_id, 200

    @api.doc(parser=api.parser().add_argument('avatar', required=True, help='头像', location='files'))
    def put(self, user_id):
        """修改用户信息"""
        avatar = request.files['avatar']
        if avatar.content_type.startswith('image/'):
            avatar.save('%s/%s' % (current_app.static_folder, avatar.filename))

        return 'modify user %s info' % user_id, 200
