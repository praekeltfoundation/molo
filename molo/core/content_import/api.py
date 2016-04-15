from django.conf import settings

import requests
from elasticgit.workspace import RemoteWorkspace
from unicore.content.models import Localisation, Category, Page

from molo.core.content_import.helpers.locales import get_locales
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
    errors = []

    if len(repos) == 1:
        errors = validate_content_repo(repos[0], locales)
    elif len(repos) > 1:
        errors = validate_content_multirepo(repos, locales)

    return {
        'errors': errors
    }


def validate_content_repo(repo, locales):
    return ContentImportValidation(repo.workspace).is_validate_for(locales)


def validate_content_multirepo(repos, locales):
    raise NotImplementedError()


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
