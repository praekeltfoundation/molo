import json

import pytest
import responses

from unittest import TestCase
from molo.core.content_import import api
from molo.core.content_import.errors import SiteResponseError
from molo.core.content_import.tests.utils import catch


@pytest.mark.django_db
class TestGetRepoSummaries(TestCase):
    @responses.activate
    def test_get_repo_summaries(self):
        responses.add(
            responses.GET,
            'https://www.foo.com:3000/bar/baz/repos.json',
            content_type='application/json',
            status=200,
            body=json.dumps([{
                'index': 'repo1',
                'slug': 'foo',
                'data': {
                    'name': 'win',
                    'title': 'Repo 1',
                    'owner': 'bar',
                    'descriptor': 'baz',
                },
            }, {
                'index': 'repo2',
                'slug': 'quux',
                'data': {
                    'name': 'corege',
                    'title': 'Repo 2',
                    'owner': 'grault',
                    'descriptor': 'garply',
                },
            }]))

        self.assertEqual(api.get_repo_summaries({
            'protocol': 'https',
            'host': 'www.foo.com', 'path': 'bar/baz',
            'port': 3000
        }), [{
            'name': 'repo1',
            'title': 'Repo 1',
        }, {
            'name': 'repo2',
            'title': 'Repo 2',
        }])

    @responses.activate
    def test_get_repo_summaries_error(self):
        responses.add(
            responses.GET,
            'https://www.foo.com:3000/bar/baz/repos.json',
            content_type='application/json',
            status=404,
            body=json.dumps([{
                'index': 'repo1',
                'slug': 'foo',
                'data': {
                    'name': 'win',
                    'title': 'Repo 1',
                    'owner': 'bar',
                    'descriptor': 'baz',
                },
            }, {
                'index': 'repo2',
                'slug': 'quux',
                'data': {
                    'name': 'corege',
                    'title': 'Repo 2',
                    'owner': 'grault',
                    'descriptor': 'garply',
                },
            }]))

        error = catch(SiteResponseError, lambda: api.get_repo_summaries({
            'protocol': 'https',
            'host': 'www.foo.com',
            'path': 'bar/baz',
            'port': 3000
        }))

        self.assertEqual(
            error.message,
            "https://www.foo.com:3000/bar/baz/repos.json responded "
            "with a 404 error")

    @responses.activate
    def test_get_repo_summaries_defaults(self):
        responses.add(
            responses.GET,
            'https://www.foo.com:80/repos.json',
            content_type='application/json',
            status=200,
            body=json.dumps([{
                'index': 'repo1',
                'slug': 'foo',
                'data': {
                    'name': 'win',
                    'title': 'Repo 1',
                    'owner': 'bar',
                    'descriptor': 'baz',
                },
            }, {
                'index': 'repo2',
                'slug': 'quux',
                'data': {
                    'name': 'corege',
                    'title': 'Repo 2',
                    'owner': 'grault',
                    'descriptor': 'garply',
                },
            }]))

        self.assertEqual(api.get_repo_summaries({
            'protocol': 'https',
            'host': 'www.foo.com',
            'path': None,
            'port': None
        }), [{
            'name': 'repo1',
            'title': 'Repo 1',
        }, {
            'name': 'repo2',
            'title': 'Repo 2',
        }])

    @responses.activate
    def test_get_repo_summaries_no_title(self):
        responses.add(
            responses.GET,
            'https://www.foo.com:3000/bar/baz/repos.json',
            content_type='application/json',
            status=200,
            body=json.dumps([{
                'index': 'repo1',
                'data': {
                    'name': 'win',
                },
            }, {
                'index': 'repo2',
            }]))

        self.assertEqual(api.get_repo_summaries({
            'protocol': 'https',
            'host': 'www.foo.com', 'path': 'bar/baz',
            'port': 3000
        }), [{
            'name': 'repo1',
            'title': 'repo1',
        }, {
            'name': 'repo2',
            'title': 'repo2',
        }])
