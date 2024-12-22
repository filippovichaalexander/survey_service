from flask import Flask

def create_app():
    app = Flask(__name__)

    @app.route('/hello')
    def hello():
        return 'Hello works!!!!!!'

    return app

# export FLASK_APP=app.app
# flask run
# flask run --debug

# 1.28.50 - set time

#
# @app.route("/")
# def hello_world():
#     return "<p>Hello, World2s4</p>"