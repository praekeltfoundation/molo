from molo.core.content_import.helpers.locales import locales_not_in_repo


def parse_validate_content(repos, locales):
    main, errors = get_main(locales)
    errors = errors + check_languages_not_in_repos(repos, locales)

    return {
        'main': main,
        'children': get_children_locales(main, locales),
        'errors': errors
    }


def check_languages_not_in_repos(repos, locales):
    errors = [check_languages_not_in_repo(repo, locales) for repo in repos]
    return [error for error in errors if error is not None]


def check_languages_not_in_repo(repo, locales):
    missing = locales_not_in_repo(repo, locales)
    if missing:
        return {
            'type': 'languages_not_in_repo',
            'details': {
                'repo': repo.name,
                'locales': missing
            }
        }
    else:
        return None


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
