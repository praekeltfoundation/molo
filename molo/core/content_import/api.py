from django.conf import settings

from elasticgit.workspace import RemoteWorkspace

from molo.core.content_import.errors import InvalidParametersError
from molo.core.content_import.helpers.locales import get_locales
from molo.core.content_import.helpers.summaries import get_summaries
from molo.core.content_import.helpers.importing import import_repo
from molo.core.content_import.helpers.validation import ContentImportValidation
from molo.core.content_import.helpers.parse import (
    parse_get_repo_summaries, parse_validate_content, parse_import_content)


def get_repo_summaries(url_parts):
    result = parse_get_repo_summaries(url_parts)

    if result['errors']:
        raise InvalidParametersError(
            "Invalid parameters given for repo summaries retrieval",
            result['errors'])

    return get_summaries(result['url'])


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
        import_repo(repos[0], main, children)
    elif len(repos) > 1:
        import_multirepo(repos, main, children)


def import_multirepo(repos, main, children):
    for repo in repos:
        import_repo(repo, main, children, should_nest=True)


def validate_content(repos, locales):
    result = parse_validate_content(repos, locales)
    main, children = result['main'], result['children']

    if result['errors']:
        raise InvalidParametersError(
            "Invalid parameters given for content validation",
            result['errors'])

    results = [validate_repo(repo, main, children) for repo in repos]

    return {
        'warnings': [
            warning
            for res in results
            for warning in res['warnings']],
        'errors': [
            error
            for res in results
            for error in res['errors']]
    }


def validate_repo(repo, main, children):
    validator = ContentImportValidation(repo)
    return validator.validate_for(main, children)


def get_repos_by_name(names):
    return [get_repo_by_name(name) for name in names]


def get_repo_by_name(name):
    return get_repo({'name': name})


def get_repos(data):
    return [get_repo(d) for d in data]


def get_repo(datum):
    workspace = RemoteWorkspace('%s/repos/%s.json' % (
        settings.UNICORE_DISTRIBUTE_API, datum['name']))

    return Repo(workspace, **datum)


class Repo(object):
    def __init__(self, workspace, name, title=None):
        self.workspace = workspace
        self.name = name
        self.title = title
