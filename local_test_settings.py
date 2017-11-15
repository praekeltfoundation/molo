from testapp.settings.base import *


UNICORE_DISTRIBUTE_API = 'http://testserver:6543'
CELERY_ALWAYS_EAGER = True

DEAFULT_SITE_PORT = 8000


INSTALLED_APPS = INSTALLED_APPS + [
    'import_export',
]
