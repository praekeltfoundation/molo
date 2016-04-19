from django.conf import settings

import requests
from elasticgit.workspace import RemoteWorkspace
from unicore.content.models import Localisation, Category, Page

from molo.core.content_import.errors import InvalidParametersError
from molo.core.content_import.helpers.locales import get_locales
from molo.core.content_import.helpers.importing import ContentImportHelper
from molo.core.content_import.helpers.validation import ContentImportValidation
from molo.core.content_import.helpers.parse import (
    parse_validate_content, parse_import_content)


def get_repo_summaries():
    response = requests.get('%s/repos.json' % settings.UNICORE_DISTRIBUTE_API)
    return [d.get('name') for d in response.json()]


def get_languages(repos):
    return get_locales(repos)


def import_content(repos, locales):
    result = parse_import_content(repos, locales)
    main, children = result['main'], result['children']

    if result['errors']:
        raise InvalidParametersError(
            "Invalid parameters given for content import",
            result['errors'])

    if len(repos) == 1:
        import_content_repo(repos[0], main, children)
    elif len(repos) > 1:
        import_content_multirepo(repos, main, children)


def import_content_repo(repo, main, children):
    ContentImportHelper(repo).import_content_for(main, children)


def import_content_multirepo(repos, main, children):
    raise NotImplementedError()


def validate_content(repos, locales):
    result = parse_validate_content(repos, locales)
    main, children = result['main'], result['children']

    if result['errors']:
        raise InvalidParametersError(
            "Invalid parameters given for content validation",
            result['errors'])

    errors = [
        error
        for repo in repos
        for error in validate_content_repo(repo, main, children)]

    # returns a dictionary to make provision for warnings
    return {
        'errors': errors
    }


def validate_content_repo(repo, main, children):
    validator = ContentImportValidation(repo)
    return validator.validate_for(main, children)


def get_repos(data, models=(Localisation, Category, Page)):
    return [get_repo(d, models) for d in data]


def get_repo(datum, models=(Localisation, Category, Page)):
    workspace = RemoteWorkspace('%s/repos/%s.json' % (
        settings.UNICORE_DISTRIBUTE_API, datum['name']))

    for model in models:
        workspace.sync(model)

    return Repo(workspace, **datum)


class Repo(object):
    def __init__(self, workspace, name, title):
        self.workspace = workspace
        self.name = name
        self.title = title
