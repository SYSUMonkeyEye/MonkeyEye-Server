# *-* coding: utf-8 *-*
from flask import request
from app.models import Screen
from datetime import datetime, date, timedelta
from flask_restplus import Namespace, Resource

api = Namespace('screen', description='场次模块')

@api.route('/')
class ScreensResource(Resource):
    @api.doc(parser=api.parser().add_argument('movieId', type=str, required=True, help='电影id', location='args'))
    def get(self):
        """获取某部电影三天内的场次"""
        movieId = request.args.get('movieId', None)
        if movieId is None:
            return {'message':'Invalid movie id'}, 400

        today = date.today()
        twoday = timedelta(days=2)
        screens = Screen.query.filter_by(movieId=movieId) \
                              .filter(Screen.time > datetime.now()) \
                              .filter(Screen.time < today + twoday).all()
        result = [screen.__json__() for screen in screens]
        return result, 200


@api.route('/<id>')
@api.doc(params={'id': '场次id'})
class ScreenResource(Resource):
    def get(self, id):
        """获取场次信息"""
        screen = Screen.query.get(id)
        if screen is None:
            return {'message': 'Screen does not exist'}, 400
        return screen.__json__(), 200