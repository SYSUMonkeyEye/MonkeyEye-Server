# -*- coding: utf-8 -*-
import time
from uuid import uuid4
from flask_login import UserMixin
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """用户"""
    __tablename__ = 'users'
    __table_args__ = {'mysql_engine': 'InnoDB'}  # 支持事务操作和外键

    id = db.Column(db.String(11), doc='手机号码', primary_key=True)
    password = db.Column(db.String(32), doc='密码', nullable=False)
    nickname = db.Column(db.String(20), doc='昵称', default='猿眼用户', nullable=False)
    avatar = db.Column(db.String(20), doc='头像路径', default='MonkeyEye.jpg')
    description = db.Column(db.String(50), doc='个性签名', default='这个人很懒，什么也没留下', nullable=False)
    isAdmin = db.Column(db.Boolean, doc='是否管理员', default=False)

    orders = db.relationship('Order', backref='users', lazy='dynamic')
    coupons = db.relationship('Coupon', backref='users', lazy='dynamic')
    favorites = db.relationship('Favorite', backref='users', lazy='dynamic')
    comments = db.relationship('Comment', backref='users', lazy='dynamic')

    def __repr__(self):
        return '%s <%s>' % (self.nickname, self.id)

    def __json__(self):
        return {
            'id': self.id,
            'nickname': self.nickname,
            'avatar': 'static/images/user/%s' % self.avatar,
            'description': self.description
        }


class Movie(db.Model):
    """电影"""
    __tablename__ = 'movies'
    __table_args__ = {'mysql_engine': 'InnoDB'}  # 支持事务操作和外键

    id = db.Column(db.String(32), primary_key=True, default=uuid4().hex)
    expired = db.Column(db.Boolean, doc='是否下架', default=False, nullable=False)
    name = db.Column(db.String(25), doc='电影名称', nullable=False)
    description = db.Column(db.Text, doc='电影介绍', default='暂无介绍', nullable=False)
    playingTime = db.Column(db.Date, doc='上映时间', default=date.today(), nullable=False)
    duration = db.Column(db.SmallInteger, doc='电影时长(分钟)', nullable=False)
    movieType = db.Column(db.String(30), doc='电影类型', nullable=False)
    playingType = db.Column(db.String(30), doc='放映类型', nullable=False)
    rating = db.Column(db.Float, doc='电影评分', default=0)
    ratingNum = db.Column(db.SmallInteger, doc='评分人数', default=0)
    poster = db.Column(db.String(40), doc='海报路径')

    screens = db.relationship('Screen', backref='movies', lazy='dynamic')
    orders = db.relationship('Order', backref='movies', lazy='dynamic')
    comments = db.relationship('Comment', backref='movies', lazy='dynamic')
    favorites = db.relationship('Favorite', backref='movies', lazy='dynamic')

    def __repr__(self):
        return self.name

    def __json__(self):
        return {
            'id': self.id,
            'name': self.name,
            'poster': 'static/images/poster/%s' % self.poster,
            'movieType': self.movieType,
            'playingType': self.playingType,
            'playingTime': time.mktime(self.playingTime.timetuple()) * 1000,
            'duration': self.duration,
            'rating': self.rating,
            'description': self.description
        }

class Screen(db.Model):
    """场次"""
    __tablename__ = 'screens'
    __table_args__ = {'mysql_engine': 'InnoDB'}  # 支持事务操作和外键

    id = db.Column(db.String(32), primary_key=True, default=uuid4().hex)
    movieId = db.Column(db.String(32), db.ForeignKey('movies.id', ondelete='CASCADE'), nullable=False)
    price = db.Column(db.DECIMAL, nullable=False, default=30, doc='票价')
    ticketNum = db.Column(db.SmallInteger, nullable=False, doc='电影总票数')
    time = db.Column(db.DateTime, nullable=False, default=datetime.now())

    orders = db.relationship('Order', backref='screens', lazy='dynamic')


class Order(db.Model):
    """订单"""
    __tablename__ = 'orders'
    __table_args__ = {'mysql_engine': 'InnoDB'}  # 支持事务操作和外键

    id = db.Column(db.String(32), primary_key=True, default=uuid4().hex)
    movieId = db.Column(db.String(32), db.ForeignKey('movies.id', ondelete='CASCADE'), nullable=False)
    screenId = db.Column(db.String(32), db.ForeignKey('screens.id', ondelete='CASCADE'), nullable=False)
    seat = db.Column(db.SmallInteger, nullable=False, doc='座位号')
    username = db.Column(db.String(32), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    createTime = db.Column(db.DateTime, default=datetime.now(), nullable=False, doc='创建时间')
    type = db.Column(db.String(1), default='0', nullable=False, doc='订单类型')


class Coupon(db.Model):
    """优惠券"""
    __tablename__ = 'coupons'
    __table_args__ = {'mysql_engine': 'InnoDB'}  # 支持事务操作和外键

    id = db.Column(db.String(32), primary_key=True, default=uuid4().hex)
    discount = db.Column(db.DECIMAL, nullable=False, default=0.8, doc='折扣')
    conditions = db.Column(db.DECIMAL, nullable=False, doc='满多少元可用')
    username = db.Column(db.String(32), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, doc='手机号码')
    createTime = db.Column(db.DateTime, nullable=False, default=datetime.now(), doc='创建时间')
    orderId = db.Column(db.String(32), db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)

class Favorite(db.Model):
    """收藏"""
    __tablename__ = 'favorites'
    __table_args__ = {'mysql_engine': 'InnoDB'}  # 支持事务操作和外键

    id = db.Column(db.String(32), primary_key=True, default=uuid4().hex)
    username = db.Column(db.String(32), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, doc='手机号码')
    movieId = db.Column(db.String(32), db.ForeignKey('movies.id', ondelete='CASCADE'), nullable=False)


class Comment(db.Model):
    """评论"""
    __tablename__ = 'comments'
    __table_args__ = {'mysql_engine': 'InnoDB'}  # 支持事务操作和外键

    id = db.Column(db.String(32), primary_key=True, default=uuid4().hex)
    username = db.Column(db.String(32), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, doc='手机号码')
    movieId = db.Column(db.String(32), db.ForeignKey('movies.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.Text, nullable=False, doc='评论内容')
    rating = db.Column(db.SmallInteger, nullable=False, doc='电影评分')
