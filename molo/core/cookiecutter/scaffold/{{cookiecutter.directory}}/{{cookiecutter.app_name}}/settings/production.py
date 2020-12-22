from .base import *  # noqa


# Disable debug mode

DEBUG = False
ENV = 'prd'
TEMPLATE_DEBUG = False

DEFAULT_SITE_PORT = 80

# Compress static files offline
# http://django-compressor.readthedocs.org/en/latest/settings/#django.conf.settings.COMPRESS_OFFLINE

COMPRESS_OFFLINE = True


# Send notification emails as a background task using Celery,
# to prevent this from blocking web server threads
# (requires the django-celery package):
# http://celery.readthedocs.org/en/latest/configuration.html

#
#
# CELERY_SEND_TASK_ERROR_EMAILS = True
# BROKER_URL = 'redis://'


# Use Redis as the cache backend for extra performance
# (requires the django-redis-cache package):
# http://wagtail.readthedocs.org/en/latest/howto/performance.html#cache

# CACHES = {
#     'default': {
#         'BACKEND': 'redis_cache.cache.RedisCache',
#         'LOCATION': '127.0.0.1:6379',
#         'KEY_PREFIX': 'base',
#         'OPTIONS': {
#             'CLIENT_CLASS': 'redis_cache.client.DefaultClient',
#         }
#     }
# }

# Setup for CAS
ENABLE_SSO = True

MIDDLEWARE += [  # noqa: F405
    'molo.core.middleware.MoloCASMiddleware',
    'molo.core.middleware.Custom403Middleware',
]


AUTHENTICATION_BACKENDS = [
    'molo.profiles.backends.MoloProfilesModelBackend',
    'molo.core.backends.MoloModelBackend',
    'django.contrib.auth.backends.ModelBackend',
    'molo.core.backends.MoloCASBackend',
]

CAS_SERVER_URL = ''
CAS_ADMIN_PREFIX = '/admin/'
LOGIN_URL = '/accounts/login/'
CAS_VERSION = '3'

COMPRESS_OFFLINE_CONTEXT = {  # noqa
    'STATIC_URL': STATIC_URL,  # noqa
    'ENV': ENV,  # noqa
}  # noqa

try:
    from .local import *  # noqa
except ImportError:
    pass
