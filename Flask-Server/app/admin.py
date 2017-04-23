# -*- coding: utf-8 -*-
from hashlib import md5
from flask_admin import Admin
from models import db, User, Movie
from flask_admin.contrib.sqla import ModelView


class __UserModelView(ModelView):
    column_display_pk = True  # 显示主键
    column_exclude_list = ('password')  # 不显示密码
    form_edit_rules = ('mobile', 'name', 'avatar', 'gender')  # 可编辑的字段
    form_columns = ('mobile', 'password', 'name', 'avatar', 'gender')  # 可插入的字段
    column_searchable_list = ('mobile', 'name', 'avatar')

    # 新建用户时进行密码哈希
    def on_model_change(self, form, User, is_created=False):
        if is_created:
            User.password = md5(form.password.data).hexdigest()


class __MovieModelView(ModelView):
    column_display_pk = True
    column_searchable_list = ('id', 'name', 'description', 'length')


admin = Admin(name='猿眼管理系统', template_mode='bootstrap3')
userModelView = __UserModelView(User, db.session, name='用户管理')
movieModelView = __MovieModelView(Movie, db.session, name='电影管理')

admin.add_view(userModelView)
admin.add_view(movieModelView)
