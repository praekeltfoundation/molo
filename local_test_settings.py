from testapp.settings.base import *  # noqa: F403, F405


ALLOWED_HOSTS = [
    'localhost',
    '.localhost',
    'site2',
]

ENABLE_SSO = True

MIDDLEWARE += (  # noqa: F405
    'molo.core.middleware.MoloCASMiddleware',
    'molo.core.middleware.Custom403Middleware',
    'molo.core.middleware.MaintenanceModeMiddleware',
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


INSTALLED_APPS = INSTALLED_APPS + [  # noqa: F405
    'import_export',
]
