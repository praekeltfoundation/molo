from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import LANGUAGE_SESSION_KEY


def locale_set(request, locale):
    request.session[LANGUAGE_SESSION_KEY] = locale
    return redirect('/')


def health(request):
    return HttpResponse(status=200)


def import_from_ucd(request):
    return render(request, 'import_from_ucd.html')
