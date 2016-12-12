from mobi-application.settings import *  # noqa

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'mobi-application_test.db',
    }
}

DEBUG = True
CELERY_ALWAYS_EAGER = True
