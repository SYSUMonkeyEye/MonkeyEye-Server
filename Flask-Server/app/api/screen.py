# *-* coding: utf-8 *-*
from app.models import Screen
from flask_restplus import Namespace, Resource

api = Namespace('screen', description='场次模块')

@api.route('/')
class ScreensResource(Resource):
    def get(self):
        """获取场次列表"""
        result = [screen.__json__() for screen in Screen.query.all()]
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