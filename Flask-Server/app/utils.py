# *-* coding: utf-8 *-*
import time
from uuid import uuid4
from hashlib import md5
from datetime import datetime
from flask_login import current_user

mobile_code = {}
UUID = lambda : uuid4().hex
MD5 = lambda s: md5(s).hexdigest()
MD5Twice = lambda s: MD5(MD5(s))
checkPassword = lambda s: s.isalnum()
isValid = lambda x, y: len(x) == y and x.isdigit()

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

    info = mobile_code.get(mobile, None)
    if info is None:
        return False, {'message': '请先获取短信验证码'}

    if info.get('code', 0) != int(code):
        return False, {'message': '验证码错误'}

    mobile_code.pop(mobile)
    now = datetime.now()
    if (now - info.get('lasttime')).seconds < 600:
        return True,

    return False, {'message': '验证码已过期'}


#  每隔一个小时删除已过期的手机信息
def __popExpiredItems():
    expired = []
    for mobile in mobile_code:
        now = datetime.now()
        # 验证码已过期
        if (now - mobile_code.get(mobile).get('lasttime')).seconds > 600:
            expired.append(mobile)

    # 删除已过期的手机信息
    for mobile in expired:
        mobile_code.pop(mobile)

    time.sleep(3600)
    __popExpiredItems()


# 定时器，新开线程，避免阻塞主进程
from threading import Timer

Timer(0, __popExpiredItems).start()