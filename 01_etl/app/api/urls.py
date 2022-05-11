from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import FilmworkViewSet

app_name = 'api'
router = DefaultRouter()
router.register('movies', FilmworkViewSet, basename='filmworks')

urlpatterns = [
    path('v1/', include(router.urls)),
]
