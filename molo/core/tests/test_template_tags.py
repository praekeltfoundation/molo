# coding=utf-8
import pytest
from django.test import TestCase, RequestFactory
from molo.core.models import (Main, SiteLanguageRelation, Languages,)
from molo.core.tests.base import MoloTestCaseMixin
from molo.core.templatetags.core_tags import get_parent


@pytest.mark.django_db
class TestModels(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.main = Main.objects.all().first()
        self.factory = RequestFactory()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)

        self.french = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='fr',
            is_active=True)

        self.yourmind = self.mk_section(
            self.section_index, title='Your mind')
        self.yourmind_sub = self.mk_section(
            self.yourmind, title='Your mind subsection')

    def test_get_parent_template_tag(self):
        request = self.factory.get('/')
        request.site = self.site

        article = self.mk_articles(self.yourmind, 1)[0]
        fr_article = self.mk_article_translation(article, self.french)

        self.assertEquals(
            get_parent({'locale_code': 'fr', 'request': request}, article),
            self.yourmind)
        self.assertEquals(
            get_parent({'locale_code': 'fr', 'request': request}, fr_article),
            self.yourmind)
        self.assertEquals(get_parent(
            {'locale_code': 'fr', 'request': request}, self.yourmind_sub),
            self.yourmind)

        fr_yourmind = self.mk_section_translation(self.yourmind, self.french)
        self.assertEquals(
            get_parent({'locale_code': 'en', 'request': request}, article),
            self.yourmind)
        self.assertEquals(
            get_parent({'locale_code': 'en', 'request': request}, fr_article),
            self.yourmind)
        self.assertEquals(get_parent(
            {'locale_code': 'en', 'request': request}, self.yourmind_sub),
            self.yourmind)

        self.assertEquals(
            get_parent({'locale_code': 'fr', 'request': request}, article),
            fr_yourmind)
        self.assertEquals(
            get_parent({'locale_code': 'fr', 'request': request}, fr_article),
            fr_yourmind)
        self.assertEquals(get_parent(
            {'locale_code': 'fr', 'request': request}, self.yourmind_sub),
            fr_yourmind)

        self.assertEquals(get_parent(
            {'locale_code': 'fr', 'request': request}, self.yourmind),
            None)
