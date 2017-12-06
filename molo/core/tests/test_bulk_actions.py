# -*- coding: utf-8 -*-
import pytest

from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings

from molo.core.tests.base import MoloTestCaseMixin

from molo.core.models import Main, SiteLanguageRelation, Languages

from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.tests.utils import Image, get_test_image_file


@pytest.mark.django_db
@override_settings(GOOGLE_ANALYTICS={})
class TestPages(TestCase, MoloTestCaseMixin):

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
        self.yourmind_sub = self.mk_section(
            self.yourmind, title='Your mind subsection')

        self.yourmind_fr = self.mk_section_translation(
            self.yourmind, self.french, title='Your mind in french')
        self.yourmind_sub_fr = self.mk_section_translation(
            self.yourmind_sub, self.french,
            title='Your mind subsection in french')

        # Create an image for running tests on
        self.image = Image.objects.create(
            title="Test image",
            file=get_test_image_file(),
        )

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

        # Create an image for running tests on
        self.image2 = Image.objects.create(
            title="Test image",
            file=get_test_image_file(),
        )

        self.yourmind2 = self.mk_section(
            self.section_index2, title='Your mind2')
        self.yourmind_sub2 = self.mk_section(
            self.yourmind2, title='Your mind subsection2')

    def test_copy_to_all_for_section_with_article_with_translations(self):
        self.assertFalse(
            Languages.for_site(
                self.main2.get_site()).languages.filter(locale='fr').exists())
        article = self.mk_articles(self.yourmind, 1)[0]
        self.mk_article_translation(article, self.french)
        self.mk_section_translation(self.yourmind, self.french)
        self.user = self.login()
        self.client.post(reverse('copy-to-all', args=(self.yourmind.id,)))

        self.assertTrue(Page.objects.descendant_of(
            self.main2).filter(slug=article.slug).exists())
        self.assertTrue(Page.objects.descendant_of(
            self.main2).filter(slug=self.yourmind.slug).exists())
        self.assertTrue(
            Languages.for_site(
                self.main2.get_site()).languages.filter(locale='fr').exists())
        self.assertFalse(
            Languages.for_site(
                self.main2.get_site()).languages.filter(
                    locale='fr').first().is_active)
        new_section = Page.objects.descendant_of(
            self.main2).filter(slug=self.yourmind.slug).first()
        self.assertEquals(
            new_section.get_children().count(),
            self.yourmind.get_children().count())
        self.assertEquals(
            new_section.translations.all().count(),
            self.yourmind.translations.all().count())
