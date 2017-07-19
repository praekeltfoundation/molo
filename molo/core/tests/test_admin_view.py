# coding=utf-8
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from molo.core.models import (
    Main, ReactionQuestionResponse,
    SiteLanguageRelation, Languages, ReactionQuestionChoice)
from molo.core.tests.base import MoloTestCaseMixin


class TestAdminView(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        main = Main.objects.all().first()
        self.english = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(main.get_site()),
            locale='en',
            is_active=True)

        self.french = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(main.get_site()),
            locale='fr',
            is_active=True)

        self.yourmind = self.mk_section(
            self.section_index, title='Your mind')

        self.yourmind_fr = self.mk_section_translation(
            self.yourmind, self.french, title='Your mind in french')

        self.mk_main2()
        self.main2 = Main.objects.all().last()
        self.language_setting2 = Languages.objects.create(
            site_id=self.main2.get_site().pk)
        self.english2 = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting2,
            locale='en',
            is_active=True)

        self.spanish = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting2,
            locale='es',
            is_active=True)

        self.yourmind2 = self.mk_section(
            self.section_index2, title='Your mind2')

    def test_articles_appears_in_wagtail_admin(self):
        User.objects.create_superuser(
            username='testuser', password='password', email='test@email.com')
        self.client.login(username='testuser', password='password')
        self.mk_article(self.yourmind)
        self.mk_article(self.yourmind2)
        response = self.client.get(
            '/admin/core/articlepagelanguageproxy/'
        )
        self.assertContains(response, 'Your mind')
        self.assertContains(response, 'Your mind2')
