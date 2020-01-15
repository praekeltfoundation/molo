# -*- coding: UTF-8 -*-
import csv
import pytz
import tempfile
from datetime import datetime
from django.core.management import call_command
from django.test import TestCase
from molo.core.tests.base import MoloTestCaseMixin
from molo.core.models import (
    Main, Languages, ArticlePage, Tag, ArticlePageTags, SiteLanguageRelation,
    SiteLanguage, LanguageRelation, SectionPage, PageTranslation)


class ManagementCommandsTest(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(self.main.get_site()),
            locale='en',
            is_active=True)
        self.spanish = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(self.main.get_site()),
            locale='sp',
            is_active=True)
        self.french = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(self.main.get_site()),
            locale='fr',
            is_active=True)
        self.yourmind = self.mk_section(
            self.section_index, title='Your mind')
        self.article = ArticlePage(title='Test Article', slug='test-article')
        self.yourmind.add_child(instance=self.article)
        self.article.save_revision().publish()

    def test_switch_main_language(self):
        tag = Tag(title='love', slug='love')
        self.tag_index.add_child(instance=tag)
        tag.save_revision().publish()
        kw = dict(language__is_main_language=True)
        for relation in LanguageRelation.objects.filter(**kw):
            self.assertEqual(relation.language.locale, 'en')
        self.assertTrue(self.english.is_main_language)
        call_command('switch_main_language', 'id')
        self.assertTrue(SiteLanguage.objects.get(locale='id').is_main_language)
        self.assertFalse(
            LanguageRelation.objects.filter(language__locale='en').exists())
        for relation in LanguageRelation.objects.filter(**kw):
            self.assertEqual(relation.language.locale, 'id')

    def test_add_language_to_pages(self):
        call_command('add_language_to_pages')
        english = SiteLanguage.objects.first()
        article = ArticlePage.objects.get(pk=self.article.pk)
        yourmind = SectionPage.objects.get(pk=self.yourmind.pk)
        self.assertEqual(article.language, english)
        self.assertEqual(yourmind.language, english)

    def test_add_translated_pages_to_pages(self):
        self.mk_main2()
        self.main2 = Main.objects.all().last()
        self.language_setting2 = Languages.objects.create(
            site_id=self.main2.get_site().pk)
        self.english2 = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting2,
            locale='en',
            is_active=True)

        self.spanish2 = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting2,
            locale='es',
            is_active=True)
        self.yourmind2 = self.mk_section(
            self.section_index2, title='Your mind')
        # create article in english with translation in spanish and french
        english_article = self.article
        spanish_article = self.mk_article_translation(
            english_article, self.spanish)
        french_article = self.mk_article_translation(
            english_article, self.french)
        PageTranslation.objects.create(
            page=english_article, translated_page=english_article)

        # create section in english with translations
        english_section = self.yourmind
        english_section2 = self.yourmind2
        spanish_section = self.mk_section_translation(
            self.yourmind, self.spanish)
        spanish_section2 = self.mk_section_translation(
            self.yourmind2, self.spanish2)
        french_section = self.mk_section_translation(
            self.yourmind, self.french)

        # need to delete it here since it gets added in base
        for article in ArticlePage.objects.all():
            article.translated_pages.clear()
            article.save()
        for section in SectionPage.objects.all():
            section.translated_pages.clear()
            section.save()
        self.assertFalse(english_article.translated_pages.exists())
        self.assertFalse(spanish_article.translated_pages.exists())
        self.assertFalse(french_article.translated_pages.exists())
        self.assertFalse(english_section.translated_pages.exists())
        self.assertFalse(english_section2.translated_pages.exists())
        self.assertFalse(spanish_section.translated_pages.exists())
        self.assertFalse(spanish_section2.translated_pages.exists())
        self.assertFalse(french_section.translated_pages.exists())

        # run command to add languages to these pages
        call_command('add_language_to_pages')

        # run command to add list of translated_pages to these pages
        call_command('add_translated_pages_to_pages')

        # test translated pages for articles
        self.assertTrue(english_article.translated_pages.filter(
            pk=spanish_article.pk).exists())
        self.assertTrue(english_article.translated_pages.filter(
            pk=french_article.pk).exists())
        self.assertFalse(english_article.translated_pages.filter(
            pk=english_article.pk).exists())
        self.assertTrue(spanish_article.translated_pages.filter(
            pk=english_article.pk).exists())
        self.assertTrue(spanish_article.translated_pages.filter(
            pk=french_article.pk).exists())
        self.assertFalse(spanish_article.translated_pages.filter(
            pk=spanish_article.pk).exists())
        self.assertTrue(french_article.translated_pages.filter(
            pk=english_article.pk).exists())
        self.assertTrue(french_article.translated_pages.filter(
            pk=spanish_article.pk).exists())

        # test translated pages for sections
        self.assertTrue(english_section.translated_pages.filter(
            pk=spanish_section.pk).exists())
        self.assertTrue(english_section2.translated_pages.filter(
            pk=spanish_section2.pk).exists())
        self.assertTrue(english_section.translated_pages.filter(
            pk=french_section.pk).exists())
        self.assertTrue(spanish_section.translated_pages.filter(
            pk=english_section.pk).exists())
        self.assertTrue(spanish_section2.translated_pages.filter(
            pk=english_section2.pk).exists())
        self.assertTrue(spanish_section.translated_pages.filter(
            pk=french_section.pk).exists())
        self.assertTrue(french_section.translated_pages.filter(
            pk=english_section.pk).exists())
        self.assertTrue(french_section.translated_pages.filter(
            pk=spanish_section.pk).exists())

    def test_add_feature_in_latest_date_to_article(self):
        self.assertEqual(self.article.featured_in_latest_start_date, None)
        now = datetime.now()
        now = pytz.utc.localize(now)

        # create the csv file with the article slug and date
        data = {
            self.article.slug: now
        }
        fake_namefile = tempfile.NamedTemporaryFile()
        with open(fake_namefile.name, 'w') as fake_csv:
            writer = csv.writer(fake_csv)
            writer.writerow(['slug', 'date'])
            for key, value in data.items():
                writer.writerow([key, value])
        # call the command
        call_command('set_promotional_dates_from_csv', fake_namefile.name)
        self.assertEqual(
            ArticlePage.objects.last().featured_in_latest_start_date, now)
        fake_namefile.close()

    def test_add_tag_to_article(self):
        self.assertEqual(ArticlePageTags.objects.count(), 0)
        # create the tag data
        tag = Tag(title='over 18', slug='over-18')
        self.tag_index.add_child(instance=tag)
        tag.save_revision().publish()
        tag_data = {
            self.article.slug: tag.title
        }

        # create csv
        fake_namefile = tempfile.NamedTemporaryFile()
        with open(fake_namefile.name, 'w') as fake_csv:
            writer = csv.writer(fake_csv)
            writer.writerow(['slug', 'date'])
            for key, value in tag_data.items():
                writer.writerow([key, value])

        # call command to link tag to article
        call_command(
            'add_tag_to_article', fake_csv.name, 'en')

        # it should create a Article Relationship with the Tag
        self.assertEqual(ArticlePageTags.objects.count(), 1)
        self.assertEqual(
            ArticlePageTags.objects.first().tag.title, tag.title)
        self.assertEqual(
            ArticlePageTags.objects.first().page, self.article)

        fake_namefile.close()
