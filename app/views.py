from flask import Flask, request

from .db.ps import get_db_connection
from .db.queries import ALL_SURVEYS
import logging

def init_views(app):
    @app.route('/hello')
    def hello():
        app.logger.info('Hello works!!!!!')
        return 'Hello works!!!!!!'

    @app.route('/')
    def all_surveys():
        if request.method == 'GET':
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute(ALL_SURVEYS)
                all_list_surveys = cursor.fetchall()
                app.logger.info(all_list_surveys)

        return 'All surveys are here'

    return app
