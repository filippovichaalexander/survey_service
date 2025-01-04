import functools
from flask import render_template, request, redirect, url_for, flash, session
from sqlalchemy import func

from app.db2.pg import db_session

from .db2.models import User, Survey, Option, Vote, VoteOption

def init_app(app):
    def login_required(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            if session.get('loggedin') is None:
                return redirect(url_for('login'))

            return view(**kwargs)

        return wrapped_view

    @app.route('/', methods=['GET'])
    def all_surveys():
        if request.method == 'GET':
            all_surveys = db_session.query(Survey).all()
            return render_template('all_surveys.html', all_surveys=all_surveys)

    @app.route('/survey/<int:survey_id>', methods=['GET'])
    def get_survey(survey_id):
        user_id = session.get('id')
        user_voted = False
        survey = db_session.query(Survey).filter_by(id=survey_id).first()
        options = db_session.query(Option).filter_by(survey_id=survey_id).all()
        if user_id:
            user_voted = db_session.query(Vote).filter_by(survey_id=survey_id, user_id=user_id).count() > 0
        else:
            voter_ip = request.remote_addr
            user_voted = db_session.query(Vote).filter_by(survey_id=survey_id, voter_ip=voter_ip).count() > 0
        return render_template('survey.html', survey=survey, options=options, is_voted=user_voted)

    @app.route('/delete-survey/<int:survey_id>', methods=['POST'])
    @login_required
    def delete_survey(survey_id):
        print(f'Deleting survey with id: {survey_id}')
        survey = db_session.get(Survey, survey_id)
        if survey:
            db_session.delete(survey)
            db_session.commit()
            flash('Survey deleted successfully!')
        else:
            flash('Survey not found!')
        db_session.rollback()
        db_session.close()
        return redirect(url_for('all_surveys'))


    @app.route('/survey/<int:survey_id>/votes', methods=['GET'])
    def get_votes_for_survey(survey_id):
        survey = db_session.query(Survey).filter_by(id=survey_id).first()
        votes = db_session.query(Option.option_text, func.count(VoteOption.id).label('vote_count')) \
            .join(VoteOption, Option.id == VoteOption.option_id) \
            .join(Vote, VoteOption.vote_id == Vote.id) \
            .filter(Vote.survey_id == survey_id) \
            .group_by(Option.option_text) \
            .all()
        return render_template('votes.html', survey=survey, votes=votes)


    @app.route('/submit_vote', methods=['POST'])
    def submit_vote():
        survey_id = request.form['survey_id']
        user_id = session.get('id')  # user_id is optional
        voter_ip = request.remote_addr
        option_id = request.form.get('option')
        option_ids = [option_id] if option_id else request.form.getlist('options')

        if not option_ids:
            flash('Please select an option to vote.')
            return redirect(url_for('get_survey', survey_id=survey_id))
        if user_id:
            vote = Vote(survey_id=survey_id, user_id=user_id)
        else:
            vote = Vote(survey_id=survey_id, voter_ip=voter_ip)
        db_session.add(vote)
        db_session.flush()  # Ensure the vote.id is generated before using it
        for option_id in option_ids:
            vote_option = VoteOption(vote_id=vote.id, option_id=option_id)
            db_session.add(vote_option)
        db_session.commit()

        flash('Vote cast successfully!')
        return redirect(url_for('get_survey', survey_id=survey_id))

    @app.route('/create-survey', methods=['GET', 'POST'])
    @login_required
    def create_survey():
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            is_single_choice = request.form.get('is_single_choice', False)
            created_by = session.get('id')
            survey = Survey(title=title, description=description, created_by=created_by,
                            is_single_choice=bool(is_single_choice))
            db_session.add(survey)
            db_session.commit()
            flash('Survey created successfully! Add options')
            return redirect(url_for('add_option', survey_id=survey.id))
        return render_template('create_survey.html')

    @app.route('/add-option/<int:survey_id>', methods=['GET', 'POST'])
    def add_option(survey_id):
        if request.method == 'POST':
            option_text = request.form['option_text']
            option = Option(survey_id=survey_id, option_text=option_text)
            db_session.add(option)
            db_session.commit()
            flash('Option added successfully!')
            return redirect(url_for('add_option', survey_id=survey_id))

        options = db_session.query(Option).filter_by(survey_id=survey_id).all()
        return render_template('add_option.html', survey_id=survey_id, options=options)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            password_hash = request.form['password_hash']
            user = User(username=username, password_hash=password_hash)
            db_session.add(user)
            db_session.commit()
            flash('User registered successfully!')
            return redirect(url_for('login'))
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        msg = ''
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = db_session.query(User).filter_by(username=username, password_hash=password).first()
            if user:
                session['loggedin'] = True
                session['id'] = user.id
                session['username'] = user.username
                return redirect(url_for('all_surveys'))
            else:
                msg = 'Incorrect username / password!'
        return render_template('login.html', msg=msg)

    @app.route('/logout')
    def logout():
        session.pop('loggedin', None)
        session.pop('id', None)
        session.pop('username', None)
        return redirect(url_for('login'))