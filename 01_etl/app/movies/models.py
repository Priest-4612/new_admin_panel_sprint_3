from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from movies.mixin_models import CreatedMixin, TimeStampedMixin, UUIDMixin

CONSTRAINT_RATING_MIN = 0
CONSTRAINT_RATING_MAX = 10.0

template_tablename = 'content\".\"{tablename}'


class Type(models.TextChoices):
    MOVIE = _('movie')
    TV_SHOW = _('tv_show')


class Role(models.TextChoices):
    ACTOR = _('actor')
    DIRECTOR = _('director')
    PRODUCER = _('producer')
    WRITER = _('writer')


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.TextField(
        verbose_name=_('name'),
    )
    description = models.TextField(
        verbose_name=_('description'),
        blank=True,
        null=True,
    )

    class Meta(object):
        db_table = template_tablename.format(tablename='genre')
        verbose_name = _('genre')
        verbose_name_plural = _('genres')
        constraints = [
            models.UniqueConstraint(
                name='uneque_genre_name_idx',
                fields=('name',),
            ),
        ]

    def __str__(self):
        return self.name


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.TextField(
        verbose_name=_('full name'),
    )

    class Meta(object):
        db_table = template_tablename.format(tablename='person')
        verbose_name = _('person')
        verbose_name_plural = _('persons')

    def __str__(self):
        return self.full_name


class Filmwork(UUIDMixin, TimeStampedMixin):
    title = models.TextField(
        verbose_name=_('title'),
    )
    description = models.TextField(
        verbose_name=_('description'),
        blank=True,
        null=True,
    )
    creation_date = models.DateField(
        verbose_name=_('creation date'),
        blank=True,
        null=True,
    )
    rating = models.FloatField(
        verbose_name=_('rating'),
        blank=True,
        null=True,
        validators=[
            MinValueValidator(CONSTRAINT_RATING_MIN),
            MaxValueValidator(CONSTRAINT_RATING_MAX),
        ],
    )
    type = models.TextField(
        verbose_name=_('type'),
        choices=Type.choices,
        default=Type.MOVIE,
    )
    genres = models.ManyToManyField(
        to=Genre,
        verbose_name=_('genres'),
        through='FilmworkGenre',
        related_name='filmworks',
    )
    persons = models.ManyToManyField(
        to=Person,
        verbose_name=_('persons'),
        through='FilmworkPerson',
        related_name='filmworks',
    )
    file_path = models.FileField(
        verbose_name=_('file'),
        blank=True,
        null=True,
        upload_to='data/movies/',
    )

    class Meta(object):
        db_table = template_tablename.format(tablename='film_work')
        verbose_name = _('movie')
        verbose_name_plural = _('movies')
        indexes = [
            models.Index(
                fields=('creation_date',),
                name='film_work_creation_date_idx',
            ),
            models.Index(
                fields=('title',),
                name='film_work_title_idx',
            ),
            models.Index(
                fields=('type',),
                name='film_work_type_idx',
            ),
        ]

    def __str__(self):
        return self.title


class FilmworkGenre(UUIDMixin, CreatedMixin):
    genre = models.ForeignKey(
        to=Genre,
        verbose_name=_('genre'),
        db_column='genre_id',
        on_delete=models.CASCADE,
        related_name='film_work_genres',
    )
    film_work = models.ForeignKey(
        to=Filmwork,
        verbose_name=_('film_work'),
        db_column='film_work_id',
        on_delete=models.CASCADE,
        related_name='film_work_genres',
    )

    class Meta(object):
        db_table = template_tablename.format(tablename='genre_film_work')
        verbose_name = _('filmwork genre')
        verbose_name_plural = _('filmwork genres')
        constraints = [
            models.UniqueConstraint(
                name='unique_film_work_genre',
                fields=('film_work', 'genre'),
            ),
        ]

    def __str__(self):
        return 'Genre: {genre} in film_work: {film_work}'.format(
            genre=self.genre,
            film_work=self.film_work,
        )


class FilmworkPerson(UUIDMixin, CreatedMixin):
    film_work = models.ForeignKey(
        verbose_name=_('film_work'),
        to='Filmwork',
        db_column='film_work_id',
        on_delete=models.CASCADE,
        related_name='film_work_persons',
    )
    person = models.ForeignKey(
        verbose_name=_('person'),
        to='Person',
        db_column='person_id',
        on_delete=models.CASCADE,
        related_name='film_work_persons',
    )
    role = models.TextField(
        verbose_name=_('role'),
        choices=Role.choices,
        default=Role.ACTOR,
    )

    class Meta(object):
        db_table = template_tablename.format(tablename='person_film_work')
        verbose_name = _('film_work person')
        verbose_name_plural = _('film_work persons')
        constraints = [
            models.UniqueConstraint(
                fields=('film_work', 'person', 'role'),
                name='unique_film_work_person_role_idx',
            ),
        ]
        indexes = [
            models.Index(
                fields=('film_work', 'person'),
                name='film_work_person_idx',
            ),
        ]

    def __str__(self):
        return '{role}: {person} in film_work: {film_work}'.format(
            person=self.person,
            film_work=self.film_work,
            role=self.role,
        )
