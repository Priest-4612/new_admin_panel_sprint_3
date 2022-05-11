import os
import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import DictCursor

sys.path.append(os.path.join(sys.path[0], '../../03_sqlite_to_postgres'))
from load_data import conn_context

ENV_PATH = Path(__file__).resolve().parent.parent.parent.joinpath('env', '.env')
load_dotenv(dotenv_path=ENV_PATH)

SQLITE_PATH = os.getenv('SQLITE_PATH', default=None)
dsl = {
    'dbname': os.getenv('POSTGRES_DB', None),
    'user': os.getenv('POSTGRES_USER', None),
    'password': os.getenv('POSTGRES_PASSWORD', None),
    'host': os.getenv('DB_HOST', None),
    'port': os.getenv('DB_PORT', '5432'),
}

tables = [
    'film_work',
    'person',
    'genre',
    'person_film_work',
    'genre_film_work',
]


def sqlite_query(query):
    with conn_context(SQLITE_PATH) as sqlite_conn:
        sqlite_conn.execute(query)
        return sqlite_conn.fetchall()


def postgres_query(query):
    with psycopg2.connect(**dsl) as pg_conn:
        cur = pg_conn.cursor()
        cur.execute(query)
        return cur.fetchall()


def test_equal_count_data():

    counts = {}

    for table in tables:
        query = "SELECT COUNT(*) FROM {table};".format(table=table)

        counts.update({table: {
            'postgres': postgres_query(query)[0][0],
            'sqlite': sqlite_query(query)[0][0]}
        })

    assert counts['genre']['postgres'] == counts['genre']['sqlite']
    assert counts['film_work']['postgres'] == counts['film_work']['sqlite']
    assert counts['genre_film_work']['postgres'] == counts['genre_film_work']['sqlite']
    assert counts['person']['postgres'] == counts['person']['sqlite']
    assert counts['person_film_work']['postgres'] == counts['person_film_work']['sqlite']


def test_equal_content():

    content = {}

    for table in tables:

        if table == 'film_work':
            query = 'SELECT title, description, creation_date, type, rating FROM film_work;'

        if table == 'person':
            query = 'SELECT full_name FROM person;'

        if table == 'genre':
            query = 'SELECT name, description FROM genre;'

        if table == 'genre_film_work':
            query = 'SELECT film_work_id, genre_id FROM genre_film_work;'

        if table == 'person_film_work':
            query = 'SELECT role, film_work_id, person_id FROM person_film_work;'

        content.update({table: {
            'postgres': postgres_query(query),
            'sqlite': sqlite_query(query)},
        })

    assert len(set(content['film_work']['sqlite']) - set(content['film_work']['postgres'])) == 0
    assert len(set(content['genre']['sqlite']) - set(content['genre']['postgres'])) == 0
    assert len(set(content['person']['sqlite']) - set(content['person']['postgres'])) == 0
    assert len(set(content['genre_film_work']['sqlite']) -
               set(content['genre_film_work']['postgres'])) == 0
    assert len(set(content['person_film_work']['sqlite']) -
               set(content['person_film_work']['postgres'])) == 0


if __name__ == "__main__":
    test_equal_count_data()
    test_equal_content()
