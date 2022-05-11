from django.conf import settings

if settings.DEBUG:
    settings.INSTALLED_APPS.append('debug_toolbar')
    settings.MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
    settings.INSTALLED_APPS.append('django_extensions')
