# *-* coding: utf-8 *-*
import time
from uuid import uuid4
from redis import Redis
from hashlib import md5
from flask_login import current_user


myRedis = Redis()
UUID = lambda: uuid4().hex
MD5 = lambda s: md5(s).hexdigest()
MD5Twice = lambda s: MD5(MD5(s))
checkPassword = lambda s: s.isalnum()
isValid = lambda x, y: len(x) == y and x.isdigit()
time2stamp = lambda t: time.mktime(t.timetuple()) * 1000


def isAdmin():
    try:
        if current_user.isAdmin:
            return True
    except AttributeError:
        return False


# 检查短信验证码, 10分钟内有效
def checkMobileAndCode(mobile, code):
    if not isValid(mobile, 11):
        return False, {'message': '手机号码非法'}

    if not isValid(code, 6):
        return False, {'message': '验证码非法'}

    name = 'smscode:%s' % mobile
    smscode = myRedis.get(name)
    if smscode is None:
        return False, {'message': '请先获取短信验证码'}

    if smscode != code:
        return False, {'message': '验证码错误'}

    myRedis.delete(name)
    return True,
