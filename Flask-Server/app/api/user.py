# *-* coding: utf-8 *-*
import os
from datetime import datetime
from flask import request, current_app
from app.models import db, User, Screen, Movie
from flask_restplus import Namespace, Resource
from flask_login import login_user, login_required, current_user
from app.utils import checkPassword, checkMobileAndCode, MD5, time2stamp

api = Namespace('user', description='用户模块')


@api.route('/')
class UsersResource(Resource):
    @api.doc(parser=api.parser().add_argument(
        'id', required=True, help='手机号码', location='form')
        .add_argument(
        'password', required=True, help='密码的md5值', location='form')
        .add_argument(
        'payPassword', required=True, help='支付密码的md5值', location='form')
        .add_argument(
        'smscode', required=True, help='短信验证码', location='form')
    )
    def post(self):
        """用户注册"""
        form = request.form
        mobile = form.get('id', '')
        smscode = form.get('smscode', '')

        # 校验手机和短信验证码
        res = checkMobileAndCode(mobile, smscode)
        if not res[0]:
            return res[1], 233

        if User.query.get(mobile) is not None:
            return {'message': '手机号码已被注册'}, 233

        password = form.get('password', '')
        if not checkPassword(password):
            return {'message': '密码非法'}, 233

        pay_password = form.get('payPassword', '')
        if not checkPassword(pay_password):
            return {'message': '支付密码非法'}, 233

        user = User()
        user.id = mobile
        user.password = MD5(password)
        user.payPassword = MD5(pay_password)
        db.session.add(user)
        db.session.commit()
        login_user(user, True)
        return {'message': '注册成功'}, 200

    @login_required
    def get(self):
        """获取用户信息(需登录)"""
        return current_user.__json__(), 200

    @api.doc(parser=api.parser()
             .add_argument('nickname', help='昵称', location='form')
             .add_argument('description', help='个性签名', location='form')
             .add_argument('avatar', help='头像', location='files'))
    @login_required
    def patch(self):
        """修改用户信息(需登录)"""
        form = request.form
        nickname = form.get('nickname', '').strip()
        description = form.get('description', '').strip()
        avatar = request.files.get('avatar', None)

        if len(nickname):
            current_user.nickname = nickname

        if len(description):
            current_user.description = description

        if avatar is not None and avatar.content_type.startswith('image/'):
            filename = avatar.filename
            filename = "%s_%d%s" % (current_user.id, time2stamp(datetime.now()), filename[filename.rindex('.'):])
            url = current_app.static_folder + '/images/user/%s'
            avatar.save(url % filename)
            old = current_user.avatar
            if old != 'MonkeyEye.jpg':
                os.remove(url % old)
            current_user.avatar = filename

        db.session.commit()
        return {'message': '用户信息修改成功'}, 200


@api.route('/history')
class HistoryResource(Resource):
    res = '{name} {time}放映 {hallNum}号厅{seat}座 订单{id}'
    @login_required
    def get(self):
        """获取观影历史(需登录)"""
        orders = current_user.orders.filter_by(status=1)
        screens = set([Screen.query.get(o.screenId) for o in orders])
        movies = set([Movie.query.get(s.movieId) for s in screens])
        return [{
                    'movieType': m.movieType,
                    'name': m.name,
                    'playingType': m.playingType,
                    'playingTime': time2stamp(m.playingTime),
                    'poster': '/static/images/poster/%s' % m.poster,
                    'id': m.id
                } for m in movies], 200
