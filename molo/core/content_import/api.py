from django.conf import settings

import requests
from elasticgit.workspace import RemoteWorkspace
from unicore.content.models import Localisation, Category, Page

from molo.core.content_import.helper import ContentImportHelper
from molo.core.content_import.validation import ContentImportValidation


def get_repos():
    response = requests.get('%s/repos.json' % settings.UNICORE_DISTRIBUTE_API)
    return [repo.get('name') for repo in response.json()]


def get_languages(workspaces):
    if len(workspaces) == 1:
        return get_repo_languages(workspaces[0])
    elif len(workspaces) > 1:
        return get_multirepo_languages(workspaces)


def get_repo_languages(workspace):
    return ContentImportHelper(workspace).parse_locales()


def get_multirepo_languages(workspaces):
    raise NotImplementedError()


def import_content(workspaces, locales):
    if len(workspaces) == 1:
        import_content_repo(workspaces[0], locales)
    elif len(workspaces) > 1:
        import_content_multirepo(workspaces, locales)


def import_content_repo(workspace, locales):
    ContentImportHelper(workspace).import_content_for(locales)


def import_content_multirepo(workspaces, locales):
    raise NotImplementedError()


def validate_content(workspaces, locales):
    if len(workspaces) == 1:
        return validate_content_repo(workspaces[0], locales)
    elif len(workspaces) > 1:
        return validate_content_multirepo(workspaces, locales)
    else:
        return {'errors': []}


def validate_content_repo(workspace, locales):
    return ContentImportValidation(workspace).is_validate_for(locales)


def validate_content_multirepo(workspaces, locales):
    raise NotImplementedError()


def get_workspaces(names, models=(Localisation, Category, Page)):
    return [get_workspace(name, models) for name in names]


def get_workspace(name, models=(Localisation, Category, Page)):
    ws = RemoteWorkspace('%s/repos/%s.json' % (
        settings.UNICORE_DISTRIBUTE_API, name))

    for model in models:
        ws.sync(model)
