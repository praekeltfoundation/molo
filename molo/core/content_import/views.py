import requests

from django.conf import settings
from elasticgit.workspace import RemoteWorkspace
from babel import Locale

from molo.core.content_import.helper import ContentImportHelper
from molo.core.content_import.validation import ContentImportValidation

from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes)
from rest_framework.response import Response
from rest_framework.authentication import (
    SessionAuthentication, BasicAuthentication)
from rest_framework.permissions import IsAuthenticated

from unicore.content.models import Localisation, Category, Page


@api_view(['GET'])
def get_repos(request):
    response = requests.get(
        '%s/repos.json' % settings.UNICORE_DISTRIBUTE_API).json()
    return Response({
        'repos': [repo.get('name') for repo in response]})


@api_view(['GET'])
def get_repo_languages(request, name):
    ws = RemoteWorkspace('%s/repos/%s.json' % (
        settings.UNICORE_DISTRIBUTE_API, name))
    ws.sync(Localisation)

    return Response({
        'locales': [{
            'locale': l.locale,
            'name': Locale.parse(l.locale).english_name
        }for l in ws.S(Localisation).all()],
    })


@api_view(['POST'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def import_content(request, name):
    ws = RemoteWorkspace('%s/repos/%s.json' % (
        settings.UNICORE_DISTRIBUTE_API, name))
    ws.sync(Localisation)
    ws.sync(Category)
    ws.sync(Page)

    # create wagtail content
    locales = request.data.get('locales')
    errors = ContentImportValidation(ws).is_validate_for(locales)

    if errors:
        return Response(status=422, data={'errors': errors})
    else:
        ContentImportHelper(ws).import_content_for(locales)
        return Response()


@api_view(['POST'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def import_validate(request, name):
    ws = RemoteWorkspace('%s/repos/%s.json' % (
        settings.UNICORE_DISTRIBUTE_API, name))
    ws.sync(Localisation)
    ws.sync(Category)
    ws.sync(Page)

    # validate import content
    locales = request.data.get('locales')
    errors = ContentImportValidation(ws).is_validate_for(locales)
    if errors:
        return Response(status=422, data={'errors': errors})
    else:
        return Response()
