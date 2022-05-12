from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseConfig, BaseSettings, Field

ENV_PATH = Path(__file__).resolve().parents[1].joinpath('env', '.env')
load_dotenv(dotenv_path=ENV_PATH)


class PostgresDSL(BaseSettings):
    dbname: str
    user: str
    password: str
    host: str
    port: str
    options: str = Field('-c search_path=content')

    class Config(BaseConfig):
        fields = {
            'dbname': {'env': 'POSTGRES_DB'},
            'user': {'env': 'POSTGRES_USER'},
            'password': {'env': 'POSTGRES_PASSWORD'},
            'host': {'env': 'DB_HOST'},
            'port': {'env': 'DB_PORT'},
        }


class RedisDSL(BaseSettings):
    hosts: str
    port: str

    class Config(BaseConfig):
        fields = {
            'hosts': {'env': 'REDIS_HOST'},
            'port': {'env': 'REDIS_PORT'},
        }


class ElasticDSL(BaseSettings):
    host: str
    port: str

    class Config(BaseConfig):
        fields = {
            'host': {'env': 'ELASTIC_HOST'},
            'port': {'env': 'ELASTIC_PORT'},
        }


class Settings(BaseSettings):
    postgres_dsl: PostgresDSL = PostgresDSL()
    redis_dsl: RedisDSL = RedisDSL()
    elastic_dsl: ElasticDSL = ElasticDSL()

    class Config(BaseConfig):
        env_file = ENV_PATH.as_posix()
        env_file_encoding = 'utf-8'
