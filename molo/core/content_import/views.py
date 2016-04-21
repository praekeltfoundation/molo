from rest_framework.parsers import JSONParser
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes)
from rest_framework.response import Response
from rest_framework.authentication import (
    SessionAuthentication, BasicAuthentication)
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import parser_classes

from molo.core.content_import import api
from unicore.content.models import Localisation


@api_view(['GET'])
def get_repos(request):
    return Response({'repos': api.get_repo_summaries()})


@api_view(['GET'])
def get_repo_languages(request):
    names = request.query_params.getlist('repo')
    repos = api.get_repos(names, models=(Localisation,))
    result = api.get_languages(repos)

    return Response({
        'locales': result['locales'],
        'warnings': result['warnings']
    })


@api_view(['PUT'])
@parser_classes((JSONParser,))
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def import_content(request):
    data = request.data
    repo_data, locales = data['repos'], data['locales']
    repos = api.get_repos(repo_data)

    # TODO handle `InvalidParameterError`s
    result = api.validate_content(repos, locales)

    if result['errors']:
        return Response(status=422, data={
            'type': 'validation_failure',
            'errors': result['errors']
        })
    else:
        api.import_content(repos, locales)
        return Response(status=204)


@api_view(['POST'])
@parser_classes((JSONParser,))
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def import_validate(request):
    data = request.data
    repo_data, locales = data['repos'], data['locales']
    repos = api.get_repos(repo_data)

    # TODO handle `InvalidParameterError`s
    result = api.validate_content(repos, locales)

    return Response(data={
        'repos': repo_data,
        'locales': locales,
        'errors': result['errors']
    })
