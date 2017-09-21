from .base import *  # noqa


DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'filters': {
#         'require_debug_false': {
#             '()': 'django.utils.log.RequireDebugFalse',
#         },
#         'require_debug_true': {
#             '()': 'django.utils.log.RequireDebugTrue',
#         },
#     },
#     'handlers': {
#         'console': {
#             'level': 'DEBUG',
#             'filters': ['require_debug_true'],
#             'class': 'logging.StreamHandler',
#         },
#         'mail_admins': {
#             'level': 'ERROR',
#             'filters': ['require_debug_false'],
#             'class': 'django.utils.log.AdminEmailHandler'
#         }
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['console', 'mail_admins'],
#             'level': 'DEBUG',
#         },
#         'py.warnings': {
#             'handlers': ['console'],
#         },
#     }
# }

try:
    from .local import *  # noqa
except ImportError:
    pass
