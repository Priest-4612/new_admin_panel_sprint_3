from collections import defaultdict
from enum import Enum

from pydantic_models import (  # isort: skip
    FilmElastick,
    Genre,
    GenreElastic,
    GenreRaw,
    Person,
    PersonElastic,
    PersonRaw,
    RawMovies,
)


class PersonRole(Enum):
    ACTOR = 'actor'
    WRITER = 'producer'
    DIRECTOR = 'director'


class DataTransform(object):
    def add_role_person(self, role, data, film):
        mapping_person = {
            PersonRole.ACTOR.value: {
                'names': data.actors_names,
                'obj': data.actors,
            },
            PersonRole.WRITER.value: {
                'names': data.writers_names,
                'obj': data.writers,
            },
            PersonRole.DIRECTOR.value: {
                'names': data.directors_names,
                'obj': data.directors,
            },
        }
        person = Person(**film)
        data_mapping = mapping_person.get(role, None)
        if data_mapping:
            if person.name not in data_mapping['names']:
                data_mapping['names'].add(person.name)
                data_mapping['obj'].append(person)

    def transform_film(self, films_raw):
        result = defaultdict(dict)
        for film in films_raw:
            mv = RawMovies(**film)
            id = mv.fw_id
            data = result[id]
            if not data:
                data = FilmElastick(**mv.dict())

            genre_name = mv.genre_name
            if genre_name and genre_name not in data.genres_names:
                genre = Genre(id=mv.genre_id, name=genre_name)
                data.genres_names.append(genre_name)
                data.genres.append(genre)

            if mv.role:
                self.add_role_person(mv.role, data, film)

            result[id] = data
        return result

    def transform_persons(self, get_data):
        result = defaultdict(dict)
        for person in get_data:
            p_raw = PersonRaw(**person)
            id = p_raw.id
            data = result[id]
            if not data:
                data = PersonElastic(**p_raw.dict())
            data.role.add(p_raw.role_raw)
            data.film_ids.add(p_raw.film_work_id)
            result[id] = data
        return result

    def transform_genres(self, get_data):
        result = defaultdict(dict)
        for genre in get_data:
            genre_raw = GenreRaw(**genre)
            id = genre_raw.id
            data = result[id]
            if not data:
                data = GenreElastic(**genre_raw.dict())
            data.description = genre_raw.description
            data.film_ids.add(genre_raw.film_work_id)
            result[id] = data
        return result
