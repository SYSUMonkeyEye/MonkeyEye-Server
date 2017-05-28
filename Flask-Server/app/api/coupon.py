# *-* coding: utf-8 *-*
from flask_restplus import Namespace, Resource
from flask_login import current_user, login_required

api = Namespace('coupon', description='优惠券模块')


@api.route('/')
class CouponsResource(Resource):
    @login_required
    def get(self):
        """获取优惠券列表(需登录)"""
        return [c.__json__() for c in current_user.coupons], 200