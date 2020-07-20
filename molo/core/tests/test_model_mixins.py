from django.test import TestCase

from wagtail.images.tests.utils import Image, get_test_image_file

from molo.core.models import (
    ArticlePage,
    SectionPage,
    Tag,
    FooterPage,
    BannerPage,
)
from molo.core.api.constants import ERROR
from molo.core.api.tests import constants
from molo.core.api import importers
from molo.core.tests.base import MoloTestCaseMixin


class TestImportableMixin(MoloTestCaseMixin, TestCase):
    def setUp(self):
        self.mk_main()

    def test_tag_importable(self):
        content = constants.TAG_PAGE_RESPONSE
        content_copy = dict(content)
        class_ = Tag

        tag = Tag.create_page(content_copy, class_)

        self.assertEqual(type(tag), Tag)
        self.assertEqual(tag.title, content["title"])
        self.assertEqual(tag.title, content["title"])
        self.assertEqual(tag.feature_in_homepage,
                         content["feature_in_homepage"])
        self.assertEqual(tag.go_live_at, content["go_live_at"])
        self.assertEqual(tag.expire_at, content["expire_at"])
        self.assertEqual(tag.expired, content["expired"])

    def check_article_and_footer_fields(self, page, content, record_keeper):
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
        self.assertEqual(page.feature_as_hero_article,
                         content["feature_as_hero_article"])

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

        # Check that image has been added
        self.assertTrue(page.image)
        self.assertEqual(page.image.title, content["image"]["title"])
        # Check that social media file has been added
        self.assertTrue(page.social_media_image)
        self.assertEqual(page.social_media_image.title,
                         content["social_media_image"]["title"])

        # Check that foreign relationships have been created
        self.assertTrue(content["id"] in
                        record_keeper.foreign_to_many_foreign_map["nav_tags"])
        self.assertEqual((record_keeper.foreign_to_many_foreign_map["nav_tags"]
                          [content["id"]]),
                         [content["nav_tags"][0]["tag"]["id"], ])

        self.assertTrue(
            content["id"] in
            record_keeper.foreign_to_many_foreign_map["recommended_articles"])
        self.assertEqual(
            (record_keeper.foreign_to_many_foreign_map["recommended_articles"]
                [content["id"]]),
            [content["recommended_articles"][0]["recommended_article"]["id"],
             content["recommended_articles"][1]["recommended_article"]["id"]])

        self.assertTrue(
            content["id"] in
            record_keeper.foreign_to_many_foreign_map["related_sections"])
        self.assertEqual(
            (record_keeper.foreign_to_many_foreign_map["related_sections"]
                [content["id"]]),
            [content["related_sections"][0]["section"]["id"],
             content["related_sections"][1]["section"]["id"]])

    def test_article_importable(self):
        content = constants.ARTICLE_PAGE_RESPONSE
        content_copy = dict(content)

        # Validate Assumptions
        #   The images have already been imported
        #   The record keeper has mapped the relationship

        foreign_image_id = content["image"]["id"]
        image = Image.objects.create(
            title=content["image"]["title"],
            file=get_test_image_file(),
        )

        foreign_social_media_image_id = content["social_media_image"]["id"]
        social_media_image = Image.objects.create(
            title=content["social_media_image"]["title"],
            file=get_test_image_file(),
        )

        record_keeper = importers.RecordKeeper()
        record_keeper.record_image_relation(foreign_image_id, image.id)
        record_keeper.record_image_relation(
            foreign_social_media_image_id, social_media_image.id)

        class_ = ArticlePage

        page = ArticlePage.create_page(
            content_copy, class_, record_keeper=record_keeper)

        self.check_article_and_footer_fields(page, content, record_keeper)

    def test_article_body_not_importable(self):
        content = constants.ARTICLE_PAGE_RESPONSE_STREAM_FIELDS
        content_copy = dict(content)

        record_keeper = importers.RecordKeeper()

        class_ = ArticlePage

        page = ArticlePage.create_page(
            content_copy, class_, record_keeper=record_keeper)

        self.assertEqual(page.title, content["title"])
        self.assertFalse(page.body)

        self.assertTrue(content["id"] in record_keeper.article_bodies)
        self.assertEqual(
            record_keeper.article_bodies[content["id"]],
            content["body"])

    def test_section_importable(self):
        content = constants.SECTION_PAGE_RESPONSE
        content_copy = dict(content)

        # Validate Assumptions
        #   The images have already been imported
        #   The record keeper has mapped the relationship

        foreign_image_id = content["image"]["id"]
        image = Image.objects.create(
            title=content["image"]["title"],
            file=get_test_image_file(),
        )

        record_keeper = importers.RecordKeeper()
        record_keeper.record_image_relation(foreign_image_id, image.id)

        class_ = SectionPage

        page = SectionPage.create_page(
            content_copy, class_, record_keeper=record_keeper)

        self.assertEqual(page.title, content["title"])
        self.assertEqual(page.description, content["description"])
        self.assertEqual(page.extra_style_hints,
                         content["extra_style_hints"])
        self.assertEqual(page.commenting_state, content["commenting_state"])
        self.assertEqual(page.monday_rotation, content["monday_rotation"])
        self.assertEqual(page.tuesday_rotation, content["tuesday_rotation"])
        self.assertEqual(page.wednesday_rotation,
                         content["wednesday_rotation"])
        self.assertEqual(page.thursday_rotation,
                         content["thursday_rotation"])
        self.assertEqual(page.friday_rotation, content["friday_rotation"])
        self.assertEqual(page.saturday_rotation,
                         content["saturday_rotation"])
        self.assertEqual(page.sunday_rotation, content["sunday_rotation"])

        self.assertEqual(page.commenting_open_time,
                         content["commenting_open_time"])
        self.assertEqual(page.commenting_close_time,
                         content["commenting_close_time"])
        self.assertEqual(page.content_rotation_start_date,
                         content["content_rotation_start_date"])
        self.assertEqual(page.content_rotation_end_date,
                         content["content_rotation_end_date"])

        # NESTED FIELDS
        self.assertTrue(hasattr(page.time, "stream_data"))
        self.assertEqual(page.time.stream_data, content["time"])

        # Check that image has been added
        self.assertTrue(page.image)
        self.assertEqual(page.image.title, content["image"]["title"])

        # Check that foreign relationships have been created
        self.assertTrue(
            content["id"] in
            record_keeper.foreign_to_many_foreign_map["section_tags"])
        self.assertEqual(
            (record_keeper.foreign_to_many_foreign_map["section_tags"]
                [content["id"]]),
            [content["section_tags"][0]["tag"]["id"],
             content["section_tags"][1]["tag"]["id"]])

    def test_footer_importable(self):
        content = constants.ARTICLE_PAGE_RESPONSE
        content_copy = dict(content)

        # Validate Assumptions
        #   The images have already been imported
        #   The record keeper has mapped the relationship

        foreign_image_id = content["image"]["id"]
        image = Image.objects.create(
            title=content["image"]["title"],
            file=get_test_image_file(),
        )

        foreign_social_media_image_id = content["social_media_image"]["id"]
        social_media_image = Image.objects.create(
            title=content["social_media_image"]["title"],
            file=get_test_image_file(),
        )

        record_keeper = importers.RecordKeeper()
        record_keeper.record_image_relation(foreign_image_id, image.id)
        record_keeper.record_image_relation(
            foreign_social_media_image_id, social_media_image.id)

        class_ = FooterPage

        page = FooterPage.create_page(
            content_copy, class_, record_keeper=record_keeper)

        self.check_article_and_footer_fields(page, content, record_keeper)

    def test_banner_importable(self):
        content = constants.BANNER_PAGE_RESPONSE
        content_copy = dict(content)

        # Validate Assumptions
        #   The images have already been imported
        #   The record keeper has mapped the relationship

        foreign_image_id = content["banner"]["id"]
        image = Image.objects.create(
            title=content["banner"]["title"],
            file=get_test_image_file(),
        )

        record_keeper = importers.RecordKeeper()
        record_keeper.record_image_relation(foreign_image_id, image.id)

        class_ = BannerPage

        page = BannerPage.create_page(
            content_copy, class_, record_keeper=record_keeper)

        self.assertEqual(page.title, content["title"])
        self.assertEqual(page.external_link, content["external_link"])

        # check that banner link has been created
        self.assertEqual(
            (record_keeper.foreign_to_foreign_map["banner_link_page"]
                [content["id"]]),
            content["banner_link_page"]["id"])

        # check that banner image has been attached
        self.assertTrue(page.banner)
        self.assertEqual(page.banner, image)
        self.assertEqual(page.banner.title, content["banner"]["title"])

    def test_image_not_imported_logs_error(self):
        content = constants.ARTICLE_WITH_ONLY_IMAGE_RESPONSE
        content_copy = dict(content)

        # Break the assumptions that the images have already
        # been imported thus the record keeper has mapped
        # the relationship

        record_keeper = importers.RecordKeeper()
        logger = importers.Logger()

        class_ = ArticlePage

        ArticlePage.create_page(
            content_copy, class_,
            record_keeper=record_keeper,
            logger=logger)

        self.assertTrue(len(logger.record), 1)
        error_log = logger.record[0]
        self.assertEqual(error_log["log_type"], ERROR)
