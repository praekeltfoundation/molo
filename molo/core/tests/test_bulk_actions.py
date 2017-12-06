# -*- coding: utf-8 -*-
import pytest

from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings

from molo.core.tests.base import MoloTestCaseMixin

from molo.core.models import Main, SiteLanguageRelation, Languages

from wagtail.wagtailcore.models import Page


@pytest.mark.django_db
@override_settings(GOOGLE_ANALYTICS={})
class TestCopyBulkAction(TestCase, MoloTestCaseMixin):

    def setUp(self):
        # make main one with section and sub section with fr translations
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
        self.yourmind_sub = self.mk_section(
            self.yourmind, title='Your mind subsection')

        self.yourmind_fr = self.mk_section_translation(
            self.yourmind, self.french, title='Your mind in french')
        self.yourmind_sub_fr = self.mk_section_translation(
            self.yourmind_sub, self.french,
            title='Your mind subsection in french')

        # make main 2 with different section to main 1
        self.mk_main2()
        self.main2 = Main.objects.all().last()
        self.language_setting2 = Languages.objects.create(
            site_id=self.main2.get_site().pk)
        self.english2 = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting2,
            locale='en',
            is_active=True)
        self.yourmind2 = self.mk_section(
            self.section_index2, title='Your mind2')
        self.yourmind_sub2 = self.mk_section(
            self.yourmind2, title='Your mind subsection2')

        # create main 3 with nothing
        self.mk_main2(title='main3', slug='main3', path='4099')
        self.main3_pk = Page.objects.get(title='main3').pk
        self.main3 = Main.objects.all().last()

    def test_copy_to_all(self):
        # assert main 3 has translation languages
        self.assertFalse(
            Languages.for_site(
                self.main3.get_site()).languages.filter(locale='fr').exists())

        # create articles in main 1
        article = self.mk_articles(self.yourmind, 1)[0]
        self.mk_article_translation(article, self.french)
        self.mk_section_translation(self.yourmind, self.french)
        self.user = self.login()

        # create that same article in main 2 but under a different section
        self.mk_articles(self.yourmind2, 1)[0]

        # copy the section with the article to all the sites
        self.client.post(reverse('copy-to-all', args=(self.yourmind.id,)))

        # it should copy that section to main 2 still with the same article
        self.assertTrue(Page.objects.child_of(
            self.section_index2).filter(slug=self.yourmind.slug).exists())
        self.assertEquals(
            Page.objects.child_of(self.section_index2).count(), 3)

        # main 3 should only have one article with the original slug
        self.assertEquals(Page.objects.descendant_of(
            self.main3).filter(slug=article.slug).count(), 1)

        # main 3 should have the opied section
        self.assertTrue(Page.objects.descendant_of(
            self.main3).filter(slug=self.yourmind.slug).exists())

        # test that it copies the language over as well
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
