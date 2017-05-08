# *-* coding: utf-8 *-*
from app.models import Order
from flask_restplus import Namespace, Resource
from flask_login import login_required, current_user

api = Namespace('order', description='订单模块')

@api.route('/')
class OrdersResource(Resource):
    @login_required
    def get(self):
        """获取用户的订单列表"""
        userId = current_user.id
        result = [order.__json__() for order in Order.query.filter_by(username=userId).all()]
        return result, 200

    @login_required
    def post(self):
        """创建订单"""
        return '', 200


@api.route('/<id>')
@api.doc(params={'id': '订单id'})
class MovieResource(Resource):
    @login_required
    def get(self, id):
        """获取订单信息"""
        order = Order.query.filter_by(username=current_user.id).get(id)
        if order is None:
            return {'message': 'Order does not exist'}, 400

        return order.__json__(), 200