# *-* coding: utf-8 *-*
from app.utils import *
from app.models import *
from flask_login import login_user
from flask import request, current_app
from flask_restplus import Namespace, Resource

api = Namespace('user', description='用户模块')


@api.route('/')
class UsersResource(Resource):
    @api.doc(parser=api.parser()
             .add_argument('id', required=True, help='手机号码', location='form')
             .add_argument('password', required=True, help='密码的MD5摘要', location='form')
             .add_argument('smscode', required=True, help='短信验证码', location='form'))
    def post(self):
        """用户注册"""
        form = request.form
        mobile = form.get('id', '')
        hash = form.get('password', '')
        smscode = form.get('smscode', '')

        # 校验手机和短信验证码
        res = checkMobileAndCode(mobile, smscode)
        if not res[0]:
            return res[1], 400

        if User.query.get(mobile) is not None:
            return {'message': 'User already exists'}, 400

        user = User()
        user.id = mobile
        user.password = md5(hash).hexdigest()
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return {'message': 'Register successfully'}, 200

    def get(self):
        """获取用户列表"""
        result = [user.__json__() for user in User.query.filter_by(isAdmin=False).all()]
        return result, 200


@api.route('/<id>')
@api.doc(params={'id':'手机号码'})
class UserResource(Resource):
    def get(self, id):
        """获取用户信息"""
        if isValid(id, 11):
            user = User.query.filter_by(id=id).first()
            if user is None:
                return {'message':'User does not exist'}, 400
            return user.__json__(), 200
        return {'message':'Invalid mobile'}, 400

    @api.doc(parser=api.parser().add_argument('avatar', required=True, help='头像', location='files'))
    def put(self, id):
        """修改用户信息"""
        avatar = request.files['avatar']
        if avatar.content_type.startswith('image/'):
            avatar.save('%s/%s' % (current_app.static_folder, avatar.filename))

        return 'modify user %s info' % id, 200
