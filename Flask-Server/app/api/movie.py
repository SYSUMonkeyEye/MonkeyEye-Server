# *-* coding: utf-8 *-*
from flask import request
from app.models import Movie, Recommend
from flask_restplus import Namespace, Resource

api = Namespace('movie', description='电影模块')


@api.route('/')
class MoviesResource(Resource):
    @api.doc(parser=api.parser().add_argument(
        'query', type=str, help='电影搜索', location='args')
    )
    def get(self):
        """获取电影列表"""
        query = request.args.get('query', '')
        movies = Movie.query.filter_by(expired=False)
        if query.strip() == '':
            return [m.__json__() for m in movies], 200
        else:
            condition = Movie.name.like('%{}%'.format(query))
            return [m.__json__() for m in movies.filter(condition)], 200


@api.route('/<id>')
@api.doc(params={'id': '电影id'})
class MovieResource(Resource):
    def get(self, id):
        """获取电影信息"""
        movie = Movie.query.get(id)
        if movie is None:
            return {'message': '电影不存在'}, 233
        return movie.__json__(), 200


@api.route('/recommendation')
class RecommendResource(Resource):
    def get(self):
        """获取电影推荐"""
        return [r.__json__() for r in Recommend.query], 200
