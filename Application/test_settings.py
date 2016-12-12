from Application.settings import *  # noqa

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'Application_test.db',
    }
}

DEBUG = True
CELERY_ALWAYS_EAGER = True
