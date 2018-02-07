# -*- coding: UTF-8 -*-
import csv
import pytz
import tempfile
from datetime import datetime
from django.core.management import call_command
from django.test import TestCase
from django.utils.six import StringIO
from molo.core.tests.base import MoloTestCaseMixin
from molo.core.models import (
    Main, Languages, ArticlePage, Tag, ArticlePageTags, SiteLanguageRelation)


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
        self.yourmind = self.mk_section(
            self.section_index, title='Your mind')
        self.article = ArticlePage(title='Test Article', slug='test-article')
        self.yourmind.add_child(instance=self.article)
        self.article.save_revision().publish()

    def test_add_feature_in_latest_date_to_article(self):
        self.assertEquals(self.article.featured_in_latest_start_date, None)
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
        out = StringIO()
        call_command(
            'set_promotional_dates_from_csv', fake_namefile.name, std_out=out)
        self.assertEquals(
            ArticlePage.objects.last().featured_in_latest_start_date, now)
        fake_namefile.close()

    def test_add_tag_to_article(self):
        self.assertEquals(ArticlePageTags.objects.count(), 0)
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
        out = StringIO()
        call_command(
            'add_tag_to_article', fake_csv.name, 'en',
            std_out=out)

        # it should create a Article Relationship with the Tag
        self.assertEquals(ArticlePageTags.objects.count(), 1)
        self.assertEquals(
            ArticlePageTags.objects.first().tag.title, tag.title)
        self.assertEquals(
            ArticlePageTags.objects.first().page, self.article)

        fake_namefile.close()
