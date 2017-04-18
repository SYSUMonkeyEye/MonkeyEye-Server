# -*- coding: utf-8 -*-
import sys
import random
import top.api
import app.utils as utils
from datetime import datetime
from app.utils import mobile_code
from flask import Blueprint, request, jsonify, current_app

reload(sys)
sys.setdefaultencoding('utf-8')  # 解决短信解码问题

smscode = Blueprint('smscode', __name__)


@smscode.route('/api/smscode')
def getSmsNum():
    mobile = request.args.get('mobile', '')
    if utils.isValid(mobile, 11):
        info = mobile_code.get(mobile, None)
        now = datetime.now()

        # 90秒可请求一次短信验证码
        if info == None or (now - info.get('lasttime')).seconds > 90:
            req = top.api.AlibabaAliqinFcSmsNumSendRequest()
            APPKEY = current_app.config['APPKEY']
            APPSECRET = current_app.config['APPSECRET']
            req.set_app_info(top.appinfo(APPKEY, APPSECRET))
            req.extend = '123456'
            req.sms_type = 'normal'
            req.sms_free_sign_name = '猿眼电影'
            req.sms_template_code = 'SMS_62200286'
            code = random.randint(100000, 999999)
            req.sms_param = '{"code":"%d"}' % code
            req.rec_num = mobile
            try:
                res = req.getResponse()['alibaba_aliqin_fc_sms_num_send_response']['result']
                if res['success']:
                    mobile_code.update({
                        mobile: dict(lasttime=datetime.now(), code=code)
                    })
                    return jsonify(dict(status=200, msg=code))

                return jsonify(dict(status=400, msg=res['err_code']))

            except Exception as e:
                print(e)
                return jsonify(dict(status=500, msg=str(e)))

        return jsonify(dict(status=429, msg='Too Many Requests'))

    return jsonify(dict(status=400, msg='Invalid Mobile'))