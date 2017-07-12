from django.conf import settings


def compress_settings(request):
    return {
        'STATIC_URL': settings.STATIC_URL,
        'ENV': settings.ENV
    }
