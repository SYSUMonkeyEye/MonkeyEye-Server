# *-* coding: utf-8 *-*
from flask import request
from app.utils import UUID
from app.models import Favorite, Movie, db
from flask_restplus import Namespace, Resource
from flask_login import current_user, login_required

api = Namespace('favorite', description='收藏模块')


@api.route('/')
class FavoritesResource(Resource):
    @login_required
    def get(self):
        """获取收藏列表"""
        return [f.__json__() for f in current_user.favorites], 200

    @login_required
    @api.doc(parser=api.parser().add_argument(
        'movieId', type=str, required=True, help='电影id', location='form')
    )
    def post(self):
        """收藏电影(需登录)"""
        mid = request.form.get('movieId', '')
        movie = Movie.query.get(mid)
        if movie is None:
            return {'message': '电影不存在'}, 233
        movie = current_user.favorites.filter_by(movieId=mid).first()
        if movie is not None:
            return {'message': '不能重复收藏同部电影'}, 233

        favorite = Favorite()
        favorite.id = UUID()
        favorite.username = current_user.id
        favorite.movieId = mid
        db.session.add(favorite)
        db.session.commit()

        return {'message': '收藏成功', 'id': favorite.id}, 200,


@api.route('/<id>')
@api.doc(params={'id': '收藏id'})
class FavoriteResource(Resource):
    @login_required
    def delete(self, id):
        """取消收藏(需登录)"""
        favorite = current_user.favorites.filter_by(id=id).first()
        if favorite is None:
            return {'message': '您没有这个收藏'}, 233
        db.session.delete(favorite)
        db.session.commit()
        return {'message': '取消收藏成功'}, 200