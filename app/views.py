import functools

from flask import Flask, request, render_template, flash, url_for, session

from werkzeug.utils import redirect

from .db.ps import get_db_connection
from .db.queries import (
    ALL_SURVEYS,
    CREATE_USER,
    GET_USER_BY_USERNAME_AND_PASSWORD,
    CREATE_SURVEY,
    CREATE_OPTION,
    GET_OPTIONS_FOR_SURVEY,
    CHECK_USER_VOTED,
    CHECK_ANONYMOUS_USER_VOTED,
    GET_SURVEY,
    GET_VOTES_FOR_SURVEY,
    CREATE_VOTE,
    CREATE_VOTE_OPTIONS,
    DELETE_SURVEY,
)
import logging

from sqlalchemy import func


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

    @app.route('/survey/<int:survey_id>', methods=['GET'])
    def get_survey(survey_id):
        user_id = session.get('id')
        user_voted = False
        conn = get_db_connection()
        with conn.cursor() as cursor:
            if user_id:
                cursor.execute(CHECK_USER_VOTED, (survey_id, user_id))
                user_voted = bool(cursor.fetchone())
                cursor.execute(CHECK_USER_VOTED, (survey_id, user_id))

            else:
                # Check for anonymous user by IP address
                user_ip = request.remote_addr
                cursor.execute(CHECK_ANONYMOUS_USER_VOTED, (survey_id, user_ip))
                user_voted = bool(cursor.fetchone())

            cursor.execute(GET_SURVEY, (survey_id,))
            survey = cursor.fetchone()
            cursor.execute(GET_OPTIONS_FOR_SURVEY, (survey_id,))
            options = cursor.fetchall()

        return render_template('survey.html', survey=survey, options=options, is_voted=user_voted)

    @app.route('/survey/<int:survey_id>/votes', methods=['GET'])
    def get_votes_for_survey(survey_id):
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(GET_VOTES_FOR_SURVEY, (survey_id,))
            votes = cursor.fetchall()
            cursor.execute(GET_SURVEY, (survey_id,))
            survey = cursor.fetchone()
        return render_template('votes.html', votes=votes, survey=survey)

    @app.route('/submit_vote', methods=['POST'])
    def submit_vote():
        survey_id = request.form['survey_id']
        user_id = session.get('id')  # user_id is optional
        voter_ip = request.remote_addr
        option_id = request.form.get('option')
        option_ids = [option_id] if option_id else request.form.getlist('options')

        if not option_ids:
            flash('Please select option to vote.')
            return redirect(url_for('get_survey', survey_id=survey_id))

        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(CREATE_VOTE, (survey_id, user_id, voter_ip))
            vote_id = cursor.fetchone()[0]
            for option_id in option_ids:
                cursor.execute(CREATE_VOTE_OPTIONS, (vote_id, option_id))
            conn.commit()

        flash('Vote cast successfully!')
        return redirect(url_for('get_survey', survey_id=survey_id))

    @app.route('/delete-survey/<int:survey_id>', methods=['POST'])
    @login_required
    def delete_survey(survey_id):
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(DELETE_SURVEY, (survey_id,))
            conn.commit()
        flash('Survey deleted successfully!')
        return redirect(url_for('all_surveys'))

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
