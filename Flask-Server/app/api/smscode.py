# -*- coding: utf-8 -*-
import sys
import random
import top.api
from app.utils import isValid
from datetime import datetime
from app.utils import mobile_code
from flask import request, current_app
from flask_restplus import Resource, Namespace

reload(sys)
sys.setdefaultencoding('utf-8')  # 解决短信解码问题
api = Namespace('smscode', description='短信验证码模块')


@api.route('/')
class SmsCode(Resource):
    @api.doc(parser=api.parser().add_argument('mobile', type=str, required=True, help='手机号码', location='args'))
    def get(self):
        """获取短信验证码"""
        mobile = request.args.get('mobile', '')
        if not isValid(mobile, 11):
            return {'message': 'Invalid Mobile'}, 400

        info = mobile_code.get(mobile, None)
        now = datetime.now()

        # 90秒可请求一次短信验证码
        if info is not None and (now - info.get('lasttime')).seconds < 90:
            return {'message': 'Too Many Requests'}, 429

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
            # res = req.getResponse()['alibaba_aliqin_fc_sms_num_send_response']['result']
            # if res['success']:
            if 1:
                mobile_code.update({
                    mobile: dict(lasttime=datetime.now(), code=code)
                })
                return {'message': code}, 200

            return {'message': res['err_code']}, 400

        except Exception as e:
            print(e)
            return {'message': str(e)}, 500


