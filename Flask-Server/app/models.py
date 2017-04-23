# -*- coding: utf-8 -*-
from uuid import uuid4
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    mobile = db.Column(db.String(11), primary_key=True)
    password = db.Column(db.String(32), nullable=False)
    name = db.Column(db.String(20), default='猿眼用户', nullable=False)
    avatar = db.Column(db.String(32), default='MonkeyEye', nullable=False)
    gender = db.Column(db.String(1))


class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.String(32), primary_key=True, default=uuid4().hex)
    name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.Text, nullable=False)
    length = db.Column(db.SmallInteger, nullable=False)
