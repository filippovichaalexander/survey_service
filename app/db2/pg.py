import click
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError


engine = create_engine('postgresql://postgres:postgres@localhost:5432/survey_service')
db_session = scoped_session(sessionmaker(bind=engine))


Base = declarative_base()
Base.query = db_session.query_property()

def close_db_connection(exception=None):
    db_session.remove()


@click.command('init-db')
def init_db_command():
    try:
        import app.db2.models
        Base.metadata.create_all(bind=engine)
        click.echo('Initialized the database.')
    except SQLAlchemyError as e:
        click.echo(f'Error initializing the database: {e}')


def init_app(app):
    app.teardown_appcontext(close_db_connection)
    app.cli.add_command(init_db_command)