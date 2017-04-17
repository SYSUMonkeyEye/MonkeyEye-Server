# *-* coding: utf-8
import time
import random
import top.api
import datetime
from threading import Timer
from flask import Blueprint, request, jsonify, current_app


def checkSmsNum(mobile, code):
    if isValid(mobile, 11) and isValid(code, 6):
        info = MobileCode.get(mobile, None)
        if info != None and info.get("code", "") == int(code):
            now = datetime.datetime.now()
            if (now - info.get("lasttime")).seconds < 600:
                MobileCode.pop(mobile)
                return "pass"
            return "expired code"

    return "invalid args"


def _popExpiredItems():
    for mobile in MobileCode:
        now = datetime.datetime.now()
        if (now - MobileCode.get(mobile).get("lasttime")).seconds > 600:
            MobileCode.pop(mobile)

    time.sleep(1800)
    _popExpiredItems()


smsnum = Blueprint('smsnum', __name__)
MobileCode = {}
isValid = lambda x, y: len(x) == y and x.isdigit()
timer = Timer(10, _popExpiredItems)
timer.start()


@smsnum.route('/api/smsnum')
def getSmsNum():
    mobile = request.args.get("mobile", "")
    if isValid(mobile, 11):
        info = MobileCode.get(mobile, None)
        now = datetime.datetime.now()
        if info == None or (now - info.get("lasttime")).seconds > 90:
            req = top.api.AlibabaAliqinFcSmsNumSendRequest()
            config = current_app._get_current_object().config
            req.set_app_info(
                top.appinfo(config.get("APPKEY"), config.get("APPSECRET")))

            req.extend = "123456"
            req.sms_type = "normal"
            req.sms_free_sign_name = "猿眼电影"
            req.sms_template_code = "SMS_62200286"
            code = random.randint(100000, 999999)
            req.sms_param = '{"code":"%d"}' % code
            req.rec_num = mobile
            try:
                # resp = req.getResponse()
                # print type(resp)
                # print(resp)
                MobileCode.update({mobile: {
                    "lasttime": datetime.datetime.now(),
                    "code": code
                }})
                return jsonify({"status": 200, "msg": code})
            except Exception as e:
                print(e)
                return jsonify({"status": 500, "msg": str(e)})

        return jsonify({"status": 403, "msg": "wait a minute"})
    return jsonify({"status": 403, "msg": "invalid mobile number"})
