# *-* coding: utf-8 *-*
from flask import request
from app.models import Movie
from flask_restplus import Namespace, Resource

api = Namespace('movie', description='电影模块')

@api.route('/')
class MoviesResource(Resource):
    @api.doc(parser=api.parser().add_argument('query', type=str, help='电影搜索', location='args'))
    def get(self):
        """获取电影列表"""
        query = request.args.get('query', False)
        if not query or query.strip() == '':
            result = [movie.__json__() for movie in Movie.query.filter_by(expired=False).all()]
        else:
            result = [movie.__json__()
                      for movie in Movie.query.filter_by(expired=False)
                    .filter(Movie.name.like('%{}%'.format(query))).all()]

        return result, 200


@api.route('/<id>')
@api.doc(params={'id': '电影id'})
class MovieResource(Resource):
    def get(self, id):
        """获取电影信息"""
        movie = Movie.query.get(id)
        if movie is None:
            return {'message': 'Movie does not exist'}, 400
        return movie.__json__(), 200