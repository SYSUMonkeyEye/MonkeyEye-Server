# *-* coding: utf-8

import app
import random
import top.api
import datetime
from flask import Blueprint, request

smsnum = Blueprint('smsnum', __name__)
isValid = lambda x, y: len(x) == y and x.isdigit()

MobileCode = {}

@smsnum.route('/api/smsnum', method = ['POST'])
def getSmsNum():
    mobile = request.form.get("mobile", "")
    if isValid(mobile, 11):
        info = MobileCode.get(mobile, None)
        now = datetime.datetime.now()
        if info == None or (now - info.get("lasttime")).seconds > 90:
            req = top.api.AlibabaAliqinFcSmsNumSendRequest()
            req.set_app_info(top.appinfo(app.config["APPKEY"], app.config["APPSECRET"]))

            req.extend = "123456"
            req.sms_type = "normal"
            req.sms_free_sign_name = "猿眼电影"
            req.sms_template_code = "SMS_62200286"
            code = random.randint(100000, 999999)
            req.sms_param='{"code":"%d"}' % code
            req.rec_num = mobile
            try:
              # resp = req.getResponse()
              # print type(resp)
              # print(resp)
              MobileCode[mobile] = {
                "lasttime": datetime.datetime.now(),
                "code": code
              }
              print MobileCode
            except Exception as e:
              print(e)

def checkSmsNum(mobile, smsnum):
    if isValid(mobile, 11) and isValid(smsnum, 6):
        info = MobileCode.get(mobile, None)
        if info != None and info.get("code", "") == smsnum:
            now = datetime.datetime.now()
            if now - info.get("lasttime") < 600:
              return True, ""
            return False, "outdate code"

    return False, "invalid args"
