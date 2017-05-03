# -*- coding: utf-8 -*-
from uuid import uuid4
from flask_login import UserMixin
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """用户"""
    __tablename__ = 'users'
    __table_args__ = {'mysql_engine': 'InnoDB'}  # 支持事务操作和外键

    id = db.Column(db.String(11), primary_key=True, doc='手机号码')
    password = db.Column(db.String(32), nullable=False, doc='密码')
    nickname = db.Column(db.String(20), default='猿眼用户', nullable=False, doc='昵称')
    avatar = db.Column(db.String(20), default='MonkeyEye.jpg', nullable=False, doc='头像路径')
    description = db.Column(db.String(50), default='这个人很懒，什么也没留下', nullable=False, doc='个性签名')
    isAdmin = db.Column(db.Boolean, default=False, nullable=False, doc='是否管理员')

    orders = db.relationship('Order', backref='users', lazy='dynamic')
    coupons = db.relationship('Coupon', backref='users', lazy='dynamic')
    favorites = db.relationship('Favorite', backref='users', lazy='dynamic')
    comments = db.relationship('Comment', backref='users', lazy='dynamic')

    def __json__(self):
        return dict(id=self.id,
                      nickname=self.nickname,
                      avatar='static/images/user/%s' % self.avatar,
                      description=self.description)

class Movie(db.Model):
    """电影"""
    __tablename__ = 'movies'
    __table_args__ = {'mysql_engine': 'InnoDB'}  # 支持事务操作和外键

    id = db.Column(db.String(32), primary_key=True, default=uuid4().hex)
    name = db.Column(db.String(30), nullable=False, doc='电影名称')
    poster = db.Column(db.String(50), nullable=False, doc='海报路径')
    description = db.Column(db.Text, default='暂无介绍', nullable=False, doc='电影介绍')
    playingTime = db.Column(db.Date, default=date.today(), nullable=False, doc='上映时间')
    duration = db.Column(db.SmallInteger, nullable=False, doc='电影时长(分钟)')
    movieType = db.Column(db.String(30), nullable=False, doc='电影类型')
    playingType = db.Column(db.String(30), doc='放映类型')
    rating = db.Column(db.DECIMAL, default=0, doc='电影评分')
    ratingNum = db.Column(db.SmallInteger, default=0, doc='评分人数')

    recommends = db.relationship('Recommend', backref='movies', lazy='dynamic')
    screens = db.relationship('Screen', backref='movies', lazy='dynamic')
    orders = db.relationship('Order', backref='movies', lazy='dynamic')
    comments = db.relationship('Comment', backref='movies', lazy='dynamic')
    favorites = db.relationship('Favorite', backref='movies', lazy='dynamic')


class Recommend(db.Model):
    """推荐"""
    __tablename__ = 'recommends'
    __table_args__ = {'mysql_engine': 'InnoDB'}  # 支持事务操作和外键

    id = db.Column(db.String(32), primary_key=True, default=uuid4().hex)
    type = db.Column(db.Boolean, nullable=False, doc='正在热映|即将上映')
    movieId = db.Column(db.String(32), db.ForeignKey('movies.id', ondelete='CASCADE'), nullable=False)


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
