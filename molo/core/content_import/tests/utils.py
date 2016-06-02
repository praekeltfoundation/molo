from molo.core.content_import.api import Repo


def catch(error_cls, fn):
    try:
        fn()
        return None
    except error_cls as e:
        return e


def fake_repos(*names):
    return tuple(Repo(None, name, name) for name in names)


def find_repos(repos, names):
    return tuple(r for r in repos if r.name in names)


def find_repos_from_data(repos, data):
    names = [d['name'] for d in data]
    return tuple(r for r in repos if r.name in names)
