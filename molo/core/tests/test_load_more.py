from django.utils import timezone

from django.test import TestCase

from molo.core.tests.base import MoloTestCaseMixin
from molo.core.models import (SiteSettings, Main, Languages,
                              SiteLanguageRelation, ArticlePage)
from molo.core.tasks import promote_articles


class TestTags(MoloTestCaseMixin, TestCase):
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
        self.spanish = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(main.get_site()),
            locale='es',
            is_active=True)
        self.arabic = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(main.get_site()),
            locale='ar',
            is_active=True)

        self.yourmind = self.mk_section(
            self.section_index, title='Your mind')
        self.yourbody = self.mk_section(
            self.section_index, title='Your body')
        self.yourmind_sub = self.mk_section(
            self.yourmind, title='Your mind subsection')

        self.yourmind_fr = self.mk_section_translation(
            self.yourmind, self.french, title='Your mind in french')
        self.yourmind_sub_fr = self.mk_section_translation(
            self.yourmind_sub, self.french,
            title='Your mind subsection in french')

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
        self.yourmind_sub2 = self.mk_section(
            self.yourmind2, title='Your mind subsection2')

        self.site_settings = SiteSettings.for_site(main.get_site())
        self.site_settings2 = SiteSettings.for_site(self.main2.get_site())
        self.site_settings.enable_clickable_tags = True
        self.site_settings.enable_tag_navigation = True
        self.site_settings.save()

    def test_home_more(self):
        articles = self.mk_articles(parent=self.yourmind, count=30)
        for article in articles[:12]:
            article.featured_in_latest_start_date = timezone.now()
            article.save()
        promote_articles()
        articles = ArticlePage.objects.all()
        response = self.client.get('/home-more/?page=2')
        for article in articles[12:24]:
            self.assertContains(response, article.title)
        for article in articles[24:]:
            self.assertNotContains(response, article.title)
        response = self.client.get('/home-more/?page=3')
        for article in articles[24:]:
            self.assertContains(response, article.title)
        for article in articles[12:24]:
            self.assertNotContains(response, article.title)
        self.assertNotContains(response, 'More')

    def test_home_index(self):
        articles = self.mk_articles(parent=self.yourmind, count=30)
        for article in articles[:12]:
            article.featured_in_latest_start_date = timezone.now()
            article.save()
        promote_articles()
        articles = ArticlePage.objects.all()
        response = self.client.get('/home-index/?page=2')
        for article in articles[12:24]:
            self.assertContains(response, article.title)
        for article in articles[24:]:
            self.assertNotContains(response, article.title)
        response = self.client.get('/home-index/?page=3')
        for article in articles[24:]:
            self.assertContains(response, article.title)
        for article in articles[12:24]:
            self.assertNotContains(response, article.title)
        self.assertNotContains(response, 'More')
