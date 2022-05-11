import os

from dotenv import load_dotenv

load_dotenv()

postgres_dsl = {
    'dbname': os.getenv('POSTGRES_DB', None),
    'user': os.getenv('POSTGRES_USER', None),
    'password': os.getenv('POSTGRES_PASSWORD', None),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'options': '-c search_path=content',
}

redis_dsl = {
    'host': os.getenv('REDIS_HOST', 'localhost'),
    'port': os.getenv('REDIS_PORT', '6379'),
}

elastic_dsl = {
    'hosts': [
        'http://{host}:{port}'.format(
            host=os.environ.get('ELASTIC_HOST', 'localhost'),
            port=os.environ.get('ELASTIC_PORT', '9200'),
        ),
    ],
    'http_auth': (
        os.environ.get('ELASTIC_USER', None),
        os.environ.get('ELASTIC_PASSWORD', None),
    ),
}
