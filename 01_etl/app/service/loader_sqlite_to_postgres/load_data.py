import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

from dataclasses_models import (  # isort:skip
    Genre,
    GenreFilmwork,
    Filmwork,
    Person,
    PersonFilmWork,
)
from postgres_saver import PostgresSaver  # isort:skip
from sqlite_loader import SQLiteLoader  # isort:skip

dataclass_dict = {
    'film_work': Filmwork,
    'genre': Genre,
    'genre_film_work': GenreFilmwork,
    'person': Person,
    'person_film_work': PersonFilmWork,
}


def load_from_sqlite(
    sqlite_conn: sqlite3.Connection,
    postgres_conn: _connection,
    size: 100,
):
    postgres_saver = PostgresSaver(postgres_conn)
    sqlite_loader = SQLiteLoader(sqlite_conn)

    for table in dataclass_dict.keys():
        tables_data = sqlite_loader.load_data(table, dataclass_dict, size)
        for table_data in tables_data:
            postgres_saver.save_data(table_data, table, size)


@contextmanager
def sqlite_connector(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn.cursor()
    finally:
        conn.close()


@contextmanager
def postgres_connector(dsl):
    conn = psycopg2.connect(**dsl, cursor_factory=DictCursor)
    try:
        yield conn
    finally:
        conn.close()


if __name__ == '__main__':
    SIZE = 500
    BASE_PATH = Path(__file__).resolve()
    ENV_PATH = BASE_PATH.parents[3].joinpath('env', '.env')
    load_dotenv(dotenv_path=ENV_PATH)
    SQLITE_PATH = BASE_PATH.parent.joinpath(
        os.getenv('SQLITE_PATH', default=None),
    )

    dsl = {
        'dbname': os.getenv('POSTGRES_DB', None),
        'user': os.getenv('POSTGRES_USER', None),
        'password': os.getenv('POSTGRES_PASSWORD', None),
        'host': os.getenv('DB_HOST', None),
        'port': os.getenv('DB_PORT', '5432'),
    }

    with sqlite_connector(
        SQLITE_PATH,
    ) as sqlite_conn, postgres_connector(
        dsl,
    ) as postgres_conn:
        load_from_sqlite(sqlite_conn, postgres_conn, SIZE)
