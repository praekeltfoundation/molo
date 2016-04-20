import requests


def get_summaries(url):
    # TODO handle error responses
    return parse_repo_summaries_response(requests.get(url).json())


def parse_repo_summaries_response(resp):
    return [{
        'name': d['index'],
        'title': d['data']['title']
    } for d in resp]
