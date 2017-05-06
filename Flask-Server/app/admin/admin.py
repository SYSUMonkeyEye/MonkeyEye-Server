# -*- coding: utf-8 -*-
from views import *
from flask import jsonify, make_response
from flask_admin import Admin


def init_login(app):
    """初始化登录"""
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(id):
        return db.session.query(User).get(id)

    @login_manager.unauthorized_handler
    def unauthorized_callback():
        return make_response(jsonify({'message':'Unauthorized. Login first'}), 401)


admin = Admin(name='猿眼管理系统', template_mode='bootstrap3',
              index_view=MyAdminIndexView(), base_template='admin.html')
userModelView = UserModelView(User, db.session, name='用户管理')
movieModelView = MovieModelView(Movie, db.session, name='电影管理')
screenModelView = ScreenModelView(Screen, db.session, name='场次管理')
recommendModelView = RecommendModelView(Recommend, db.session, name='推荐管理')
orderModelView = OrderModelView(Order, db.session, name='订单管理')
commentModelView = CommentModelView(Comment, db.session, name='评论管理')
couponModelView = CouponModelView(Coupon, db.session, name='优惠券管理')
favoriteModelView = FavoriteModelView(Favorite, db.session, name='收藏管理')

admin.add_view(userModelView)
admin.add_view(movieModelView)
admin.add_view(screenModelView)
admin.add_view(recommendModelView)
admin.add_view(orderModelView)
admin.add_view(commentModelView)
admin.add_view(couponModelView)
admin.add_view(favoriteModelView)