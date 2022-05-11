"""Проектное задание панель администратора."""

import os
from pathlib import Path

from dotenv import load_dotenv
from split_settings.tools import include

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = Path(BASE_DIR).parent.joinpath('env', '.env')
load_dotenv(dotenv_path=ENV_PATH)

SECRET_KEY = os.getenv('APP_KEY')

DEBUG = os.getenv('APP_DEBUG', default=False) == 'True'

ALLOWED_HOSTS = os.getenv('APP_URL', '127.0.0.1').split(', ')
INTERNAL_IPS = ['127.0.0.1', 'localhost']

include(
    'components/apps.py',
    'components/database.py',
    'components/middleware.py',
    'components/localization.py',
    'components/password_validators.py',
    'components/templates.py',
    'components/logger.py',
    'components/debugging.py',
)

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

STATIC_URL = '/static_backend/'
STATIC_ROOT = Path(BASE_DIR).joinpath('data', 'static_backend')

MEDIA_URL = '/media_backend/'
MEDIA_ROOT = Path(BASE_DIR).joinpath('data', 'media_backend')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOCALE_PATHS = ['movies/locale']
