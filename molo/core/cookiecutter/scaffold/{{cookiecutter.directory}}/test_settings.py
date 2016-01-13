from {{cookiecutter.app_name}}.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '{{cookiecutter.app_name}}_test.db',
    }
}

DEBUG = True
CELERY_ALWAYS_EAGER = True
