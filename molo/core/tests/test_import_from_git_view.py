import pytest

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group

from molo.core.tests.base import MoloTestCaseMixin
from molo.core.models import SiteLanguage


@pytest.mark.django_db
class TestImportFromGit(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.user = self.login()
        self.group = Group(name="Universal Core Importers")
        self.group.save()

    def test_wagtail_has_import_menu_item(self):
        response = self.client.get(reverse('import-from-git'))
        self.assertContains(
            response, 'Import content from a Universal Core site')

    def test_wagtail_has_no_import_menu_item_for_invalid_user(self):
        response = self.client.get('/admin/')
        self.assertNotContains(
            response, 'Import content')

    def test_wagtail_has_no_import_menu_item_with_lang_page(self):
        self.english = SiteLanguage.objects.create(
            locale='en',
        )
        response = self.client.get('/admin/')
        self.assertNotContains(
            response, 'Import content')

    def test_wagtail_has_import_menu_item_valid_user(self):
        self.user.groups.add(self.group)
        response = self.client.get('/admin/')
        self.assertContains(
            response, 'Import content')

    def test_wagtail_has_import_menu_item_lang_page(self):
        self.english = SiteLanguage.objects.create(
            locale='en',
        )
        self.user.groups.add(self.group)
        response = self.client.get('/admin/')
        self.assertContains(
            response, 'Import content')
