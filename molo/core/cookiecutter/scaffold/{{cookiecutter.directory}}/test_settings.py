from {{cookiecutter.app_name}}.settings import *  # noqa

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '{{cookiecutter.app_name}}_test.db',
    }
}

DEBUG = True
CELERY_ALWAYS_EAGER = True

DEFAULT_SITE_PORT = 8000
