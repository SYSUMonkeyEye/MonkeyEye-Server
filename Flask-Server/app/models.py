# -*- coding: utf-8 -*-
from uuid import uuid4
from datetime import datetime, date
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = {'mysql_engine': 'InnoDB'}  # 支持事务操作和外键

    id = db.Column(db.String(11), primary_key=True, doc='手机号码')
    password = db.Column(db.String(32), nullable=False, doc='密码')
    nickname = db.Column(db.String(20), default='猿眼用户', nullable=False, doc='昵称')
    image = db.Column(db.String(32), default='MonkeyEye', nullable=False, doc='头像路径')


class Movie(db.Model):
    __tablename__ = 'movies'
    __table_args__ = {'mysql_engine': 'InnoDB'}  # 支持事务操作和外键

    id = db.Column(db.String(32), primary_key=True, default=uuid4().hex)
    name = db.Column(db.String(30), nullable=False, doc='电影名称')
    description = db.Column(db.Text, nullable=False, doc='电影介绍')
    duration = db.Column(db.SmallInteger, nullable=False, doc='电影时长(分钟)')
    rating = db.Column(db.SmallInteger, doc='电影评分')
    poster = db.Column(db.String(50), nullable=False, doc='海报路径')
    movieType = db.Column(db.String(30), nullable=False, doc='电影类型')
    playingTime = db.Column(db.Date, default=date.today(), doc='上映时间')
    playingType = db.Column(db.String(30), doc='放映类型')

    recommends = db.relationship('Recommend', backref='movies', lazy='dynamic')
    screens = db.relationship('Screen', backref='movies', lazy='dynamic')


class Recommend(db.Model):
    __tablename__ = 'recommends'
    __table_args__ = {'mysql_engine': 'InnoDB'}  # 支持事务操作和外键

    id = db.Column(db.String(32), primary_key=True, default=uuid4().hex)
    type = db.Column(db.String(1), nullable=False, doc='正在热映|即将上映')
    movieId = db.Column(db.String(32), db.ForeignKey('movies.id'), nullable=False)


class Screen(db.Model):
    __tablename__ = 'screens'
    __table_args__ = {'mysql_engine': 'InnoDB'}  # 支持事务操作和外键

    id = db.Column(db.String(32), primary_key=True, default=uuid4().hex)
    movieId = db.Column(db.String(32), db.ForeignKey('movies.id'), nullable=False)
    price = db.Column(db.DECIMAL, nullable=False, doc='票价')
    ticketNum = db.Column(db.SmallInteger, nullable=False, doc='电影票序号')
    time = db.Column(db.DateTime, nullable=False, default=datetime.now())


class Order(db.Model):
    __tablename__ = 'orders'
    __table_args__ = {'mysql_engine': 'InnoDB'}  # 支持事务操作和外键

    id = db.Column(db.String(32), primary_key=True, default=uuid4().hex)
    movieId = db.Column(db.String(32), db.ForeignKey('movies.id'), nullable=False)
    screenId = db.Column(db.String(32), db.ForeignKey('screens.id'), nullable=False)
    ticketNum = db.Column(db.SmallInteger, nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.now())
    seat = db.Column(db.SmallInteger, nullable=False)
    username = db.Column(db.String(32), db.ForeignKey('users.id'), nullable=False)
    createTime = db.Column(db.DateTime, nullable=False, default=datetime.now())


class Coupon(db.Model):
    __tablename__ = 'coupons'
    __table_args__ = {'mysql_engine': 'InnoDB'}  # 支持事务操作和外键

    id = db.Column(db.String(32), primary_key=True, default=uuid4().hex)
    discount = db.Column(db.DECIMAL, nullable=False, default=0.8, doc='折扣')
    conditions = db.Column(db.DECIMAL, nullable=False)
    username = db.Column(db.String(32), db.ForeignKey('users.id'), nullable=False, doc='手机号码')
    createTime = db.Column(db.DateTime, nullable=False, default=datetime.now(), doc='创建时间')