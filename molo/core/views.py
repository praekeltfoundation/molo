from django.conf import settings


def locale_set(request, locale):
    request.session[settings.LANGUAGE_SESSION_KEY] = locale
