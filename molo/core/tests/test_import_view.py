import pytest

from django.test import TestCase
from django.core.urlresolvers import reverse

from molo.core.tests.base import MoloTestCaseMixin


@pytest.mark.django_db
class TestImportFromUCD(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.user = self.login()

    def test_wagtail_has_import_menu_item(self):
        response = self.client.get(reverse("import-from-ucd"))
        self.assertContains(response, 'welcome to the import page')
