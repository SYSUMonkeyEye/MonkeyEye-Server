# *-* coding: utf-8 *-*
from flask_restplus import Api
from user import api as ns1
from movie import api as ns2
from screen import api as ns3
from order import api as ns4
from session import api as ns5
from smscode import api as ns6
from password import api as ns7

api = Api(
    title='MonkeyEye',
    version='1.0',
    description='猿眼电影订票系统API',
    doc='/swagger/',
    catch_all_404s=True,
    serve_challenge_on_401=True
)

api.add_namespace(ns1, path='/api/users')
api.add_namespace(ns2, path='/api/movies')
api.add_namespace(ns3, path='/api/screens')
api.add_namespace(ns4, path='/api/orders')
api.add_namespace(ns5, path='/api/session')
api.add_namespace(ns6, path='/api/smscode')
api.add_namespace(ns7, path='/api/password')