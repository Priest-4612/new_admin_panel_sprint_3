from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from api.pagination import CustomPagination
from api.serializers import FilmworkSerializer
from movies.models import Filmwork, Role


class FilmworkViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Filmwork.objects.prefetch_related(
        'genres', 'persons',
    ).values().all().annotate(
        genres=ArrayAgg(
            'genres__name',
            distinct=True,
        ),
        actors=ArrayAgg(
            'persons__full_name',
            filter=Q(film_work_persons__role__icontains=Role.ACTOR),
            distinct=True,
        ),
        directors=ArrayAgg(
            'persons__full_name',
            filter=Q(film_work_persons__role__icontains=Role.DIRECTOR),
            distinct=True,
        ),
        writers=ArrayAgg(
            'persons__full_name',
            filter=Q(film_work_persons__role__icontains=Role.WRITER),
            distinct=True,
        ),
    )
    serializer_class = FilmworkSerializer
    permission_classes = [AllowAny]
    pagination_class = CustomPagination
