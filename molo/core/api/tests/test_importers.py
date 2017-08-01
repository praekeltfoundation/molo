"""
Test the importing module.
This module relies heavily on an external service and requires
quite a bit of mocking.
"""
import os
from django.test import TestCase
from mock import patch

from molo.core.api import importers
from molo.core.api.tests import constants, utils
from molo.core.models import (
    ArticlePage,
    SectionPage,
    SiteLanguageRelation,
)
from molo.core.tests.base import MoloTestCaseMixin

import responses

from wagtail.wagtailimages.tests.utils import Image, get_test_image_file

from dateutil import parser


class ArticleImportTestCase(MoloTestCaseMixin, TestCase):

    def setUp(self):
        self.mk_main()
        self.importer = importers.ArticlePageImporter(
            base_url="http://localhost:8000",
            content=constants.AVAILABLE_ARTICLES["items"]
        )

    def test_article_importer_initializtion(self):
        self.assertEqual(
            self.importer.content(),
            constants.AVAILABLE_ARTICLES["items"]
        )

    @patch("molo.core.api.importers.get_image")
    def test_articles_can_be_saved(self, mock_image):
        image = Image.objects.create(
            title="Test image",
            file=get_test_image_file(),
        )
        mock_image.return_value = image

        # Create parent page to which articles will be saved
        section = self.mk_section(
            self.section_index, title="Parent Test Section 2",
        )
        self.assertEqual(ArticlePage.objects.all().count(), 0)

        # Save the articles
        # Save the first available article
        # import pdb;pdb.set_trace()
        self.importer.save([0, ], section.id)
        self.assertEqual(ArticlePage.objects.all().count(), 1)

    def test_nested_fields_can_be_extracted(self):
        # It is necessary to separate nested fields in each article
        # dictionary from those that are not nested. Reason being
        # some of the nested fields have to be treated differently.
        pass

    @patch("molo.core.api.importers.get_image")
    def test_related_image_can_be_retrieved(self, mock_image):
        mock_image.return_value = constants.RELATED_IMAGE
        # assert 0
        # self.assertIsInstance(
        #     importers.get_image(base_url=self.importer.base_url, image_id=1),
        #     Image
        # )

    def tearDown(self):
        del self.importer


class SectionImportTestCase(MoloTestCaseMixin, TestCase):

    def setUp(self):
        self.mk_main()
        self.importer = importers.SectionPageImporter(
            base_url="http://localhost:8000",
            content=constants.AVAILABLE_SECTIONS["items"]
        )

    def test_section_importer_initializtion(self):
        self.assertEqual(
            self.importer.content(),
            constants.AVAILABLE_SECTIONS["items"]
        )

    def tearDown(self):
        del self.importer

    # @patch("molo.core.api.importers.get_image")
    # def test_section_can_be_saved(self, mock_image):
    #     image = Image.objects.create(
    #         title="Test image",
    #         file=get_test_image_file(),
    #     )
    #     mock_image.return_value = image
    #
    #     # Add new sections as children pf the SectionIndexPage
    #     self.assertEqual(SectionPage.objects.all().count(), 0)
    #
    #     # Save the articles
    #     # Save the first available article
    #     self.importer.save([0, ], self.section_index.id)
    #     self.assertEqual(SectionPage.objects.all().count(), 1)


class TestImporterUtilFunctions(TestCase):
    def setUp(self):
        self.test_url = "http://localhost:8000/api/v2/images/"

    @responses.activate
    def test_list_of_objects_from_api(self):
        responses.add(responses.GET,
                      self.test_url,
                      json=constants.WAGTAIL_API_LIST_VIEW, status=200)
        returned_list = importers.list_of_objects_from_api(self.test_url)
        self.assertEqual(
            returned_list,
            constants.WAGTAIL_API_LIST_VIEW["items"])

    @patch("molo.core.api.importers.requests.get",
           side_effect=utils.mocked_requests_get)
    def test_list_of_objects_from_api_paginated(self, mock_get):
        responses.add(responses.GET,
                      self.test_url,
                      json=constants.WAGTAIL_API_LIST_VIEW_PAGE_1, status=200)
        responses.add(responses.GET,
                      "{}?limit=20&offset=20".format(self.test_url),
                      json=constants.WAGTAIL_API_LIST_VIEW_PAGE_2, status=200)
        returned_list = importers.list_of_objects_from_api(self.test_url)
        expected_response = (
            constants.WAGTAIL_API_LIST_VIEW_PAGE_1["items"] +
            constants.WAGTAIL_API_LIST_VIEW_PAGE_2["items"]
        )
        self.assertEqual(
            returned_list,
            expected_response)


class TestSiteSectionImporter(MoloTestCaseMixin, TestCase):
    def setUp(self):
        self.fake_base_url = "http://localhost:8000"
        self.mk_main()
        self.importer = importers.SiteImporter(self.site.pk,
                                               self.fake_base_url)

    @responses.activate
    def test_get_language_ids(self):
        responses.add(responses.GET,
                      "{}/api/v2/languages/".format(self.fake_base_url),
                      json=constants.LANGUAGE_LIST_RESPONSE, status=200)
        self.assertEqual(
            self.importer.get_language_ids(),
            [constants.LANGUAGE_LIST_RESPONSE["items"][0]["id"],
             constants.LANGUAGE_LIST_RESPONSE["items"][1]["id"]])

    @responses.activate
    def test_copy_site_languages(self):
        responses.add(responses.GET,
                      "{}/api/v2/languages/".format(self.fake_base_url),
                      json=constants.LANGUAGE_LIST_RESPONSE, status=200)
        responses.add(responses.GET,
                      "{}/api/v2/languages/1/".format(self.fake_base_url),
                      json=constants.LANGUAGE_RESPONSE_1, status=200)
        responses.add(responses.GET,
                      "{}/api/v2/languages/2/".format(self.fake_base_url),
                      json=constants.LANGUAGE_RESPONSE_2, status=200)

        self.importer.copy_site_languages()

        eng_lang = SiteLanguageRelation.objects.get(locale="en")
        fr_lang = SiteLanguageRelation.objects.get(locale="fr")

        self.assertTrue(eng_lang)
        self.assertTrue(eng_lang.is_active)
        self.assertTrue(eng_lang.is_main_language)

        self.assertTrue(fr_lang)
        self.assertTrue(fr_lang.is_active)
        self.assertFalse(fr_lang.is_main_language)

    @responses.activate
    def test_fetch_and_create_image_new_image(self):
        image_title = "test_title.png"
        relative_url = "/media/images/SIbomiWV1AQ.original.jpg"
        test_file_path = os.getcwd() + '/molo/core/api/tests/test_image.png'

        with open(test_file_path, 'rb') as img1:
            responses.add(
                responses.GET, '{}{}'.format(self.fake_base_url, relative_url),
                body=img1.read(), status=200,
                content_type='image/jpeg',
                stream=True
            )
        result = self.importer.fetch_and_create_image(
            relative_url,
            image_title)

        self.assertEqual(type(result), Image)
        self.assertEqual(result.title, image_title)
        self.assertEqual(Image.objects.count(), 1)

    @responses.activate
    @patch("molo.core.api.importers.SiteImporter.fetch_and_create_image",
           side_effect=utils.mocked_fetch_and_create_image)
    def test_import_images(self, mock_fetch_and_create_image):
        image_list_url = '{}/api/v2/images/'.format(self.fake_base_url)
        image_detail_url_1 = "{}{}/".format(image_list_url,
                                            constants.IMAGE_DETAIL_1["id"])
        image_detail_url_2 = "{}{}/".format(image_list_url,
                                            constants.IMAGE_DETAIL_2["id"])
        responses.add(
            responses.GET, image_list_url,
            json=constants.IMAGE_LIST_RESPONSE, status=200)
        responses.add(
            responses.GET, image_detail_url_1,
            json=constants.IMAGE_DETAIL_1, status=200)
        responses.add(
            responses.GET, image_detail_url_2,
            json=constants.IMAGE_DETAIL_2, status=200)

        self.assertEqual(Image.objects.count(), 0)

        self.importer.import_images()

        self.assertEqual(Image.objects.count(), 2)
        self.assertEqual(
            Image.objects.first().title,
            constants.IMAGE_DETAIL_1["title"])
        self.assertEqual(
            Image.objects.last().title,
            constants.IMAGE_DETAIL_2["title"])

        # check that image mapping from foreign to local exists
        self.assertEqual(
            self.importer.image_map[constants.IMAGE_DETAIL_1["id"]],
            Image.objects.first().id)
        self.assertEqual(
            self.importer.image_map[constants.IMAGE_DETAIL_2["id"]],
            Image.objects.last().id)

    @responses.activate
    @patch("molo.core.api.importers.SiteImporter.fetch_and_create_image",
           side_effect=utils.mocked_fetch_and_create_image)
    def test_import_images_avoid_duplicates(self, mock_fetch_and_create_image):
        image_list_url = '{}/api/v2/images/'.format(self.fake_base_url)
        image_detail_url_1 = "{}{}/".format(image_list_url,
                                            constants.IMAGE_DETAIL_1["id"])
        image_detail_url_2 = "{}{}/".format(image_list_url,
                                            constants.IMAGE_DETAIL_2["id"])
        responses.add(
            responses.GET, image_list_url,
            json=constants.IMAGE_LIST_RESPONSE, status=200)
        responses.add(
            responses.GET, image_detail_url_1,
            json=constants.IMAGE_DETAIL_1, status=200)
        responses.add(
            responses.GET, image_detail_url_2,
            json=constants.IMAGE_DETAIL_2, status=200)

        # create 'duplicate' image with same name
        Image.objects.create(
            title='local image',
            file=get_test_image_file(),
        )
        self.assertEqual(Image.objects.count(), 1)

        self.importer.import_images()

        self.assertEqual(Image.objects.count(), 2)
        # Note that local title is used over foreign title
        self.assertEqual(
            Image.objects.first().title,
            'local image')
        self.assertEqual(
            Image.objects.last().title,
            constants.IMAGE_DETAIL_2["title"])

        # check that image mapping from foreign to local exists
        self.assertEqual(
            self.importer.image_map[constants.IMAGE_DETAIL_1["id"]],
            Image.objects.first().id)
        self.assertEqual(
            self.importer.image_map[constants.IMAGE_DETAIL_2["id"]],
            Image.objects.last().id)

    def test_create_article_page(self):
        # fake the content passed to the importer
        content = utils.fake_article_page_response()

        # create local versions of images, mapped to foreign ID
        foreign_image_id = content["image"]["id"]
        image = Image.objects.create(
            title=content["image"]["title"],
            file=get_test_image_file(),
        )
        self.importer.image_map[foreign_image_id] = image.id

        foreign_social_media_image_id = content["social_media_image"]["id"]
        social_media_image = Image.objects.create(
            title=content["social_media_image"]["title"],
            file=get_test_image_file(),
        )

        (self.importer
             .image_map[foreign_social_media_image_id]) = social_media_image.id

        # avoid any side effects by creating a copy of content
        content_copy = dict(content)

        parent = self.mk_section(self.section_index)

        self.assertEqual(ArticlePage.objects.count(), 0)

        article = self.importer.create_page(parent, content_copy)

        self.assertEqual(ArticlePage.objects.count(), 1)
        self.assertEqual(article.get_parent(), parent)
        self.assertNotEqual(article.id, content["id"])

        # FLAT FIELDS
        self.assertEqual(article.title, content["title"])
        self.assertEqual(article.subtitle, content["subtitle"])
        self.assertEqual(article.commenting_state, content["commenting_state"])
        self.assertEqual(article.social_media_title,
                         content["social_media_title"])
        self.assertEqual(article.social_media_description,
                         content["social_media_description"])
        self.assertEqual(article.featured_in_latest,
                         content["featured_in_latest"])
        self.assertEqual(article.featured_in_section,
                         content["featured_in_section"])
        self.assertEqual(article.featured_in_homepage,
                         content["featured_in_homepage"])
        self.assertEqual(article.feature_as_topic_of_the_day,
                         content["feature_as_topic_of_the_day"])

        self.assertEqual(article.commenting_open_time,
                         parser.parse(content["commenting_open_time"]))
        self.assertEqual(article.commenting_close_time,
                         parser.parse(content["commenting_close_time"]))
        self.assertEqual(article.featured_in_latest_start_date,
                         parser.parse(
                             content["featured_in_latest_start_date"]))
        self.assertEqual(article.featured_in_latest_end_date,
                         parser.parse(content["featured_in_latest_end_date"]))
        self.assertEqual(article.featured_in_section_start_date,
                         parser.parse(
                             content["featured_in_section_start_date"]))
        self.assertEqual(article.featured_in_section_end_date,
                         parser.parse(content["featured_in_section_end_date"]))
        self.assertEqual(article.featured_in_homepage_start_date,
                         parser.parse(
                             content["featured_in_homepage_start_date"]))
        self.assertEqual(article.featured_in_homepage_end_date,
                         parser.parse(
                             content["featured_in_homepage_end_date"]))
        self.assertEqual(article.promote_date,
                         parser.parse(content["promote_date"]))
        self.assertEqual(article.demote_date,
                         parser.parse(content["demote_date"]))

        # NESTED FIELDS
        self.assertTrue(hasattr(article.body, "stream_data"))
        self.assertEqual(article.body.stream_data, content['body'])

        self.assertEqual(article.tags.count(), len(content['tags']))
        for tag in article.tags.all():
            self.assertTrue(tag.name in content["tags"])

        self.assertEqual(article.metadata_tags.count(),
                         len(content['metadata_tags']))
        for metadata_tag in article.metadata_tags.all():
            self.assertTrue(metadata_tag.name in content["metadata_tags"])

        # Check that all reference fields have been properly stored
        # for further processing later

        # nav_tags
        self.assertEqual(self.importer.id_map[content["id"]], article.id)
        self.assertTrue(article.id in self.importer.nav_tags)
        self.assertEqual(self.importer.nav_tags[article.id],
                         [content["nav_tags"][0]["tag"]["id"], ])
        # TODO
        # self.assertEqual(self.importer.image_map[article.id], [])

        self.assertTrue(article.id in self.importer.related_sections)
        self.assertEqual(
            self.importer.related_sections[article.id],
            [content["related_sections"][0]["section"]["id"],
             content["related_sections"][1]["section"]["id"]])

        self.assertTrue(article.id in self.importer.recommended_articles)
        self.assertEqual(
            self.importer.recommended_articles[article.id],
            [content["recommended_articles"][0]["recommended_article"]["id"],
             content["recommended_articles"][1]["recommended_article"]["id"]])

        self.assertTrue(article.id in self.importer.reaction_questions)
        self.assertEqual(
            self.importer.reaction_questions[article.id],
            [content["reaction_questions"][0]["reaction_question"]["id"],
             content["reaction_questions"][1]["reaction_question"]["id"]])

        # Check that image file has been added
        self.assertTrue(article.image)
        self.assertEqual(article.image.title, content["image"]["title"])
        # Check that social media file has been added
        self.assertTrue(article.social_media_image)
        self.assertEqual(article.social_media_image.title,
                         content["social_media_image"]["title"])

    def test_create_section_page(self):
        # fake the content passed to the importer
        content = utils.fake_section_page_response()

        # create local versions of images, mapped to foreign ID
        foreign_image_id = content["image"]["id"]
        image = Image.objects.create(
            title=content["image"]["title"],
            file=get_test_image_file(),
        )
        self.importer.image_map[foreign_image_id] = image.id

        # avoid any side effects by creating a copy of content
        content_copy = dict(content)

        parent = self.section_index

        self.assertEqual(SectionPage.objects.count(), 0)

        section = self.importer.create_page(parent, content_copy)

        self.assertEqual(section.get_parent(), parent)
        self.assertNotEqual(section.id, content["id"])

        # TODO test live attribute
        self.assertEqual(section.title, content["title"])
        self.assertEqual(section.description, content["description"])
        self.assertEqual(section.extra_style_hints,
                         content["extra_style_hints"])
        self.assertEqual(section.commenting_state, content["commenting_state"])
        self.assertEqual(section.monday_rotation, content["monday_rotation"])
        self.assertEqual(section.tuesday_rotation, content["tuesday_rotation"])
        self.assertEqual(section.wednesday_rotation,
                         content["wednesday_rotation"])
        self.assertEqual(section.thursday_rotation,
                         content["thursday_rotation"])
        self.assertEqual(section.friday_rotation, content["friday_rotation"])
        self.assertEqual(section.saturday_rotation,
                         content["saturday_rotation"])
        self.assertEqual(section.sunday_rotation, content["sunday_rotation"])

        self.assertEqual(section.commenting_open_time,
                         parser.parse(content["commenting_open_time"]))
        self.assertEqual(section.commenting_close_time,
                         parser.parse(content["commenting_close_time"]))
        self.assertEqual(section.content_rotation_start_date,
                         parser.parse(content["content_rotation_start_date"]))
        self.assertEqual(section.content_rotation_end_date,
                         parser.parse(content["content_rotation_end_date"]))

        # NESTED FIELDS
        # time
        self.assertTrue(hasattr(section.time, "stream_data"))
        self.assertEqual(section.time.stream_data, content["time"])

        # section_tags/nav_tags
        self.assertEqual(self.importer.id_map[content["id"]], section.id)
        self.assertTrue(section.id in self.importer.section_tags)
        self.assertEqual(self.importer.section_tags[section.id],
                         [content["section_tags"][0]["tag"]["id"],
                          content["section_tags"][1]["tag"]["id"]])
        # Check that image file has been added
        self.assertTrue(section.image)
        self.assertEqual(section.image.title, content["image"]["title"])

    def test_create_section_page_translated(self):
        # create 2 languages
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.importer.language_setting,
            locale='en',
            is_active=True)
        self.french = SiteLanguageRelation.objects.create(
            language_setting=self.importer.language_setting,
            locale='fr',
            is_active=True)

        content = constants.ARTICLE_PAGE_RESPONSE_MAIN_LANG
        content_for_translated = constants.ARTICLE_PAGE_RESPONSE_FRENCH
        content_copy = dict(content)
        content_for_translated_copy = dict(content_for_translated)

        parent = self.section_index

        self.assertEqual(ArticlePage.objects.count(), 0)

        article = self.importer.create_page(parent, content_copy)

        self.assertEqual(ArticlePage.objects.count(), 1)

        translated_article = self.importer.create_translated_content(
            article, content_for_translated_copy, "fr")

        self.assertEqual(ArticlePage.objects.count(), 2)
        self.assertEqual(article.get_translation_for(
            "fr", self.importer.site),
            translated_article)
