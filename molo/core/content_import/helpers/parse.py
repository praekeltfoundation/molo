from urlparse import ParseResult, urlunparse

from molo.core.content_import.utils import conj, omit_nones


def parse_get_repo_summaries(url_parts):
    url_parts = conj(url_parts_defaults(), omit_nones(url_parts))
    errors = get_required_param_errors(url_parts)

    if errors:
        return {
            'url_parts': None,
            'errors': errors
        }
    else:
        return {
            'url': repo_summaries_url(url_from_parts(url_parts)),
            'errors': []
        }


def parse_validate_content(repos, locales):
    main, errors = get_main(locales)

    return {
        'main': main,
        'children': get_children_locales(main, locales),
        'errors': errors
    }


def parse_import_content(repos, locales):
    return parse_validate_content(repos, locales)


def repo_summaries_url(url):
    return '/'.join((url.rstrip('/'), 'repos.json'))


def url_parts_defaults():
    return {
        'port': 80,
        'path': '',
        'host': None,
        'protocol': 'http',
    }


def url_from_parts(parts):
    return urlunparse(ParseResult(
        parts['protocol'],
        ':'.join((parts['host'], str(parts['port']))),
        parts['path'],
        None,
        None,
        None))


def get_required_param_errors(params):
    return [{
        'type': 'missing_required_parameter',
        'details': {'name': name}
    } for name, v in params.iteritems() if v is None]


def get_children_locales(main, locales):
    return [locale['locale'] for locale in locales if locale['locale'] != main]


def get_main(locales):
    mains = [locale for locale in locales if locale.get('is_main')]

    if not mains:
        return (None, [{
            'type': 'no_main_language_given',
        }])
    elif len(mains) > 1:
        return (None, [{
            'type': 'multiple_main_languages_given',
        }])
    else:
        return (mains[0].get('locale'), [])
