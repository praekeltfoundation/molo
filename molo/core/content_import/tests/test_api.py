import pytest
import responses

from django.contrib.auth.models import User

from rest_framework.test import APIClient

from elasticgit.tests.base import ModelBaseTest

from molo.core.models import SiteLanguage, SectionPage, ArticlePage, FooterPage
from molo.core.tests.base import MoloTestCaseMixin
from molo.core.content_import.tests.base import ElasticGitTestMixin
from molo.core.content_import.helper import ContentImportHelper

from unicore.content import models as eg_models


@pytest.mark.django_db
class ContentImportAPITestCase(
        ModelBaseTest, MoloTestCaseMixin, ElasticGitTestMixin):

    def setUp(self):
        self.client = APIClient()

    @responses.activate
    def test_get_repos(self):
        self.mock_get_repos_from_ucd()

        User.objects.create_superuser('testuser', 'testuser@email.com', '1234')
        self.client.login(username='testuser', password='1234')

        resp = self.client.get('/import/repos/')
        self.assertEquals(resp.data, {'repos': []})
