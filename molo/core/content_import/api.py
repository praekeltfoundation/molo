from django.conf import settings

import requests
from elasticgit.workspace import RemoteWorkspace
from unicore.content.models import Localisation, Category, Page

from molo.core.content_import.errors import InvalidParametersError
from molo.core.content_import.helpers.locales import get_locales
from molo.core.content_import.helpers.parse import parse_validate_content
from molo.core.content_import.helpers.importing import ContentImportHelper
from molo.core.content_import.helpers.validation import ContentImportValidation


def get_repo_summaries():
    response = requests.get('%s/repos.json' % settings.UNICORE_DISTRIBUTE_API)
    return [d.get('name') for d in response.json()]


def get_languages(repos):
    return get_locales(repos)


def import_content(repos, locales):
    if len(repos) == 1:
        import_content_repo(repos[0], locales)
    elif len(repos) > 1:
        import_content_multirepo(repos, locales)


def import_content_repo(repo, locales):
    ContentImportHelper(repo.workspace).import_content_for(locales)


def import_content_multirepo(repos, locales):
    raise NotImplementedError()


def validate_content(repos, locales):
    result = parse_validate_content(repos, locales)
    main, locales = result['main'], result['locales']

    if result['errors']:
        raise InvalidParametersError(
            "Invalid parameters given for content validation",
            result['errors'])

    errors = [
        error
        for repo in repos
        for error in validate_content_repo(repo, main, locales)]

    # returns a dictionary to make provision for warnings
    return {
        'errors': errors
    }


def validate_content_repo(repo, main, locales):
    validator = ContentImportValidation(repo)
    return validator.validate_for(main, locales)


def get_repos(names, models=(Localisation, Category, Page)):
    return [get_repo(name, models) for name in names]


def get_repo(name, models=(Localisation, Category, Page)):
    workspace = RemoteWorkspace('%s/repos/%s.json' % (
        settings.UNICORE_DISTRIBUTE_API, name))

    for model in models:
        workspace.sync(model)

    return Repo(name, workspace)


class Repo(object):
    def __init__(self, name, workspace):
        self.name = name
        self.workspace = workspace
