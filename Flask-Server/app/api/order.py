# *-* coding: utf-8 *-*
from flask import request
from datetime import datetime
from ..models import Order, Screen, db
from flask_restplus import Namespace, Resource
from flask_login import login_required, current_user

api = Namespace('order', description='订单模块')

@api.route('/')
class OrdersResource(Resource):
    @login_required
    def get(self):
        """获取用户的订单列表(需登录)"""
        return [o.__json__() for o in current_user.orders], 200


    @api.doc(parser=api.parser()
             .add_argument('screenId', required=True, help='场次id', location='form')
             .add_argument('seat', required=True, help='座位(逗号分隔)', location='form'))
    @login_required
    def post(self):
        """创建订单(需登录)"""
        try:
            now = datetime.now()
            form = request.form

            screenId = form.get('screenId', '')
            screen = Screen.query.get(screenId)
            if screen is None:
                return {'message':'场次不存在'}, 233

            if now > screen.time:
                return {'message':'该场次已上映'}, 233

            need_pay_order = current_user.orders.filter_by(status=0).first()
            if need_pay_order is not None:
                delta = (now - need_pay_order.createTime).seconds
                if delta < 600:
                    return {'message': '您还有未支付的订单'}, 233
                else:
                    db.session.delete(need_pay_order)
                    db.session.commit()

            seats = form.get('seat', '').strip()
            if len(seats) == 0:
                return {'message':'座位号非法'}, 233
            seats = map(int, seats.split(','))

            if len(seats) > 4:
                return {'message':'您一次最多购买4张票'}, 233

            # 获取该场次已出售的座位
            seat_ordered = set()
            for o in screen.orders:
                seat_ordered.update(set(o.seat))

            if len(seat_ordered) == screen.ticketNum:
                return {'message':'该场次电影票已卖完'}, 233

            err = [s for s in seats if s in seat_ordered]
            if len(err):
                return {'message':'座位 %r 已经被预订' % err}, 233

            order = Order()
            order.screenId = screenId
            order.seat = seats
            order.username = current_user.id
            db.session.add(order)
            db.session.commit()
            return {'message':'订单创建成功'}, 200
        except Exception as e:
            print e
            return {'message':'Internal Server Error'}, 500


@api.route('/<id>')
@api.doc(params={'id': '订单id'})
class MovieResource(Resource):
    @login_required
    def get(self, id):
        """获取订单信息(需登录)"""
        print dir(current_user.orders)
        order = current_user.orders.filter_by(id=id).first()
        if order is None:
            return {'message': '订单不存在'}, 233

        return order.__json__(), 200
