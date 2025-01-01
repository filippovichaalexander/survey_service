import functools

from flask import Flask, request, render_template, flash, url_for, session

from werkzeug.utils import redirect

from .db.ps import get_db_connection
from .db.queries import ALL_SURVEYS, CREATE_USER, GET_USER_BY_USERNAME_AND_PASSWORD, CREATE_SURVEY, CREATE_OPTION, GET_OPTIONS_FOR_SURVEY
import logging

def init_views(app):
    @app.route('/hello')
    def hello():
        app.logger.info('Hello works!!!!!')
        return 'Hello works!!!!!!'


    def login_required(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            if session.get('loggedin') is None:
                return redirect(url_for('login'))

            return view(**kwargs)

        return wrapped_view

    @app.route('/create-survey', methods=['GET', 'POST'])
    @login_required
    def create_survey():
        if request.method == 'POST':
            title = request.form.get('title')
            description = request.form.get('description')
            is_single_choice = request.form.get('is_single_choice', False)
            created_by = session.get('id')
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute(CREATE_SURVEY, (title, description, created_by, is_single_choice))
                result = cursor.fetchone()
                conn.commit()
            flash('Survey created successfully! Add options')
            return redirect(url_for('add_option', survey_id=result[0]))
        return render_template('create_survey.html')

    @app.route('/add-option/<int:survey_id>', methods=['GET', 'POST'])
    def add_option(survey_id):
        if request.method == 'POST':
            option_text = request.form.get('option_text')
            survey_id = request.form.get('survey_id')
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute(CREATE_OPTION, (survey_id, option_text))
                conn.commit()
            flash('Option added successfully!')
            return redirect(url_for('add_option', survey_id=survey_id))

        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(GET_OPTIONS_FOR_SURVEY, (survey_id,))
            options = cursor.fetchall()

        return render_template('add_option.html', survey_id=survey_id, options=options)

    @app.route('/')
    def all_surveys():
        if request.method == 'GET':
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute(ALL_SURVEYS)
                surveys = cursor.fetchall()
                app.logger.info(surveys)

        return render_template('all_surveys.html', all_surveys=surveys)

    # ##### Registration #####
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            user_name = request.form.get('username')
            password_hash = request.form.get('password_hash')
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute(CREATE_USER, (user_name, password_hash))
                conn.commit()
            flash('User created succesfully!')
            return redirect(url_for('login'))
        return render_template('registration.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            user_name = request.form.get('username')
            password_hash = request.form.get('password')
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute(GET_USER_BY_USERNAME_AND_PASSWORD, (user_name, password_hash))
                account = cursor.fetchone()
                if account:
                    session['id'] = account[0]
                    session['username'] = account[1]
                    session['loggedin'] = True
                    return redirect(url_for('all_surveys'))
                else:
                    flash('Incorrect username or password')
        return render_template('login.html')

    @app.route('/logout', methods=['GET'])
    def logout():
        if request.method == 'GET':
            # session.clear()
            session.pop('loggedin', None)
            session.pop('id', None)
            session.pop('username', None)
            return redirect(url_for('login'))


    return app
