# *-* coding: utf-8 *-*
import os
from ..models import *
import flask_login as login
from flask import current_app
from datetime import timedelta
from flask import request, redirect, url_for
from flask_admin.contrib.sqla import ModelView
from ..utils import MD5, MD5Twice, isAdmin, UUID
from flask_login import login_required, current_user
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
        if MD5(self.password.data) != user.password:
            raise ValidationError('Invalid password')

    def get_user(self):
        return User.query.filter_by(id=self.username.data, isAdmin=1).first()


class MyModelView(ModelView):
    page_size = 10            # 每页10条数据
    column_display_pk = True  # 显示主键

    def is_accessible(self):
        return isAdmin()


class UserModelView(MyModelView):
    column_exclude_list = ('password', 'payPassword', 'isAdmin')  # 不显示密码
    form_columns = ('id', 'password', 'payPassword', 'nickname',
                    'money', 'avatar', 'description')  # 可插入的字段
    form_edit_rules = form_columns[3:]  # 可编辑的字段
    form_overrides = {'avatar': fields.FileField}
    form_args = {
        'id': {  # id只能11位数字
            'validators': [validators.Regexp('\d{11}', message='Invalid mobile')]
        }
    }

    def on_model_change(self, form, user, is_created):
        avatar = form.avatar.data
        # 用户如果上传头像则进行保存
        if avatar.content_type.startswith('image/'):
            filename = avatar.filename
            filename = '%s%s' % (user.id, filename[filename.rindex('.'):])
            url = '%s/images/user/%s' % (current_app.static_folder, filename)
            avatar.save(url)
            user.avatar = filename
        elif is_created:
            user.avatar = 'MonkeyEye.jpg'
        else:  # 没有上传头像将使用上一次的头像
            user.avatar = form.avatar.object_data

        if is_created:  # 新建用户时密码进行两次md5
            user.password = MD5Twice(form.password.data)
            user.payPassword = MD5Twice(form.payPassword.data)

    def after_model_delete(self, user):
        # 删除用户时删除用户头像
        if user.avatar != 'MonkeyEye.jpg':
            url = '%s/images/user/%s' % (current_app.static_folder, user.avatar)
            os.remove(url)


class MovieModelView(MyModelView):
    column_exclude_list = ('description',)
    form_columns = ('expired', 'name', 'poster', 'description',
                    'playingTime', 'duration', 'movieType', 'playingType')
    form_create_rules = form_columns[1:]
    form_overrides = {'poster': fields.FileField}
    form_args = {
        'movieType': {
            'render_kw': {
                'placeholder': '电影类型, 中文逗号分隔'
            }
        }
    }

    def on_model_change(self, form, movie, is_created):
        poster = form.poster.data
        if is_created:
            movie.id = UUID()
        if poster.content_type.startswith('image/'):
            filename = poster.filename
            filename = '%s%s' % (movie.id, filename[filename.rindex('.'):])
            url = '%s/images/poster/%s' % (current_app.static_folder, filename)
            poster.save(url)
            movie.poster = filename
        elif is_created:
            raise ValidationError('poster required')
        else:
            movie.poster = form.poster.object_data

        if form.description.data.strip() == '':
            movie.description = '暂无介绍'

    def after_model_change(self, form, movie, is_created):
        # 电影下架后删除该电影的推荐
        if movie.expired:
            recommend = Recommend.query.get(movie.id)
            if recommend is not None:
                db.session.delete(recommend)
                db.session.commit()

    def after_model_delete(self, movie):
        # 电影删除后删除电影的海报
        url = '%s/images/poster/%s' % (current_app.static_folder, movie.poster)
        os.remove(url)


class ScreenModelView(MyModelView):
    column_list = ('id', 'movies', 'hallNum', 'time', 'price')
    form_columns = column_list[1:]
    form_edit_rules = column_list[2:]  # 可编辑的字段
    form_args = {
        'hallNum': {
            'validators': [validators.Regexp(
                            '[1-5]', message='hall number is between 1 and 5')],
            'render_kw': {'placeholder': "放映厅, 1~5"}
        },
        'movies': {  # 已上映的未下架的电影可添加场次
            'query_factory':
                lambda: Movie.query.filter_by(expired=False)
                                   .filter(Movie.playingTime < datetime.now())
        }
    }

    def on_model_change(self, form, screen, is_created):
        time = form.time.data
        now = datetime.now()
        if time < now:
            raise ValidationError('time has passed')
        movie = Movie.query.get(screen.movieId)
        if movie is None:
            raise ValidationError('movie does not exist')
        if movie.expired:
            raise ValidationError('movie is expired')

        # 从4个小时前在同个放映厅的场次
        # 判断同个时间段是否有电影在上映
        fourh = now - timedelta(hours=4)
        screens = Screen.query.filter_by(hallNum=form.hallNum.data) \
                              .filter(Screen.time > fourh).all()
        endtime = time + timedelta(minutes=movie.duration)

        for s in screens:
            if s is screen:
                continue

            # 合法的场次要求
            # 开始时间比其他场次结束时间晚 或者 结束时间比其他场次开始时间早
            m = Movie.query.get(s.movieId)
            if time > (s.time + timedelta(minutes=m.duration))\
                    or endtime < s.time:
                continue

            raise ValidationError(
                '%r is playing in the same hall at this time' % movie
            )

        if is_created:
            screen.id = UUID()


class RecommendModelView(MyModelView):
    form_args = dict(movies={
        'query_factory': lambda: Movie.query.filter_by(expired=False)
    })


class OrderModelView(MyModelView):
    column_list = ('id', 'screens', 'seat', 'users',
                   'status', 'createTime', 'couponId')
    form_edit_rules = ('status',)
    form_columns = column_list[1:-1]
    form_overrides = {'seat': fields.StringField}
    form_args = {
        'seat': {
            'render_kw': {
                'placeholder': '座位号, 英文逗号分隔, 最多4个座位'
            }
        },
        # 'type': {
        #     'render_kw': {
        #         'placeholder': '订单状态(0:未支付, 1:已支付)'},
        #     'validators': [validators.Regexp('[01]', message='Invalid order type')]
        # },
        'screens': {  # 订单只能预定未开始的场次
            'query_factory': lambda: Screen.query.filter(Screen.time > datetime.now())
        }
    }

    def delete_expired_order(self, oid):
        db.engine.execute(
            "CREATE EVENT `%s` \
            ON SCHEDULE AT CURRENT_TIMESTAMP + INTERVAL 10 MINUTE \
            ON COMPLETION NOT PRESERVE \
            ENABLE \
            DO \
            DELETE FROM orders WHERE id = '%s' AND status = 0;" % (oid, oid)
        )

    def on_model_change(self, form, order, is_created):
        if not is_created:
            return

        seat = form.seat.data
        sid = form.screens.raw_data[0]
        screen = Screen.query.get(sid)

        if form.createTime.data > screen.time:
            raise ValidationError('The screen has been played')

        user = User.query.get(order.username)
        need_pay_order = user.orders.filter_by(status=0).first()
        if need_pay_order is not None and need_pay_order is not order:
            raise ValidationError('您还有未支付的订单')

        try:
            seats = map(int, seat.strip().split(','))
            if len(seats) == 0 or len(
                    filter(lambda x: x < 1 or x > screen.ticketNum, seats)) > 0:
                raise ValidationError('Invalid seat')

            if len(seats) > 4:
                raise ValidationError(
                    'You can only buy up to 4 tickets at a time'
                )
        except Exception:
            raise ValidationError('Invalid seat')

        # 获取该场次已出售的座位
        seat_ordered = set()
        for o in screen.orders:
            if o is not order:
                seat_ordered.update(set(o.seat))

        err = [s for s in seats if s in seat_ordered]
        print err
        if len(err):
            raise ValidationError('Seat %r have been ordered' % err)

        order.seat = seats
        order.id = UUID()

    def after_model_change(self, form, order, is_created):
        if is_created:
            self.delete_expired_order(order.id)


class CouponModelView(MyModelView):
    column_list = ('id', 'status',  'users',
                   'discount', 'condition', 'expiredTime')
    form_create_rules = column_list[2:]
    form_edit_rules = ('status',)


class FavoriteModelView(MyModelView):
    column_list = ('id', 'users', 'movies')
    form_columns = column_list[1:]


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
    @login_required
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.login_view'))
