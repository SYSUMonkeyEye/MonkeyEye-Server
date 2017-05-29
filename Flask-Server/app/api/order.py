# *-* coding: utf-8 *-*
from ..utils import MD5
from flask import request
from datetime import datetime
from ..models import Order, Screen, db
from flask_restplus import Namespace, Resource
from flask_login import login_required, current_user

api = Namespace('order', description='订单模块')


@api.route('/')
class OrdersResource(Resource):
    def delete_expired_order(self, oid):
        db.engine.execute(
            "CREATE EVENT `%s` \
            ON SCHEDULE AT CURRENT_TIMESTAMP + INTERVAL 10 MINUTE \
            ON COMPLETION NOT PRESERVE \
            ENABLE \
            DO \
            DELETE FROM orders WHERE id = '%s' AND status = 0;" % (oid, oid)
        )

    @login_required
    def get(self):
        """获取订单列表(需登录)"""
        return [o.__json__() for o in current_user.orders], 200

    @api.doc(parser=api.parser().add_argument(
        'screenId', required=True, help='场次id', location='form')
        .add_argument(
        'seat', required=True, help='座位(逗号分隔)', location='form')
    )
    @login_required
    def post(self):
        """创建订单(需登录)"""
        try:
            now = datetime.now()
            form = request.form

            sid = form.get('screenId', '')
            screen = Screen.query.get(sid)
            if screen is None:
                return {'message': '场次不存在'}, 233

            if now > screen.time:
                return {'message': '该场次已上映'}, 233

            need_pay_order = current_user.orders.filter_by(status=0).first()
            if need_pay_order is not None:
                return {'message': '您还有未支付的订单'}, 233

            try:
                seats = map(int, form.get('seat', '').strip().split(','))
                if len(seats) == 0 or len(
                        filter(lambda x: x < 1 or x > screen.ticketNum, seats)
                ) > 0:
                    return {'message': '座位号非法'}, 233

                if len(seats) > 4:
                    return {'message': '您一次最多购买4张票'}, 233
            except Exception:
                return {'message': '座位号非法'}, 233

            # 获取该场次已出售的座位
            seat_ordered = set()
            for o in screen.orders:
                seat_ordered.update(set(o.seat))

            err = [s for s in seats if s in seat_ordered]
            if len(err):
                return {'message': '座位 %s 已经被预订' % ','.join(err)}, 233

            order = Order()
            order.screenId = sid
            order.seat = seats
            order.username = current_user.id
            db.session.add(order)
            db.session.commit()
            self.delete_expired_order(order.id)
            return {'message': '订单创建成功', 'id': order.id}, 200
        except Exception as e:
            print e
            return {'message': 'Internal Server Error'}, 500


@api.route('/<id>')
@api.doc(params={'id': '订单id'})
class OrderResource(Resource):
    @login_required
    def get(self, id):
        """获取订单信息(需登录)"""
        order = current_user.orders.filter_by(id=id).first()
        if order is None:
            return {'message': '订单不存在'}, 233

        return order.__json__(), 200

    @login_required
    def delete(self, id):
        """取消订单(需登录)"""
        order = current_user.orders.filter_by(id=id).first()
        if order is None:
            return {'message': '订单不存在'}, 233
        if order.status:
            return {'message': '订单已支付，无法取消'}, 233
        db.session.delete(order)
        db.session.commit()
        return {'message': '取消订单成功'}, 200

    @login_required
    @api.doc(parser=api.parser().add_argument(
        'couponId', help='优惠券id', location='form')
        .add_argument(
        'payPassword', help='支付密码md5值', required=True, location='form')
    )
    def patch(self, id):
        """订单支付(需登录)"""
        if current_user.payPassword != MD5(request.form.get('payPassword', '')):
            return {'message': '支付密码错误'}, 233

        order = current_user.orders.filter_by(id=id).first()
        if order is None:
            return {'message': '订单不存在'}, 233

        if order.status:
            return {'message': '订单已支付'}, 233

        seats = order.seat
        price = len(seats) * Screen.query.get(order.screenId).price
        order.totalPrice = price
        coupon = None
        cid = request.form.get('couponId', None)
        if cid is not None:
            coupon = current_user.coupons.filter_by(id=cid).first()
            if coupon is None:
                return {'message': '优惠券不存在'}, 233
            if coupon.status:
                return {'message': '优惠券已使用'}, 233
            if price < coupon.conditions:
                return {'message': '未达到优惠金额'}, 233
            price = min(0, price - coupon.discount)

        if current_user.money < price:
            return {'message': '账户余额不足'}, 233

        if coupon is not None:
            coupon.status = True
            order.couponId = coupon.id
        order.status = True
        order.payPrice = price
        current_user.money -= price
        db.session.commit()
        return {'message': '支付成功'}, 200
