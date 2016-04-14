from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes)
from rest_framework.response import Response
from rest_framework.authentication import (
    SessionAuthentication, BasicAuthentication)
from rest_framework.permissions import IsAuthenticated

from molo.core.content_import import api
from unicore.content.models import Localisation


@api_view(['GET'])
def get_repos(request):
    return Response({'repos': api.get_repos()})


@api_view(['GET'])
def get_repo_languages(request):
    repos = request.query_params.getlist('repo')
    workspaces = api.get_workspaces(repos, models=(Localisation,))
    locales, errors = api.get_languages(workspaces)

    return Response({
        'locales': locales,
        'errors': errors
    })


@api_view(['PUT'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def import_content(request):
    data = request.data
    repos, locales = data.getlist('repos'), data.getlist('locales')
    workspaces = api.get_workspaces(repos)
    errors = api.validate_content(workspaces, locales)

    if errors:
        return Response(status=422, data={
            'type': 'validation_failure',
            'errors': errors
        })
    else:
        api.import_content(workspaces, locales)
        return Response(status=204)


@api_view(['POST'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def import_validate(request):
    data = request.data
    repos, locales = data.getlist('repos'), data.getlist('locales')
    workspaces = api.get_workspaces(repos)
    errors = api.validate_content(workspaces, locales)

    return Response(data={
        'repos': repos,
        'locales': locales,
        'errors': errors
    })
