"""Объявление admin моделей приложения фильмы."""
from django.contrib import admin

from movies import models


@admin.register(models.Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created', 'modified']
    list_display_links = ['name']
    list_filter = ['name']
    search_fields = ['name']


@admin.register(models.Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'created', 'modified']
    list_display_links = ['full_name']
    list_filter = ['full_name']
    search_fields = ['full_name']


class FilmworkGenreInline(admin.TabularInline):
    model = models.FilmworkGenre


class FilmworkPersonInline(admin.TabularInline):
    model = models.FilmworkPerson
    autocomplete_fields = ['person']


@admin.register(models.Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'type',
        'creation_date',
        'rating',
        'created',
        'modified',
        'get_genres',
        'get_persons',
    ]
    list_filter = ['type']
    search_fields = ['title', 'description', 'id']
    list_prefetch_related = ('genres', 'persons')
    inlines = (FilmworkGenreInline, FilmworkPersonInline)

    def get_queryset(self, request):
        return super().get_queryset(
            request,
        ).prefetch_related(
            *self.list_prefetch_related,
        )

    def get_genres(self, film):
        return ', '.join([genre.name for genre in film.genres.all()])
    get_genres.short_description = 'Жанры фильма'

    def get_persons(self, film):
        return ', '.join([person.full_name for person in film.persons.all()])
    get_persons.short_description = 'Персоны фильма'
