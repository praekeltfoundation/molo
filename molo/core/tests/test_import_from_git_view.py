import pytest

from django.test import TestCase
from django.core.urlresolvers import reverse

from molo.core.tests.base import MoloTestCaseMixin


@pytest.mark.django_db
class TestImportFromGit(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.user = self.login()

    def test_wagtail_has_import_menu_item(self):
        response = self.client.get(reverse('import-from-git'))
        self.assertContains(
            response, 'Import content from a Universal Core site')
