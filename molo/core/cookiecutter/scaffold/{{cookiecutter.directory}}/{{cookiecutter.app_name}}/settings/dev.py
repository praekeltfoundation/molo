from .base import *  # noqa


DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    '.localhost',
]

try:
    from .local import *  # noqa
except ImportError:
    pass
