import abc
import json
from pathlib import Path
from typing import Any, Optional

from redis import Redis

from backoff import backoff  # isort: skip


class BaseStorage(object):
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище."""

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища."""


class JsonFileStorage(BaseStorage):
    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path
        Path(self.file_path).touch(exist_ok=True)

    def save_state(self, state: dict) -> None:
        old_state = self.retrieve_state()
        new_state = {**old_state, **state}
        with open(self.file_path, 'w') as write_file:
            write_file.write(json.dumps(new_state))

    def retrieve_state(self) -> dict:
        with open(self.file_path, 'r') as read_file:
            readed_data = read_file.read()
            if not readed_data:
                return {}
        return json.loads(readed_data)


class State(object):
    """
    Класс для хранения состояния при работе с данными.

    Чтобы постоянно не перечитывать данные с начала.
    Здесь представлена реализация с сохранением состояния в файл.
    В целом ничего не мешает поменять это поведение на работу с БД или
    распределённым хранилищем.
    """

    def __init__(self, storage: BaseStorage):
        self.storage = storage

    def set_state(self, key: str, state: Any) -> None:
        """Установить состояние для определённого ключа."""
        self.storage.save_state({key: state})

    def get_state(self, key: str) -> Any:
        """Получить состояние по определённому ключу."""
        state = self.storage.retrieve_state()
        if key not in state.keys():
            return None
        state_object = state[key]
        if isinstance(state_object, 'bytes'):
            return state_object.decode('utf8')
        return state_object


class RedisStorage(BaseStorage):
    def __init__(self, redis_adapter: Redis, redis_dsl: [dict, None] = None):
        self.redis_adapter = redis_adapter
        self.redis_dsl = redis_dsl
        self.redis_conn = None

    @backoff
    def connect(self) -> None:
        if self.redis_dsl is None:
            self.redis_conn = self.redis_adapter()
        self.redis_conn = self.redis_adapter(**self.redis_dsl)

    def retrieve_state(self) -> dict:
        if not self.redis_conn.ping():
            self.connect()
        return self.redis_conn

    def save_state(self, state: dict) -> None:
        if not self.redis_conn.ping():
            self.connect()
        self.redis_conn.mset(state)

    def __del__(self):
        if self.redis_conn:
            self.redis_conn.close()
