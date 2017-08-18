from dateutil import parser

from django.test import TestCase

from molo.core.models import (
    ArticlePage,
    Tag,
)
from molo.core.api.tests import constants
from molo.core.tests.base import MoloTestCaseMixin


class TestImportableMixin(MoloTestCaseMixin, TestCase):
    def setUp(self):
        pass

    def test_tag_importable(self):
        content = constants.TAG_PAGE_RESPONSE
        content_copy = dict(content)
        class_ = Tag

        tag = Tag.create_page(content_copy, class_)

        self.assertEqual(type(tag), Tag)
        self.assertEqual(tag.title, content["title"])

    def test_article_importable(self):
        content = constants.ARTICLE_PAGE_RESPONSE
        content_copy = dict(content)
        class_ = ArticlePage

        page = ArticlePage.create_page(content_copy, class_)

        self.assertEqual(page.title, content["title"])
        self.assertEqual(page.subtitle, content["subtitle"])
        self.assertEqual(page.commenting_state, content["commenting_state"])
        self.assertEqual(page.social_media_title,
                         content["social_media_title"])
        self.assertEqual(page.social_media_description,
                         content["social_media_description"])
        self.assertEqual(page.featured_in_latest,
                         content["featured_in_latest"])
        self.assertEqual(page.featured_in_section,
                         content["featured_in_section"])
        self.assertEqual(page.featured_in_homepage,
                         content["featured_in_homepage"])
        self.assertEqual(page.feature_as_topic_of_the_day,
                         content["feature_as_topic_of_the_day"])

        self.assertEqual(page.commenting_open_time,
                        content["commenting_open_time"])
        self.assertEqual(page.commenting_close_time,
                         content["commenting_close_time"])
        self.assertEqual(page.featured_in_latest_start_date,
                         content["featured_in_latest_start_date"])
        self.assertEqual(page.featured_in_latest_end_date,
                         content["featured_in_latest_end_date"])
        self.assertEqual(page.featured_in_section_start_date,
                         content["featured_in_section_start_date"])
        self.assertEqual(page.featured_in_section_end_date,
                         content["featured_in_section_end_date"])
        self.assertEqual(page.featured_in_homepage_start_date,
                         content["featured_in_homepage_start_date"])
        self.assertEqual(page.featured_in_homepage_end_date,
                         content["featured_in_homepage_end_date"])
        self.assertEqual(page.promote_date,
                         content["promote_date"])
        self.assertEqual(page.demote_date,
                         content["demote_date"])

        # NESTED FIELDS
        self.assertTrue(hasattr(page.body, "stream_data"))
        self.assertEqual(page.body.stream_data, content['body'])

        self.assertEqual(page.tags.count(), len(content['tags']))
        for tag in page.tags.all():
            self.assertTrue(tag.name in content["tags"])

        self.assertEqual(page.metadata_tags.count(),
                         len(content['metadata_tags']))
        for metadata_tag in page.metadata_tags.all():
            self.assertTrue(metadata_tag.name in content["metadata_tags"])
