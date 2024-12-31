from flask import Flask, request, render_template

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
                surveys = cursor.fetchall()
                app.logger.info(surveys)

        return render_template('all_surveys.html', all_surveys=surveys)

    return app
