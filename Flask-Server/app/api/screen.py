# *-* coding: utf-8 *-*
from flask import request
from app.models import Screen, Movie
from datetime import datetime, date, timedelta
from flask_restplus import Namespace, Resource

api = Namespace('screen', description='场次模块')

@api.route('/')
class ScreensResource(Resource):
    @api.doc(parser=api.parser().add_argument('movieId', type=str, required=True, help='电影id', location='args'))
    def get(self):
        """获取某部电影三天内的场次"""
        movieId = request.args.get('movieId', '')
        movie = Movie.query.get(movieId)
        if movie is None:
            return {'message':'电影不存在'}, 233

        today = date.today()
        twoday = timedelta(days=3)
        screens = movie.screens.filter(Screen.time > datetime.now()) \
                               .filter(Screen.time < today + twoday)
        return [s.__json__() for s in screens], 200


@api.route('/<id>')
@api.doc(params={'id': '场次id'})
class ScreenResource(Resource):
    def get(self, id):
        """获取场次信息"""
        screen = Screen.query.get(id)
        if screen is None:
            return {'message': '场次不存在'}, 233
        return screen.__json__(), 200


@api.route('/<id>/seats')
@api.doc(params={'id': '场次id'})
class ScreenResource(Resource):
    def get(self, id):
        """获取场次已预定的座位号"""
        screen = Screen.query.get(id)
        if screen is None:
            return {'message': '场次不存在'}, 233

        seat_ordered = []
        for o in screen.orders:
            seat_ordered.extend(o.seat)
        return seat_ordered, 200