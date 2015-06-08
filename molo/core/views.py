from django.shortcuts import redirect
from django.utils.translation import LANGUAGE_SESSION_KEY


def locale_set(request, locale):
    request.session[LANGUAGE_SESSION_KEY] = locale
    return redirect('/')
