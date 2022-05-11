from typing import Generator, List

from elasticsearch import Elasticsearch, helpers

from pydantic_models import Film
from utils.backoff import backoff


class ElasticConnector(object):
    def __init__(self, elastic_dsl):
        self.elastic_dsl = elastic_dsl
        self.client = None

    @backoff
    def __enter__(self):
        self.client = Elasticsearch(**self.elastic_dsl)
        if not self.client.ping():
            raise ConnectionError('Elasticsearch ошибка соединения')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()


class ElasticsearchLoader(ElasticConnector):

    def generate_elastic_data(self, index, data: List[Film]) -> Generator:
        yield from (
            {
                'index': index,
                '_id': item.id,
                '_source': item.json(),
            }
            for item in data
        )

    def bulk_data_to_elastic(self, index, data: List[Film]) -> None:
        helpers.bulk(self.client, self.generate_elastic_data(index, data))
