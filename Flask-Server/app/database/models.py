# -*- coding: utf-8 -*-
from . import db
from uuid import uuid4
from hashlib import md5


class User(db.Model):
    id = db.Column(db.String(11), primary_key=True)
    password = db.Column(db.String(32))
    name = db.Column(db.String(20))
    avatar = db.Column(db.String(32))

    def __init__(self, id, password, name='猿眼用户', avatar='MonkeyEye'):
        self.id = id
        self.password = md5(password).hexdigest()
        self.name = name
        self.avatar = avatar

    def __repr__(self):
        return '<User %r, mobile %r>' % (self.username, self.id)


class Movie(db.Model):
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(30))
    description = db.Column(db.Text)
    length = db.Column(db.Integer)

    def __init__(self, name, description, length):
        self.name = name
        self.description = description
        self.length = length
        self.id = uuid4().hex

    def __repr__(self):
        return '<Movie %r, %r minutes>' % (self.name, self.length)
