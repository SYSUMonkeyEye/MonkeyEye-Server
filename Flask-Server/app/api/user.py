from flask import Blueprint

from app.api import smsnum

user = Blueprint('user', __name__)


@user.route('/')
def hello_world():
    return "hello"