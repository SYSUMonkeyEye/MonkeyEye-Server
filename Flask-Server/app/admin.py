# -*- coding: utf-8 -*-
from hashlib import md5
from flask_admin import Admin
from models import *
from flask_admin.contrib.sqla import ModelView


class ModelView(ModelView):
    column_display_pk = True  # 显示主键


class __UserModelView(ModelView):
    column_exclude_list = ('password')  # 不显示密码
    form_edit_rules = ('id', 'nickname', 'image')  # 可编辑的字段
    form_columns = ('id', 'password', 'nickname', 'image')  # 可插入的字段
    column_searchable_list = ('id', 'nickname', 'image')

    # 新建用户时进行密码哈希
    def on_model_change(self, form, User, is_created=False):
        if is_created:
            User.password = md5(form.password.data).hexdigest()


class __MovieModelView(ModelView):
    column_searchable_list = ('id', 'name', 'description', 'duration')
    form_excluded_columns = ('recommends')


class __RecommendModelView(ModelView):
    form_columns = column_list = ['id', 'movieId', 'type']


class __ScreenModelView(ModelView):
    form_columns = column_list = ['id', 'movieId', 'price', 'ticketNum', 'time']

admin = Admin(name='猿眼管理系统', template_mode='bootstrap3')
userModelView = __UserModelView(User, db.session, name='用户管理')
movieModelView = __MovieModelView(Movie, db.session, name='电影管理')
recommendModelView = __RecommendModelView(Recommend, db.session, name='推荐管理')
screenModelView = __ScreenModelView(Screen, db.session, name='场次管理')

admin.add_view(userModelView)
admin.add_view(movieModelView)
admin.add_view(recommendModelView)
admin.add_view(screenModelView)
