from testapp.settings.base import *


ENABLE_SSO = True

MIDDLEWARE_CLASSES += (
    'molo.core.middleware.MoloCASMiddleware',
    'molo.core.middleware.Custom403Middleware',
)


AUTHENTICATION_BACKENDS = (
    'molo.profiles.backends.MoloProfilesModelBackend',
    'molo.core.backends.MoloModelBackend',
    'django.contrib.auth.backends.ModelBackend',
    'molo.core.backends.MoloCASBackend',
)

CAS_SERVER_URL = 'http://testcasserver'
CAS_ADMIN_PREFIX = '/admin/'
LOGIN_URL = '/accounts/login/'
CAS_VERSION = '3'


CELERY_ALWAYS_EAGER = True

DEAFULT_SITE_PORT = 8000


INSTALLED_APPS = INSTALLED_APPS + [
    'import_export',
]
