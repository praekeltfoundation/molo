import requests

from elasticgit.workspace import RemoteWorkspace

from molo.core.models import SiteLanguage
from molo.core.content_import.helper import ContentImportHelper

from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes)
from rest_framework.response import Response
from rest_framework.authentication import (
    SessionAuthentication, BasicAuthentication)
from rest_framework.permissions import IsAuthenticated

from unicore.content.models import Localisation, Category, Page


@api_view(['GET'])
def get_repos(request):
    response = requests.get('http://localhost:6543/repos.json').json()
    return Response({
        'repos': [repo.get('name') for repo in response]})


@api_view(['GET'])
def get_repo_languages(request, name):
    ws = RemoteWorkspace('http://localhost:6543/repos/%s.json' % name)
    ws.sync(Localisation)

    return Response({
        'locales': [l.locale for l in ws.S(Localisation).all()],
    })


@api_view(['GET'])
def get_available_languages(request):
    return Response({
        'locales': [{
            'locale': l.locale,
            'name': l.get_locale_display(),
            'is_main_language': l.is_main_language}
            for l in SiteLanguage.objects.all()],
    })


@api_view(['POST'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def import_content(request, name):
    ws = RemoteWorkspace('http://localhost:6543/repos/%s.json' % name)
    ws.sync(Localisation)
    ws.sync(Category)
    ws.sync(Page)

    # create wagtail content

    locales = request.data.get('locales')
    ContentImportHelper(ws).import_content_for(locales)
    return Response()
