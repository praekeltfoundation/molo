from .base import *  # noqa


DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

ALLOWED_HOSTS = [
    'localhost',
    '.localhost',
]

try:
    from .local import *  # noqa
except ImportError:
    pass
