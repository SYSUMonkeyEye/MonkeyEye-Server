# *-* coding: utf-8 *-*
from flask_restplus import Api
from smscode import api as ns1
from session import api as ns2

api = Api(
    title='MonkeyEye',
    version='1.0',
    description='猿眼电影售票系统API',
    doc='/swagger/',
    catch_all_404s=True
)

api.add_namespace(ns1, path='/api/smscode')
api.add_namespace(ns2, path='/api/session')
