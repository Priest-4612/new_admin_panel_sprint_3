import datetime
import json
import logging
from pathlib import Path

from redis import Redis

from config import elastic_dsl, postgres_dsl, redis_dsl
from elt_payplan.data_transformer import DataTransform
from elt_payplan.elasticsearch_loader import ElasticsearchLoader
from elt_payplan.postgres_extractor import PostgresExtractor
from utils.state import RedisStorage, State


def loader_es(
    state: State,
    pg_conn: PostgresExtractor,
    table: dict,
    es_conn: ElasticsearchLoader,
):
    table_name = table['name']
    limit = 100
    state_table = json.loads(state.get_state(table_name))

    state_date = state_table.get('date', datetime.datetime.min.isoformat())
    date_end = state_date

    generator_modified_ids = pg_conn.get_ids_modified_table(
        table_name, state_date, limit,
    )
    for modified_ids in generator_modified_ids:
        date_end = datetime.now().isoformat()
        if table.get('func_film_id', None):
            film_modified_ids = pg_conn.get_film_id_in_table(
                table=table_name,
                table_ids=[item['id'] for item in modified_ids],
            )
        else:
            film_modified_ids = modified_ids

        transform_personal_index = table.get('transform_personal_index', None)
        if transform_personal_index:
            get_data = transform_personal_index['get_data'](
                [item['id'] for item in modified_ids],
            )
            serialize_data_index = transform_personal_index['func_transform'](
                get_data,
            )
            es_conn.set_bulk(
                transform_personal_index['index_name'],
                serialize_data_index.values(),
            )

        film_result = pg_conn.get_film_data(
            [item['id'] for item in film_modified_ids],
        )
        if film_result:
            film_serialize = DataTransform.transform_film(film_result)
            es_conn.bulk_data_to_elastic('movies', film_serialize.values())
        state.set_state(table['name'], json.dumps({'date': state_date}))

    state.set_state(table['name'], json.dumps({'offset': 0, 'date': date_end}))


if __name__ == '__main__':
    BASE_PATH = Path(__file__).resolve()
    PATH_TO_LOG = BASE_PATH.parents[3].joinpath('logs', 'backoff')

    _log_format = (
        '%(asctime)s - [%(levelname)s] -  %(name)s - ',
        '(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s',
    )

    logging.basicConfig(
        level=logging.DEBUG,
        format=_log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                filename=PATH_TO_LOG, mode='a', encoding='utf8',
            ),
        ])

    try:
        state = State(RedisStorage(redis_adapter=Redis(), redis_dsl=redis_dsl))
        with PostgresExtractor(
            postgres_dsl,
        ) as pg_conn, ElasticsearchLoader(
            elastic_dsl,
        ) as es_conn:
            transform_index = {
                'persons': {
                    'func_transform': DataTransform.transform_persons,
                    'get_data': pg_conn.get_person_data,
                    'index_name': 'persons',
                },
                'genres': {
                    'func_transform': DataTransform.transform_genres,
                    'get_data': pg_conn.get_genre_data,
                    'index_name': 'genres',
                },
            }
            tables_pg = [
                {
                    'name': 'genre',
                    'func_film_id': True,
                    'transform_genre_index': transform_index.get(
                        'genres', None,
                    ),
                },
                {
                    'name': 'person',
                    'func_film_id': True,
                    'transform_personal_index': transform_index.get(
                        'persons', None,
                    ),
                },
                {
                    'name': 'film_work',
                },
            ]
            for table in tables_pg:
                loader_es(state, pg_conn, table, es_conn)
    except Exception as exception:
        logging.error(exception)
