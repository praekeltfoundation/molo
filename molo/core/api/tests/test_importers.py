"""
Test the importing module.
This module relies heavily on an external service and requires
quite a bit of mocking.
"""
import os
import pytest
from django.test import TestCase
from mock import patch

from molo.core.api import importers
from molo.core.api.errors import (
    RecordOverwriteError,
    ReferenceUnimportedContent,
)
from molo.core.api.tests import constants, utils
from molo.core.models import (
    ArticlePage,
    SectionPage,
    FooterPage,
    BannerPage,
    Tag,
    ArticlePageRecommendedSections,
    ArticlePageRelatedSections,
    SiteLanguageRelation,
    ArticlePageTags,
    SectionPageTags,
)
from molo.core.tests.base import MoloTestCaseMixin
from molo.core.utils import get_image_hash

import responses

from wagtail.wagtailcore.models import Site
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


class TestBaseImporter(MoloTestCaseMixin, TestCase):
    def setUp(self):
        self.fake_base_url = "http://localhost:8000"
        self.mk_main()
        self.importer = importers.BaseImporter(self.site.pk,
                                               self.fake_base_url)

    def test_format_base_url(self):
        self.fake_base_url = "http://localhost:8000/"
        base_importer = importers.BaseImporter(self.site.pk,
                                               self.fake_base_url)
        self.assertEqual(base_importer.base_url, self.fake_base_url[:-1])


class TestImageSectionImporter(MoloTestCaseMixin, TestCase):
    def setUp(self):
        self.fake_base_url = "http://localhost:8000"
        self.mk_main()
        self.record_keeper = importers.RecordKeeper()
        self.importer = importers.ImageImporter(
            self.site.pk, self.fake_base_url,
            record_keeper=self.record_keeper)

    def test_image_importer_init(self):
        self.assertEqual(self.importer.image_url,
                         "http://localhost:8000/api/v2/images/")

    def test_get_image_details(self):
        local_image = Image.objects.create(
            title='local image',
            file=get_test_image_file(),
        )
        local_image_hash = get_image_hash(local_image)

        importer = importers.ImageImporter(self.site.pk,
                                           self.fake_base_url)

        self.assertEqual(importer.image_hashes[local_image_hash], local_image)
        self.assertEqual(
            importer.image_widths[local_image.width], [local_image])
        self.assertEqual(
            importer.image_heights[local_image.height], [local_image])

    def test_get_replica_image_returns_match(self):
        local_image = Image.objects.create(
            title='local image',
            file=get_test_image_file(),
        )
        local_image_hash = get_image_hash(local_image)
        self.assertEqual(Image.objects.count(), 1)
        self.importer.get_image_details()

        replica_image = self.importer.get_replica_image(
            local_image.width, local_image.height, local_image_hash)
        self.assertEqual(replica_image, local_image)

    def test_get_replica_image_returns_none(self):
        local_image = Image.objects.create(
            title='local image',
            file=get_test_image_file(),
        )
        local_image_hash = get_image_hash(local_image)
        self.importer.get_image_details()

        replica_image = self.importer.get_replica_image(
            local_image.width + 1, local_image.height, local_image_hash)
        self.assertTrue(replica_image is None)

        replica_image = self.importer.get_replica_image(
            local_image.width, local_image.height + 1, local_image_hash)
        self.assertTrue(replica_image is None)

        replica_image = self.importer.get_replica_image(
            local_image.width, local_image.height, 'fake_hash')
        self.assertTrue(replica_image is None)

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
    def test_import_image_raise_exception(self):
        image_url = '{}/api/v2/images/'.format(self.fake_base_url)
        image_detail_url_1 = "{}{}/".format(image_url,
                                            constants.IMAGE_DETAIL_1["id"])
        responses.add(
            responses.GET, image_detail_url_1,
            json=constants.IMAGE_DETAIL_1_NO_HASH, status=200)
        with pytest.raises(ValueError) as exception_info:
            self.importer.import_image(
                constants.IMAGE_LIST_RESPONSE["items"][0]["id"])
        self.assertEqual(
            exception_info.value.__str__(),
            'image hash should not be none')

    @responses.activate
    @patch("molo.core.api.importers.ImageImporter.fetch_and_create_image",
           side_effect=utils.mocked_fetch_and_create_image)
    def test_import_image(self, mock_fetch_and_create_image):
        image_url = '{}/api/v2/images/'.format(self.fake_base_url)
        foreign_image_id = constants.IMAGE_DETAIL_2["id"]
        image_detail_url_2 = "{}{}/".format(image_url, foreign_image_id)

        responses.add(
            responses.GET, image_detail_url_2,
            json=constants.IMAGE_DETAIL_2, status=200)

        self.assertEqual(Image.objects.count(), 0)

        local_image = self.importer.import_image(
            constants.IMAGE_DETAIL_2["id"])

        self.assertEqual(Image.objects.count(), 1)

        # check that record has been created
        self.assertEqual(
            self.record_keeper.get_local_image(foreign_image_id),
            local_image.id)

    @responses.activate
    def test_import_image_avoid_duplicates(self):
        image_url = '{}/api/v2/images/'.format(self.fake_base_url)
        foreign_image_id = constants.IMAGE_DETAIL_1["id"]
        image_detail_url_1 = "{}{}/".format(image_url, foreign_image_id)

        responses.add(
            responses.GET, image_detail_url_1,
            json=constants.IMAGE_DETAIL_1, status=200)

        # create 'duplicate' image with same name
        Image.objects.create(
            title='local image',
            file=get_test_image_file(constants.IMAGE_DETAIL_1["id"]),
        )
        # NOTE: images must be re-referenced once added
        self.importer.get_image_details()
        self.assertEqual(Image.objects.count(), 1)

        local_image = self.importer.import_image(
            constants.IMAGE_DETAIL_1["id"])

        self.assertEqual(Image.objects.count(), 1)

        # check logs
        self.assertEqual(
            self.record_keeper.get_local_image(foreign_image_id),
            local_image.id)

    @responses.activate
    @patch("molo.core.api.importers.ImageImporter.fetch_and_create_image",
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

        # check logs
        self.assertEqual(
            self.record_keeper.get_local_image(constants.IMAGE_DETAIL_1["id"]),
            Image.objects.first().id)
        self.assertEqual(
            self.record_keeper.get_local_image(constants.IMAGE_DETAIL_2["id"]),
            Image.objects.last().id)


class TestLanguageImporter(MoloTestCaseMixin, TestCase):
    def setUp(self):
        self.fake_base_url = "http://localhost:8000"
        self.mk_main()
        self.importer = importers.LanguageImporter(self.site.pk,
                                                   self.fake_base_url)

    def test_language_importer_init(self):
        self.assertEqual(self.importer.language_url,
                         "http://localhost:8000/api/v2/languages/")

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


class TestContentImporter(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.fake_base_url = "http://localhost:8000"
        self.mk_main()
        self.record_keeper = importers.RecordKeeper()
        self.importer = importers.ContentImporter(
            self.site.pk, self.fake_base_url,
            record_keeper=self.record_keeper)

    def test_attach_page(self):
        parent = self.section_index
        content = constants.SECTION_PAGE_RESPONSE
        content_copy = dict(content)

        result = self.importer.attach_page(
            self.section_index,
            content_copy)

        self.assertTrue(isinstance(result, SectionPage))
        self.assertEqual(
            self.section_index.get_children()[0].title,
            content["title"])

    def test_attach_translated_content(self):
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

        index = self.section_index
        parent = self.mk_section(index)

        self.assertEqual(ArticlePage.objects.count(), 0)

        article = self.importer.attach_page(parent, content_copy)

        self.assertEqual(ArticlePage.objects.count(), 1)

        translated_article = self.importer.attach_translated_content(
            article, content_for_translated_copy, "fr")

        self.assertEqual(ArticlePage.objects.count(), 2)
        site = Site.objects.get(pk=self.importer.site_pk)
        self.assertEqual(article.get_translation_for(
            "fr", site),
            translated_article)

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

        content = constants.SECTION_PAGE_RESPONSE
        content_for_translated = constants.SECTION_PAGE_RESPONSE_FRENCH
        content_copy = dict(content)
        content_for_translated_copy = dict(content_for_translated)

        parent = self.section_index

        self.assertEqual(SectionPage.objects.count(), 0)

        section = self.importer.attach_page(parent, content_copy)

        self.assertEqual(SectionPage.objects.count(), 1)

        translated_section = self.importer.attach_translated_content(
            section, content_for_translated_copy, "fr")

        self.assertEqual(SectionPage.objects.count(), 2)
        site = Site.objects.get(pk=self.importer.site_pk)
        self.assertEqual(section.get_translation_for(
            "fr", site),
            translated_section)

    @patch("molo.core.api.importers.requests.get",
           side_effect=utils.mocked_requests_get)
    def test_recursive_copy(self, mock_get):
        '''
        This test will copy content with the following structure:
        |--Sections
           |--Section 1 [with French translation]
           |  |--Article 1  [with French translation]
           |  |--Article 2
           |
           |--Section 2
              |--Sub Section
                 |--Article 3
        '''
        # create the extra local language
        self.french = SiteLanguageRelation.objects.create(
            language_setting=self.importer.language_setting,
            locale='fr',
            is_active=True)

        self.assertEqual(SectionPage.objects.count(), 0)
        self.assertEqual(ArticlePage.objects.count(), 0)

        self.importer.copy_children(
            foreign_id=constants.SECTION_INDEX_PAGE_RESPONSE["id"],
            existing_node=self.section_index)

        self.assertEqual(SectionPage.objects.count(), 4)
        self.assertEqual(ArticlePage.objects.count(), 4)

        sec_1 = SectionPage.objects.get(
            title=constants.SECTION_RESPONSE_1["title"])
        self.assertTrue(sec_1)
        self.assertEqual(sec_1.get_parent().specific, self.section_index)
        self.assertEqual(sec_1.get_children().count(), 3)

        sec_1_trans = SectionPage.objects.get(
            title=constants.SECTION_RESPONSE_1_TRANSLATION_1["title"])
        self.assertTrue(sec_1_trans)
        self.assertEqual(sec_1_trans.get_parent().specific, self.section_index)
        self.assertEqual(sec_1_trans.get_children().count(), 0)

        sec_2 = SectionPage.objects.get(
            title=constants.SECTION_RESPONSE_2["title"])
        self.assertTrue(sec_2)
        self.assertEqual(sec_2.get_parent().specific, self.section_index)
        self.assertEqual(sec_2.get_children().count(), 1)

        sec_3 = SectionPage.objects.get(
            title=constants.SUB_SECTION_RESPONSE_1["title"])
        self.assertTrue(sec_3)
        self.assertEqual(sec_3.get_parent().specific, sec_2)
        self.assertEqual(sec_3.get_children().count(), 1)

        art_1 = ArticlePage.objects.get(
            title=constants.ARTICLE_RESPONSE_1["title"])
        self.assertTrue(art_1)
        self.assertTrue(art_1.get_parent().specific, sec_1)

        art_1_trans = ArticlePage.objects.get(
            title=constants.ARTICLE_RESPONSE_1_TRANSLATION["title"])
        self.assertTrue(art_1_trans)
        self.assertTrue(art_1_trans.get_parent().specific, sec_1)

        art_2 = ArticlePage.objects.get(
            title=constants.ARTICLE_RESPONSE_2["title"])
        self.assertTrue(art_2)
        self.assertTrue(art_2.get_parent().specific, sec_1)

        art_3 = ArticlePage.objects.get(
            title=constants.NESTED_ARTICLE_RESPONSE["title"])
        self.assertTrue(art_3)
        self.assertTrue(art_3.get_parent().specific, sec_3)

class TestRecordKeeper(TestCase):
    def setUp(self):
        self.record_keeper = importers.RecordKeeper()

    def test_record_keeper_record_local_id(self):
        self.record_keeper.record_page_relation(1, 2)
        self.assertEqual(self.record_keeper.id_map[1], 2)

    def test_record_keeper_record_local_id_exception(self):
        self.record_keeper.id_map[1] = 2
        with pytest.raises(RecordOverwriteError) as exception_info:
            self.record_keeper.record_page_relation(1, 6)
        self.assertEqual(
            exception_info.value.__str__(),
            "RecordOverwriteError")

    def test_record_keeper_get_local_id(self):
        self.record_keeper.id_map[1] = 2
        self.assertEqual(
            self.record_keeper.get_local_page(1), 2)

    def test_record_keeper_get_local_id_exception(self):
        with pytest.raises(ReferenceUnimportedContent) as exception_info:
            self.record_keeper.get_local_page(1)
        self.assertEqual(
            exception_info.value.__str__(),
            "ReferenceUnimportedContent")
