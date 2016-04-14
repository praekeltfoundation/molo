import mock
import pytest
from mock import Mock
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from elasticgit.tests.base import ModelBaseTest

from molo.core.tests.base import MoloTestCaseMixin
from molo.core.content_import.tests.base import ElasticGitTestMixin


@pytest.mark.django_db
class ContentImportAPITestCase(
        ModelBaseTest, MoloTestCaseMixin, ElasticGitTestMixin):

    def setUp(self):
        self.client = APIClient()

    @mock.patch('molo.core.content_import.views.api')
    def test_get_repos(self, api):
        User.objects.create_superuser('testuser', 'testuser@email.com', '1234')
        self.client.login(username='testuser', password='1234')

        api.get_repos = lambda: ['foo']
        resp = self.client.get('/import/repos/')
        self.assertEquals(resp.data, {'repos': ['foo']})
        self.assertEquals(resp.status_code, 200)

    @mock.patch('molo.core.content_import.views.api')
    def test_get_languages(self, api):
        User.objects.create_superuser('testuser', 'testuser@email.com', '1234')
        self.client.login(username='testuser', password='1234')

        workspaces = fake_workspaces('r1', 'r2')
        ws1, ws2 = workspaces.values()

        api.get_workspaces = lambda names, **kw: pick(workspaces, *names)

        api.get_languages = lambda wses: ({
            (ws1, ws2): ['en', 'fr'],
        }[tuple(wses)], [])

        resp = self.client.get('/import/languages/?repo=r1&repo=r2')

        self.assertEquals(resp.data, {
            'locales': ['en', 'fr'],
            'errors': [],
        })

        self.assertEquals(resp.status_code, 200)

    @mock.patch('molo.core.content_import.views.api')
    def test_import_content(self, api):
        User.objects.create_superuser('testuser', 'testuser@email.com', '1234')
        self.client.login(username='testuser', password='1234')

        imports = []
        workspaces = fake_workspaces('r1', 'r2')
        ws1, ws2 = workspaces.values()

        api.get_workspaces = lambda names, **kw: pick(workspaces, *names)

        api.validate_content = lambda *a, **kw: []

        api.import_content = lambda wses, locales: (
            imports.append((wses, locales)))

        resp = self.client.put('/import/content/', data={
            'repos': ['r1', 'r2'],
            'locales': ['en', 'fr']
        })

        self.assertEqual(imports, [
            ([ws1, ws2], ['en', 'fr'])
        ])

        self.assertEquals(resp.status_code, 204)

    @mock.patch('molo.core.content_import.views.api')
    def test_import_content_validation_errors(self, api):
        User.objects.create_superuser('testuser', 'testuser@email.com', '1234')
        self.client.login(username='testuser', password='1234')

        imports = []
        workspaces = fake_workspaces('r1', 'r2')
        ws1, ws2 = workspaces.values()

        api.get_workspaces = lambda names, **kw: pick(workspaces, *names)

        api.validate_content = lambda *a, **kw: [{'type': 'fake_error'}]

        api.import_content = lambda wses, locales: (
            imports.append((wses, locales)))

        resp = self.client.put('/import/content/', data={
            'repos': ['r1', 'r2'],
            'locales': ['en', 'fr']
        })

        self.assertEquals(resp.status_code, 422)

        self.assertEqual(imports, [])

        self.assertEquals(resp.data, {
            'type': 'validation_failure',
            'errors': [{'type': 'fake_error'}],
        })

    @mock.patch('molo.core.content_import.views.api')
    def test_validate_content(self, api):
        User.objects.create_superuser('testuser', 'testuser@email.com', '1234')
        self.client.login(username='testuser', password='1234')

        workspaces = fake_workspaces('r1', 'r2')
        ws1, ws2 = workspaces.values()

        api.get_workspaces = lambda names, **kw: pick(workspaces, *names)

        api.validate_content = lambda wses, locales: {
            ((ws1, ws2), ('en', 'fr')): [{'type': 'fake_error'}]
        }[(tuple(wses), tuple(locales))]

        resp = self.client.post('/import/validation/', data={
            'repos': ['r1', 'r2'],
            'locales': ['en', 'fr']
        })

        self.assertEquals(resp.data, {
            'repos': ['r1', 'r2'],
            'locales': ['en', 'fr'],
            'errors': [{'type': 'fake_error'}],
        })

        self.assertEquals(resp.status_code, 200)


def fake_workspace(name):
    ws = Mock()
    ws.name = name
    return ws


def fake_workspaces(*names):
    return dict((name, fake_workspace(name)) for name in names)


def pick(obj, *keys):
    return [obj[k] for k in keys]
