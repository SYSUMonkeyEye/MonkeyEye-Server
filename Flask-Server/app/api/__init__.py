# *-* coding: utf-8 *-*
from flask_restplus import Api
from smscode import api as ns1
from user import api as ns2
from session import api as ns3

api = Api(
    title='MonkeyEye',
    version='1.0',
    description='猿眼电影订票系统API',
    doc='/swagger/',
    catch_all_404s=True,
    serve_challenge_on_401=True
)

api.add_namespace(ns1, path='/api/smscode')
api.add_namespace(ns2, path='/api/users')
api.add_namespace(ns3, path='/api/session')
