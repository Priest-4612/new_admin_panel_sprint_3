"""Файл конфигурации базы данных проекта."""

import os

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.getenv('POSTGRES_DB', None),
        'USER': os.getenv('POSTGRES_USER', None),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', None),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'OPTIONS': {
           'options': '-c search_path=public,content',
        },
    },
}
