import click
from flask import g, current_app
from psycopg2 import pool

DATABASE_CONFIG = {
    'dbname': 'survey_service',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': 5432
}

connection_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    **DATABASE_CONFIG
)

def get_db_connection():
    if 'db_conn' not in g:
        g.db_conn = connection_pool.getconn()
    return g.db_conn

def close_db_connection(exception):
    db_conn = g.pop('db_conn', None)
    if db_conn:
        connection_pool.putconn(db_conn)

@click.command('init-db')
def init_db_command():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        with current_app.open_resource('path to init') as f:
            cursor.execute(f.read().decode('utf8'))
    conn.commit()
    click.echo('Initialized the database')