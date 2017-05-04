# *-* coding: utf-8 *-*
from models import *
from hashlib import md5
import flask_login as login
from flask import current_app
from utils import MD5Twice, isAdmin, isValid
from flask import request, redirect, url_for
from flask_admin.contrib.sqla import ModelView
from flask_admin import expose, AdminIndexView, helpers
from wtforms import form, fields, validators, ValidationError


class LoginForm(form.Form):
    """登录表单"""
    username = fields.StringField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_username(self, field):
        """登录校验"""
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')
        if md5(self.password.data).hexdigest() != user.password:
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        return db.session.query(User).filter_by(id=self.username.data, isAdmin=1).first()

class MyModelView(ModelView):
    column_display_pk = True  # 显示主键

    def is_accessible(self):
        return isAdmin()


class UserModelView(MyModelView):
    column_exclude_list = ('password', 'isAdmin')  # 不显示密码
    form_edit_rules = ('nickname', 'avatar', 'description')  # 可编辑的字段
    form_columns = ('id', 'password', 'nickname', 'avatar', 'description')  # 可插入的字段
    form_overrides = {'avatar': fields.FileField}
    form_args = {'id': dict(validators=[validators.Regexp('\d{11}', message='Invalid mobile')])}

    def on_model_change(self, form, user, is_created=False):
        avatar = form.avatar.data
        if avatar.content_type.startswith('image/'):
            filename = avatar.filename
            filename = "%s%s" % (user.id, filename[filename.rindex('.'):])
            avatar.save('%s/images/user/%s' % (current_app.static_folder, filename))
            user.avatar = filename
        elif is_created:
            user.avatar = 'MonkeyEye.jpg'
        else:
            user.avatar = form.avatar.object_data

        if is_created:  # 新建用户时密码进行两次md5
            user.password = MD5Twice(form.password.data)


class MovieModelView(MyModelView):
    # 可插入和编辑字段
    form_columns = ('name', 'poster', 'description', 'playingTime', 'duration', 'movieType', 'playingType')
    form_overrides = dict(poster=fields.FileField)

    def on_model_change(self, form, movie, is_created=False):
        poster = form.poster.data
        movie.id = uuid4().hex if is_created else movie.id
        if poster.content_type.startswith('image/'):
            filename = poster.filename
            filename = "%s%s" % (movie.id, filename[filename.rindex('.'):])
            poster.save('%s/images/poster/%s' % (current_app.static_folder, filename))
            movie.poster = filename
        elif is_created:
            raise ValidationError("poster required")
        else:
            movie.poster = form.poster.object_data

        if form.description.data.strip() == '':
            movie.description = '暂无介绍'


class RecommendModelView(MyModelView):
    column_list = form_columns = ('id', 'movieId', 'type')


class ScreenModelView(MyModelView):
    form_columns = column_list = ('id', 'movieId', 'price', 'ticketNum', 'time')


class OrderModelView(MyModelView):
    form_columns = column_list = ('id', 'movieId', 'screenId', 'seat', 'username', 'createTime', 'type')


class CouponModelView(MyModelView):
    form_columns = column_list = ('id', 'discount', 'conditions', 'username', 'createTime', 'orderId')


class FavoriteModelView(MyModelView):
    column_list = form_columns = ('id', 'movieId', 'username')


class CommentModelView(MyModelView):
    column_list = form_columns = ('id', 'movieId', 'username', 'content', 'rating')


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not isAdmin():
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        form = LoginForm(request.form)

        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)

        if isAdmin():
            return redirect(url_for('.index'))

        self._template_args['form'] = form
        return super(MyAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        if isAdmin():
            login.logout_user()

        return redirect(url_for('.login_view'))