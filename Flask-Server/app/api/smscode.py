# -*- coding: utf-8 -*-
import sys
import random
import top.api
from flask import request
from datetime import timedelta
from app.utils import isValid, myRedis
from instance.config import APPKEY, APPSECRET
from flask_restplus import Resource, Namespace

reload(sys)
sys.setdefaultencoding('utf-8')  # 解决短信解码问题
ten_minutes = timedelta(minutes=10)
api = Namespace('smscode', description='验证码模块')


@api.route('/')
class SmsCode(Resource):
    @api.doc(parser=api.parser().add_argument(
        'mobile', type=str, required=True, help='手机号码', location='args')
    )
    def get(self):
        """获取短信验证码"""
        mobile = request.args.get('mobile', '')
        if not isValid(mobile, 11):
            return {'message': '手机号码非法'}, 233

        name = 'smscode:%s' % mobile
        code = myRedis.get(name)

        # 60秒可请求一次短信验证码
        if code is not None and myRedis.ttl(name) > 540:
            return {'message': '频繁请求'}, 233

        req = top.api.AlibabaAliqinFcSmsNumSendRequest()
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
                myRedis.setex(name, code, ten_minutes)
                return {'message': code}, 200

            return {'message': res['err_code']}, 233

        except Exception as e:
            print(e)
            return {'message': str(e)}, 500
