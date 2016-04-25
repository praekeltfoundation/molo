from rest_framework.parsers import JSONParser
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes)
from rest_framework.response import Response
from rest_framework.authentication import (
    SessionAuthentication, BasicAuthentication)
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import parser_classes

from unicore.content.models import Localisation

from molo.core.content_import import api
from molo.core.content_import.errors import (
    InvalidParametersError, SiteResponseError)


@api_view(['GET'])
def get_repo_summaries(request):
    params = request.query_params

    try:
        return Response({
            'repos': api.get_repo_summaries({
                'port': params.get('port'),
                'path': params.get('path'),
                'host': params.get('host'),
                'protocol': params.get('protocol')
            })
        })
    except SiteResponseError:
        return Response(status=422, data={'type': 'site_response_error'})
    except InvalidParametersError as e:
        return invalid_parameters_response(e)


@api_view(['GET'])
def get_repo_languages(request):
    names = request.query_params.getlist('repo')
    repos = api.get_repos_by_name(names, models=(Localisation,))
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

    try:
        result = api.validate_content(repos, locales)
    except InvalidParametersError as e:
        return invalid_parameters_response(e)

    if result['errors']:
        return Response(status=422, data={
            'type': 'validation_failure',
            'errors': result['errors'],
            'warnings': result['warnings']
        })
    else:
        api.import_content(repos, locales)
        return Response(status=200, data={
            'repos': repo_data,
            'locales': locales,
            'errors': [],
            'warnings': result['warnings']
        })


@api_view(['POST'])
@parser_classes((JSONParser,))
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def import_validate(request):
    data = request.data
    repo_data, locales = data['repos'], data['locales']
    repos = api.get_repos(repo_data)

    try:
        result = api.validate_content(repos, locales)
    except InvalidParametersError as e:
        return invalid_parameters_response(e)

    return Response(data={
        'repos': repo_data,
        'locales': locales,
        'errors': result['errors'],
        'warnings': result['warnings']
    })


def invalid_parameters_response(error):
    return Response(status=422, data={
        'type': 'invalid_parameters',
        'errors': error.errors,
    })
