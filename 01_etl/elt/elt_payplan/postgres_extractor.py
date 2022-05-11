import psycopg2
from psycopg2.extras import DictCursor

from utils.backoff import backoff


class PostgresConnector(object):
    def __init__(self, postgres_dsl):
        self.postgres_dsl = postgres_dsl
        self.connection = None
        self.cursor = None

    @backoff
    def __enter__(self):
        self.connection = psycopg2.connect(
            **self.postgres_dsl, cursor_factory=DictCursor,
        )
        self.cursor = self.connection.cursor()
        return self

    def query(self, sql):
        self.cursor.execute(sql)
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.commit()
        self.connection.close()


class PostgresExtractor(PostgresConnector):
    def get_ids_modified_table(self, table, state_date, limit):
        sql_template = """
            SELECT id modified
            FROM content.{table} WHERE modified >= '{state_date}'
            ORDER BY modified;
        """
        sql = self.cursor.mogrify(
            sql_template.format(table=table, state_date=state_date),
        )
        while True:
            loaded_data = self.query(sql).fetchmany(limit)
            if not loaded_data:
                break
            yield from (row for row in loaded_data)

    def get_person_data(self, persons_ids):
        sql_template = """
            SELECT
                p.id,
                full_name,
                pfw.role,
                pfw.film_work_id
            FROM content.person p
            LEFT JOIN content.person_film_work pfw ON pp.id = pfw.person_id
            WHERE p.id IN ({ids})
        """
        sql = self.cursor.mogrify(sql_template.format(ids=tuple(persons_ids)))
        return self.query(sql).fetchall()

    def get_genre_data(self, genre_ids):
        sql_template = """
            SELECT
                g.id,
                g.name,
                g.description,
                gfw.film_work_id
            FROM content.genre g
            LEFT JOIN content.genre_film_work gfw ON gg.id = gfw.genre_id
            WHERE g.id IN ({ids});
        """
        sql = self.cursor.mogrify(sql_template.format(ids=tuple(genre_ids)))
        return self.query(sql).fetchall()

    def get_data_from_elastic_movies(self, film_ids):
        sql_template = """
        SELECT
            fw.id as fw_id,
            fw.title,
            fw.description,
            fw.rating,
            fw.type,
            fw.created,
            fw.modified,
            pfw.role,
            pfw.id as pfw_id,
            p.id,
            p.full_name,
            g.name
        FROM content.film_work fw
        LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
        LEFT JOIN content.person p ON p.id = pfw.person_id
        LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
        LEFT JOIN content.genre g ON g.id = gfw.genre_id
        WHERE fw.id IN ({ids});
        """
        sql = self.cursor.mogrify(sql_template.format(ids=tuple(film_ids)))
        return self.query(sql).fetchall()

    def get_film_id_in_table(self, table, table_ids):
        sql_template = """
            SELECT
                fw.id
            FROM content.film_work fw
            LEFT JOIN content.{table}_film_work pfw ON pfw.film_work_id = fw.id
            WHERE pfw.{table}_id IN ({ids})
            ORDER BY fw.modified;
        """
        sql = self.cursor.mogrify(
            sql_template.format(table=table, ids=tuple(table_ids)),
        )
        return self.query(sql).fetchall()
