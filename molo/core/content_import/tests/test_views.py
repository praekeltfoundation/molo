import mock
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from elasticgit.tests.base import ModelBaseTest

from molo.core.tests.base import MoloTestCaseMixin
from molo.core.content_import.tests.base import ElasticGitTestMixin
from molo.core.content_import.api import Repo
from molo.core.content_import.errors import SiteResponseError


@pytest.mark.django_db
class ContentImportAPITestCase(
        ModelBaseTest, MoloTestCaseMixin, ElasticGitTestMixin):

    def setUp(self):
        self.client = APIClient()

    @mock.patch('molo.core.content_import.views.api')
    def test_get_repos(self, api):
        User.objects.create_superuser('testuser', 'testuser@email.com', '1234')
        self.client.login(username='testuser', password='1234')

        api.get_repo_summaries = lambda: ['foo']
        resp = self.client.get('/import/repos/')

        self.assertEquals(resp.data, {'repos': ['foo']})
        self.assertEquals(resp.status_code, 200)

    @mock.patch('molo.core.content_import.views.api')
    def test_get_repos_site_response_error(self, api):
        def get_repo_summaries():
            raise SiteResponseError(':/')

        User.objects.create_superuser('testuser', 'testuser@email.com', '1234')
        self.client.login(username='testuser', password='1234')

        api.get_repo_summaries = get_repo_summaries
        resp = self.client.get('/import/repos/')

        self.assertEquals(resp.data, {'type': 'site_response_error'})
        self.assertEquals(resp.status_code, 422)

    @mock.patch('molo.core.content_import.views.api')
    def test_get_languages(self, api):
        User.objects.create_superuser('testuser', 'testuser@email.com', '1234')
        self.client.login(username='testuser', password='1234')

        repos = fake_repos('r1', 'r2')
        api.get_repos = lambda names, **kw: find_repos(repos, names)

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

        api.validate_content = lambda *a, **kw: {'errors': []}

        api.import_content = lambda wses, locales: (
            imports.append((wses, locales)))

        resp = self.client.put('/import/content/', data={
            'repos': ['r1', 'r2'],
            'locales': ['en', 'fr']
        }, format='json')

        self.assertEqual(imports, [
            (repos, ['en', 'fr'])
        ])

        self.assertEquals(resp.status_code, 204)

    @mock.patch('molo.core.content_import.views.api')
    def test_import_content_validation_errors(self, api):
        User.objects.create_superuser('testuser', 'testuser@email.com', '1234')
        self.client.login(username='testuser', password='1234')

        imports = []
        repos = fake_repos('r1', 'r2')
        api.get_repos = lambda names, **kw: find_repos(repos, names)

        api.validate_content = lambda wses, locales: {
            (repos, ('en', 'fr')): {
                'errors': [{'type': 'fake_error'}]
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
                'errors': [{'type': 'fake_error'}]
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
        })

        self.assertEquals(resp.status_code, 200)


def fake_repos(*names):
    return tuple(Repo(None, name, name) for name in names)


def find_repos(repos, names):
    return tuple(r for r in repos if r.name in names)
