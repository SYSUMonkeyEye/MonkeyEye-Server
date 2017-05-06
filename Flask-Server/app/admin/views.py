# *-* coding: utf-8 *-*
import os
from ..models import *
from hashlib import md5
import flask_login as login
from flask import current_app
from datetime import timedelta
from ..utils import MD5Twice, isAdmin
from flask import request, redirect, url_for
from flask_admin.contrib.sqla import ModelView
from flask_admin import expose, AdminIndexView, helpers
from wtforms import form, fields, validators, ValidationError


class LoginForm(form.Form):
    """登录表单"""
    username = fields.StringField(validators=[validators.data_required()])
    password = fields.PasswordField(validators=[validators.data_required()])

    def validate_username(self, field):
        """登录校验"""
        user = self.get_user()

        if user is None:
            raise ValidationError('Invalid user')
        if md5(self.password.data).hexdigest() != user.password:
            raise ValidationError('Invalid password')

    def get_user(self):
        return User.query.filter_by(id=self.username.data, isAdmin=1).first()


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

    def on_model_change(self, form, user, is_created):
        avatar = form.avatar.data
        if avatar.content_type.startswith('image/'):
            filename = avatar.filename
            filename = '%s%s' % (user.id, filename[filename.rindex('.'):])
            avatar.save('%s/images/user/%s' % (current_app.static_folder, filename))
            user.avatar = filename
        elif is_created:
            user.avatar = 'MonkeyEye.jpg'
        else:
            user.avatar = form.avatar.object_data

        if is_created:  # 新建用户时密码进行两次md5
            user.password = MD5Twice(form.password.data)

    def after_model_delete(self, user):
        os.remove('%s/images/user/%s' % (current_app.static_folder, user.avatar))


class MovieModelView(MyModelView):
    form_overrides = {'poster': fields.FileField}
    form_columns = ('expired', 'name', 'poster', 'description', 'playingTime', 'duration', 'movieType', 'playingType')
    form_create_rules = form_columns[1:]

    def on_model_change(self, form, movie, is_created):
        poster = form.poster.data
        movie.id = uuid4().hex if is_created else movie.id
        if poster.content_type.startswith('image/'):
            filename = poster.filename
            filename = '%s%s' % (movie.id, filename[filename.rindex('.'):])
            poster.save('%s/images/poster/%s' % (current_app.static_folder, filename))
            movie.poster = filename
        elif is_created:
            raise ValidationError('poster required')
        else:
            movie.poster = form.poster.object_data

        if form.description.data.strip() == '':
            movie.description = '暂无介绍'

    def after_model_change(self, form, movie, is_created):
        if movie.expired:
            recommend = Recommend.query.get(movie.id)
            if recommend is not None:
                db.session.delete(recommend)
                db.session.commit()

    def after_model_delete(self, movie):
        os.remove('%s/images/poster/%s' % (current_app.static_folder, movie.poster))


class ScreenModelView(MyModelView):
    column_list = ('id', 'movies', 'hallNum', 'time', 'price', 'ticketNum')
    form_columns = column_list[1:]
    form_args = {'hallNum': dict(validators=[validators.Regexp('[1-5]', message='hall number is between 1 and 5')])}

    def on_model_change(self, form, screen, is_created):
        time = form.time.data
        movieId = form.movies.raw_data[0]
        if time < datetime.now():
            raise ValidationError('time has passed')
        movie = Movie.query.get(movieId)
        if movie is None:
            raise ValidationError('movie does not exist')
        if movie.expired:
            raise ValidationError('movie is expired')

        # 从昨天开始在同个放映厅的场次
        # 判断同个时间段是否有电影在上映
        yesterday = datetime.today() - timedelta(days=1)
        screens = Screen.query.filter_by(hallNum=form.hallNum.data).filter(Screen.time > yesterday).all()
        endtime = time + timedelta(minutes=movie.duration)

        for s in screens:
            if s is screen:
                continue

            # 合法的场次要求
            # 开始时间比其他场次结束时间晚 或者 结束时间比其他场次开始时间早
            m = Movie.query.get(s.movieId)
            if time > (s.time + timedelta(minutes=m.duration)) or endtime < s.time:
                continue

            raise ValidationError('%r is playing in the same hall at this time' % movie)


class RecommendModelView(MyModelView):
    def on_model_change(self, form, recommend, is_created):
        if Movie.query.get(form.movies.raw_data[0]).expired:
            raise ValidationError('This movie is expired')


class OrderModelView(MyModelView):
    form_columns = column_list = ('id', 'movieId', 'screenId', 'seat', 'username', 'createTime', 'type')


class CouponModelView(MyModelView):
    form_columns = column_list = ('id', 'discount', 'conditions', 'username', 'createTime', 'orderId')


class FavoriteModelView(MyModelView):
    column_list = form_columns = ('id', 'movieId', 'username')


class CommentModelView(MyModelView):
    column_list = ('id', 'movies', 'users', 'content', 'rating')
    form_columns = column_list[1:]


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