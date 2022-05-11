import uuid
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path


@dataclass(frozen=True)
class Genre(object):
    name: str
    description: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=datetime.today)
    updated_at: datetime = field(default_factory=datetime.today)


@dataclass
class Filmwork(object):
    title: str
    description: str
    type: str
    file_path: Path
    rating: float = field(default=0)
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    creation_date: date = field(default_factory=date.today)
    created_at: datetime = field(default_factory=datetime.today)
    updated_at: datetime = field(default_factory=datetime.today)

    def __post_init__(self):
        if self.creation_date is None:
            self.creation_date = datetime.today()


@dataclass(frozen=True)
class Person(object):
    full_name: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=datetime.today)
    updated_at: datetime = field(default_factory=datetime.today)


@dataclass(frozen=True)
class GenreFilmwork(object):
    genre_id: uuid.UUID
    film_work_id: uuid.UUID
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=datetime.today)


@dataclass(frozen=True)
class PersonFilmWork(object):
    person_id: uuid.UUID
    film_work_id: uuid.UUID
    role: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=datetime.today)
