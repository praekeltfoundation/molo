from testapp.settings import *


ENABLE_SSO = True

MIDDLEWARE_CLASSES += (
    'molo.core.middleware.MoloCASMiddleware',
    'molo.core.middleware.Custom403Middleware',
)


AUTHENTICATION_BACKENDS = (
    'molo.core.backends.MoloModelBackend',
    'django.contrib.auth.backends.ModelBackend',
    'molo.core.backends.MoloCASBackend',
)

CAS_SERVER_URL = 'http://testcasserver'
CAS_ADMIN_PREFIX = '/admin/'
LOGIN_URL = '/accounts/login/'
CAS_VERSION = '3'

UNICORE_DISTRIBUTE_API = 'http://testserver:6543'
CELERY_ALWAYS_EAGER = True

DEAFULT_SITE_PORT = 8000
