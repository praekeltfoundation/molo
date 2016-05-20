import mock
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from elasticgit.tests.base import ModelBaseTest

from molo.core.tests.base import MoloTestCaseMixin
from molo.core.content_import.tests.base import ElasticGitTestMixin
from molo.core.content_import.api import Repo
from molo.core.content_import.errors import (
    InvalidParametersError, SiteResponseError)


@pytest.mark.django_db
class ContentImportAPITestCase(
        ModelBaseTest, MoloTestCaseMixin, ElasticGitTestMixin):

    def setUp(self):
        self.client = APIClient()

    @mock.patch('molo.core.content_import.views.api')
    def test_get_repo_summaries(self, api):
        def get_repo_summaries(d):
            calls.append(d)
            return ['foo']

        User.objects.create_superuser('testuser', 'testuser@email.com', '1234')
        self.client.login(username='testuser', password='1234')

        calls = []
        api.get_repo_summaries = get_repo_summaries
        resp = self.client.get('/import/repos/', {
            'path': 'bar/baz',
            'port': '3000',
            'host': 'foo.com',
            'protocol': 'https'
        })

        self.assertEqual(calls, [{
            'path': 'bar/baz',
            'port': '3000',
            'host': 'foo.com',
            'protocol': 'https'
        }])

        self.assertEquals(resp.data, {'repos': ['foo']})
        self.assertEquals(resp.status_code, 200)

    @mock.patch('molo.core.content_import.views.api')
    def test_get_repo_summaries_site_response_error(self, api):
        def get_repo_summaries(*a, **kw):
            raise SiteResponseError(':/')

        User.objects.create_superuser('testuser', 'testuser@email.com', '1234')
        self.client.login(username='testuser', password='1234')

        api.get_repo_summaries = get_repo_summaries
        resp = self.client.get('/import/repos/', {
            'path': 'bar/baz',
            'port': '3000',
            'host': 'foo.com',
            'protocol': 'https'
        })

        self.assertEquals(resp.data, {'type': 'site_response_error'})
        self.assertEquals(resp.status_code, 422)

    @mock.patch('molo.core.content_import.views.api')
    def test_get_repo_summaries_invalid_parameters(self, api):
        def get_repo_summaries(*a, **kw):
            raise InvalidParametersError(':/', [{'type': 'fake_error'}])

        User.objects.create_superuser('testuser', 'testuser@email.com', '1234')
        self.client.login(username='testuser', password='1234')

        api.get_repo_summaries = get_repo_summaries
        resp = self.client.get('/import/repos/')

        self.assertEquals(resp.data, {
            'type': 'invalid_parameters',
            'errors': [{'type': 'fake_error'}]
        })

        self.assertEquals(resp.status_code, 422)

    @mock.patch('molo.core.content_import.views.api')
    def test_get_languages(self, api):
        User.objects.create_superuser('testuser', 'testuser@email.com', '1234')
        self.client.login(username='testuser', password='1234')

        repos = fake_repos('r1', 'r2')
        api.get_repos_by_name = lambda names, **kw: find_repos(repos, names)

        api.get_languages = lambda wses: {
            repos: {
                'locales': [{
                    'locale': 'eng_GB',
                    'name': 'English (United Kingdom)'
                }],
                'warnings': []
            },
        }[wses]

        resp = self.client.get('/import/languages/?repo=r1&repo=r2')

        self.assertEquals(resp.data, {
            'locales': [{
                'locale': 'eng_GB',
                'name': 'English (United Kingdom)'
            }],
            'warnings': [],
        })

        self.assertEquals(resp.status_code, 200)

    @mock.patch('molo.core.content_import.views.api')
    def test_import_content(self, api):
        User.objects.create_superuser('testuser', 'testuser@email.com', '1234')
        self.client.login(username='testuser', password='1234')

        imports = []
        repos = fake_repos('r1', 'r2')
        api.get_repos = lambda names, **kw: find_repos(repos, names)

        api.validate_content = lambda *a, **kw: {
            'errors': [],
            'warnings': [{'type': 'fake_warning'}],
        }

        api.import_content = lambda wses, locales: (
            imports.append((wses, locales)))

        resp = self.client.put('/import/content/', data={
            'repos': ['r1', 'r2'],
            'locales': ['en', 'fr']
        }, format='json')

        self.assertEquals(resp.status_code, 201)

        self.assertEquals(resp.data, {
            'repos': ['r1', 'r2'],
            'locales': ['en', 'fr'],
            'errors': [],
            'warnings': [{'type': 'fake_warning'}],
        })

    @mock.patch('molo.core.content_import.views.api')
    def test_import_content_validation_errors(self, api):
        User.objects.create_superuser('testuser', 'testuser@email.com', '1234')
        self.client.login(username='testuser', password='1234')

        imports = []
        repos = fake_repos('r1', 'r2')
        api.get_repos = lambda names, **kw: find_repos(repos, names)

        api.validate_content = lambda wses, locales: {
            (repos, ('en', 'fr')): {
                'errors': [{'type': 'fake_error'}],
                'warnings': [{'type': 'fake_warning'}],
            }
        }[(wses, tuple(locales))]

        api.import_content = lambda wses, locales: (
            imports.append((wses, locales)))

        resp = self.client.put('/import/content/', data={
            'repos': ['r1', 'r2'],
            'locales': ['en', 'fr']
        }, format='json')

        self.assertEquals(resp.data, {
            'type': 'validation_failure',
            'errors': [{'type': 'fake_error'}],
            'warnings': [{'type': 'fake_warning'}],
        })

        self.assertEqual(imports, [])
        self.assertEquals(resp.status_code, 422)

    @mock.patch('molo.core.content_import.views.api')
    def test_import_content_invalid_parameters(self, api):
        def validate_content(*a, **kw):
            raise InvalidParametersError(':/', [{'type': 'fake_error'}])

        User.objects.create_superuser('testuser', 'testuser@email.com', '1234')
        self.client.login(username='testuser', password='1234')

        imports = []
        repos = fake_repos('r1', 'r2')
        api.get_repos = lambda names, **kw: find_repos(repos, names)

        api.validate_content = validate_content

        resp = self.client.put('/import/content/', data={
            'repos': ['r1', 'r2'],
            'locales': ['en', 'fr']
        }, format='json')

        self.assertEquals(resp.data, {
            'type': 'invalid_parameters',
            'errors': [{'type': 'fake_error'}],
        })

        self.assertEqual(imports, [])
        self.assertEquals(resp.status_code, 422)

    @mock.patch('molo.core.content_import.views.api')
    def test_validate_content(self, api):
        User.objects.create_superuser('testuser', 'testuser@email.com', '1234')
        self.client.login(username='testuser', password='1234')

        repos = fake_repos('r1', 'r2')
        api.get_repos = lambda names, **kw: find_repos(repos, names)

        api.validate_content = lambda wses, locales: {
            (repos, ('en', 'fr')): {
                'errors': [{'type': 'fake_error'}],
                'warnings': [{'type': 'fake_warning'}],
            }
        }[(wses, tuple(locales))]

        resp = self.client.post('/import/validation/', data={
            'repos': ['r1', 'r2'],
            'locales': ['en', 'fr']
        }, format='json')

        self.assertEquals(resp.data, {
            'repos': ['r1', 'r2'],
            'locales': ['en', 'fr'],
            'errors': [{'type': 'fake_error'}],
            'warnings': [{'type': 'fake_warning'}],
        })

        self.assertEquals(resp.status_code, 200)

    @mock.patch('molo.core.content_import.views.api')
    def test_validate_content_invalid_parameters(self, api):
        def validate_content(*a, **kw):
            raise InvalidParametersError(':/', [{'type': 'fake_error'}])

        User.objects.create_superuser('testuser', 'testuser@email.com', '1234')
        self.client.login(username='testuser', password='1234')

        imports = []
        repos = fake_repos('r1', 'r2')
        api.get_repos = lambda names, **kw: find_repos(repos, names)

        api.validate_content = validate_content

        resp = self.client.post('/import/validation/', data={
            'repos': ['r1', 'r2'],
            'locales': ['en', 'fr']
        }, format='json')

        self.assertEquals(resp.data, {
            'type': 'invalid_parameters',
            'errors': [{'type': 'fake_error'}],
        })

        self.assertEqual(imports, [])
        self.assertEquals(resp.status_code, 422)


def fake_repos(*names):
    return tuple(Repo(None, name, name) for name in names)


def find_repos(repos, names):
    return tuple(r for r in repos if r.name in names)
