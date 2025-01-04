from flask import Flask

def create_app():
    app = Flask(__name__)

    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    # from .db import ps as ps_dn
    # ps_dn.init_app(app)

    from .db2 import pg as pg_dn
    pg_dn.init_app(app)

    # from .views import init_views
    # init_views(app)

    from .views2 import init_app
    init_app(app)

    return app

# export FLASK_APP=app.app
# flask run
# flask run --debug

# 1.53.31 - set time

#
# @app.route("/")
# def hello_world():
#     return "<p>Hello, World2s4</p>"