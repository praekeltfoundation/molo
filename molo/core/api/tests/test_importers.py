"""
Test the importing module.
This module relies heavily on an external service and requires
quite a bit of mocking.
"""
import os
import pytest
from django.conf import settings
from django.test import TestCase, override_settings
from mock import patch

from molo.core.api import importers
from molo.core.api.errors import (
    RecordOverwriteError,
    ReferenceUnimportedContent,
    ImportedContentInvalid,
)
from molo.core.api.tests import constants, utils
from molo.core.models import (
    ArticlePage,
    SectionPage,
    ArticlePageRecommendedSections,
    ArticlePageRelatedSections,
    SiteLanguageRelation,
    ArticlePageTags,
    SectionPageTags,
    BannerPage,
    get_translation_for
)
from molo.core.tests.base import MoloTestCaseMixin
from molo.core.utils import get_image_hash

import responses

from wagtail.core.models import Site
from wagtail.images.tests.utils import Image, get_test_image_file


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


@override_settings(MEDIA_ROOT=os.path.join(settings.PROJECT_ROOT, 'media'))
@override_settings(
    DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
class TestImageImporter(MoloTestCaseMixin, TestCase):
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

    def test_get_replica_image_returns_match(self):
        local_image = Image.objects.create(
            title='local image',
            file=get_test_image_file(),
        )
        local_image_hash = get_image_hash(local_image)
        self.assertEqual(Image.objects.count(), 1)
        self.importer.get_image_details()

        replica_image = self.importer.get_replica_image(local_image_hash)
        self.assertEqual(replica_image, local_image)

    def test_get_replica_image_returns_none(self):
        Image.objects.create(
            title='local image',
            file=get_test_image_file(),
        )
        self.importer.get_image_details()

        replica_image = self.importer.get_replica_image('wrong_hash')
        self.assertTrue(replica_image is None)

    @responses.activate
    def test_fetch_and_create_image_new_image(self):
        image_title = "test_title.png"
        url = "{}/media/images/SIbomiWV1AQ.original.jpg".format(
            self.fake_base_url)
        test_file_path = os.getcwd() + '/molo/core/api/tests/test_image.png'

        with open(test_file_path, 'rb') as img1:
            responses.add(
                responses.GET, url,
                body=img1.read(), status=200,
                content_type='image/jpeg',
                stream=True
            )
        result, context = self.importer.fetch_and_create_image(
            url,
            image_title)

        self.assertEqual(type(result), Image)
        self.assertEqual(result.title, image_title)
        self.assertEqual(Image.objects.count(), 1)

        self.assertEqual(
            context["file_url"],
            url)

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
        image_file_location = constants.IMAGE_DETAIL_2["image_url"]

        responses.add(
            responses.GET, image_detail_url_2,
            json=constants.IMAGE_DETAIL_2, status=200)

        self.assertEqual(Image.objects.count(), 0)

        new_image, context = self.importer.import_image(
            constants.IMAGE_DETAIL_2["id"])

        self.assertEqual(Image.objects.count(), 1)
        self.assertEqual(
            new_image.title,
            constants.IMAGE_DETAIL_2["title"])

        # Check returned context
        self.assertFalse(context["local_version_existed"])

        # check that record has been created
        self.assertEqual(
            context['file_url'],
            "{}{}".format(self.fake_base_url, image_file_location))

    @responses.activate
    def test_import_image_avoid_duplicates(self):
        image_url = '{}/api/v2/images/'.format(self.fake_base_url)
        foreign_image_id = constants.IMAGE_DETAIL_1["id"]
        image_detail_url_1 = "{}{}/".format(image_url, foreign_image_id)
        image_file_location = constants.IMAGE_DETAIL_1["image_url"]

        responses.add(
            responses.GET, image_detail_url_1,
            json=constants.IMAGE_DETAIL_1, status=200)

        # create 'duplicate' image with same name
        Image.objects.create(
            title='local image',
            file=get_test_image_file(),
        )
        # NOTE: images must be re-referenced once added
        self.importer.get_image_details()
        self.assertEqual(Image.objects.count(), 1)

        local_image, context = self.importer.import_image(
            constants.IMAGE_DETAIL_1["id"])

        self.assertEqual(Image.objects.count(), 1)

        # Check context
        self.assertTrue(context["local_version_existed"])
        self.assertEqual(
            context["file_url"],
            "{}{}".format(self.fake_base_url, image_file_location))
        self.assertEqual(
            context["foreign_title"],
            constants.IMAGE_DETAIL_1["title"])

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
        self.logger = importers.Logger()
        self.importer = importers.ContentImporter(
            self.site.pk, self.fake_base_url,
            record_keeper=self.record_keeper,
            logger=self.logger)

    def test_attach_page(self):
        content = utils.fake_section_page_response(image=None)
        content_copy = dict(content)

        result = self.importer.attach_page(
            self.section_index,
            content_copy)

        self.assertTrue(isinstance(result, SectionPage))
        # an empty logger means no errors were created
        # during page creation
        self.assertEqual(self.logger.record, [])
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
        self.assertEqual(get_translation_for(
            [article],
            "fr", site)[0],
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
        self.assertEqual(get_translation_for(
            [section],
            "fr", site)[0],
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

    def test_create_recommended_articles(self):
        section = self.mk_section(
            self.section_index, title="Parent Test Section 1",
        )
        # create 2 articles
        self.mk_articles(section)
        article_main = ArticlePage.objects.first()
        article_rec = ArticlePage.objects.last()

        # update map_id
        # attach imaginary foreign IDs to articles, to fake import data
        self.record_keeper.foreign_local_map["page_map"] = {
            111: article_main.id, 222: article_rec.id}

        # refer copied page to foreign id of recomended article
        self.record_keeper.foreign_to_many_foreign_map["recommended_articles"][111] = [222]  # noqa

        self.assertEqual(ArticlePageRecommendedSections.objects.count(), 0)

        # recreate importer with updated record_keeper
        self.importer = importers.ContentImporter(
            self.site.pk, self.fake_base_url,
            record_keeper=self.record_keeper)
        self.importer.create_recommended_articles()

        self.assertEqual(ArticlePageRecommendedSections.objects.count(), 1)
        recomendation = ArticlePageRecommendedSections.objects.first()
        self.assertEqual(recomendation.page.specific, article_main)
        self.assertEqual(recomendation.recommended_article.specific,
                         article_rec)

    def test_create_related_sections(self):
        section_main = self.mk_section(
            self.section_index, title="Parent Test Section 1",
        )
        section_rel = self.mk_section(
            self.section_index, title="Parent Test Section 1",
        )
        # create articles
        [parent_section, related_section] = self.mk_sections(section_main)
        article = self.mk_article(parent_section)

        # update map_id
        # attach imaginary foreign IDs to sections, to fake import data
        self.record_keeper.foreign_local_map["page_map"] = {
            111: section_main.id,
            222: section_rel.id,
            333: article.id}
        # refer copied page to foreign id of related section
        self.record_keeper.foreign_to_many_foreign_map["related_sections"][333] = [222]  # noqa

        self.assertEqual(ArticlePageRelatedSections.objects.count(), 0)
        self.importer.create_related_sections()
        self.assertEqual(ArticlePageRelatedSections.objects.count(), 1)
        relation = ArticlePageRelatedSections.objects.first()
        self.assertEqual(relation.page.specific, article)
        self.assertEqual(relation.section.specific,
                         section_rel)

    def test_create_nav_tag_relationships(self):
        '''
        Check creation of ArticlePageTags, which are called nav_tags in model
        '''
        section = self.mk_section(
            self.section_index, title="Parent Test Section 1",
        )
        article = self.mk_article(section)

        # create tag
        [tag_1, tag_2] = self.mk_tags(self.tag_index, count=2)

        # update map_id
        # attach imaginary foreign IDs to sections, to fake import data
        self.record_keeper.foreign_local_map["page_map"] = {
            111: tag_1.id, 222: tag_2.id, 333: article.id}
        self.record_keeper.foreign_to_many_foreign_map["nav_tags"][333] = [111, 222]  # noqa

        self.assertEqual(ArticlePageTags.objects.count(), 0)
        self.importer.create_nav_tag_relationships()
        self.assertEqual(ArticlePageTags.objects.count(), 2)

        [relation_1, relation_2] = list(ArticlePageTags.objects.all())

        self.assertEqual(relation_1.page.specific, article)
        self.assertEqual(relation_1.tag.specific,
                         tag_1)

        self.assertEqual(relation_2.page.specific, article)
        self.assertEqual(relation_2.tag.specific,
                         tag_2)

    def test_create_section_tag_relationships(self):
        section = self.mk_section(self.section_index)

        # create tag
        [tag_1, tag_2] = self.mk_tags(self.tag_index, count=2)

        # update map_id
        # attach imaginary foreign IDs to sections, to fake import data
        self.record_keeper.foreign_local_map["page_map"] = {
            111: tag_1.id, 222: tag_2.id, 333: section.id}
        self.record_keeper.foreign_to_many_foreign_map["section_tags"][333] = [111, 222]  # noqa

        self.assertEqual(SectionPageTags.objects.count(), 0)
        self.importer.create_section_tag_relationship()
        self.assertEqual(SectionPageTags.objects.count(), 2)

        [relation_1, relation_2] = list(SectionPageTags.objects.all())

        self.assertEqual(relation_1.page.specific, section)
        self.assertEqual(relation_1.tag.specific,
                         tag_1)

        self.assertEqual(relation_2.page.specific, section)
        self.assertEqual(relation_2.tag.specific,
                         tag_2)

    def test_create_banner_page_links(self):
        banner = self.mk_banner(parent=self.banner_index)
        section = self.mk_section(parent=self.section_index)
        # fake the banner page data
        self.record_keeper.foreign_local_map["page_map"] = {
            111: section.id, 222: banner.id}
        self.record_keeper.foreign_to_foreign_map["banner_link_page"][222] = 111   # noqa

        self.assertFalse(banner.banner_link_page)

        self.importer.create_banner_page_links()

        banner = BannerPage.objects.get(id=banner.id)
        self.assertTrue(banner.banner_link_page)
        self.assertEqual(banner.banner_link_page.specific, section)

    def test_recreate_article_body(self):
        # assumptions

        # image reference in body has been imported
        # page reference in body has been imported
        # article created without body
        # record_keeper has this ^ info

        section = self.mk_section(self.section_index)
        article = self.mk_article(section)
        article.body = None
        article.save()
        article_id = article.id

        self.assertFalse(article.body)

        body = constants.ARTICLE_PAGE_RESPONSE_STREAM_FIELDS["body"]

        self.record_keeper.foreign_local_map["page_map"] = {
            48: section.id,  # page linked to in article body
            999: article.id  # article page with body
        }

        foreign_image_id = 297
        image = Image.objects.create(
            title="fake_image",
            file=get_test_image_file(),
        )

        self.record_keeper.foreign_local_map["image_map"] = {
            foreign_image_id: image.id}

        self.record_keeper.article_bodies = {999: body}

        self.importer.recreate_article_body()

        updated_article = ArticlePage.objects.get(id=article_id)

        self.assertTrue(updated_article)
        self.assertTrue(updated_article.body)
        # TODO: check each field individually


class TestRecordKeeper(TestCase):
    def setUp(self):
        self.record_keeper = importers.RecordKeeper()

    def test_record_keeper_record_local_id(self):
        self.record_keeper.record_page_relation(1, 2)
        self.assertEqual(
            self.record_keeper.foreign_local_map["page_map"][1], 2)

    def test_record_keeper_record_local_id_exception(self):
        self.record_keeper.foreign_local_map["page_map"][1] = 2
        with pytest.raises(RecordOverwriteError) as exception_info:
            self.record_keeper.record_page_relation(1, 6)
        self.assertEqual(
            exception_info.value.__str__(),
            "RecordOverwriteError")

    def test_record_keeper_get_local_id(self):
        self.record_keeper.record_page_relation(1, 2)
        self.assertEqual(
            self.record_keeper.get_local_page(1), 2)

    def test_record_keeper_get_local_id_exception(self):
        fake_id = 1
        with pytest.raises(ReferenceUnimportedContent) as exception_info:
            self.record_keeper.get_local_page(fake_id)
        self.assertEqual(
            exception_info.value.__str__(),
            "Unimported content foreign ID: {}".format(fake_id))

    def test_record_nav_tags_with_none(self):
        '''
        wagtail allows pages to be created without a link page
        Test that this case does not cause an error and
        '''
        nested_fields = constants.NESTED_FIELD_NAV_TAG_WITH_NONE
        fake_page_id = 99

        self.record_keeper.record_nav_tags(nested_fields, fake_page_id)

        self.assertTrue(True)

    def test_record_keeper_throws_content_error(self):
        fake_page_id = 9999
        nested_fields = {
            "recommended_articles": [{
                "id": 1,
                "meta": {
                    "type": "core.ArticlePageRecommendedSections"
                },
                "recommended_article": {
                    "i_d": 27,
                    "meta": {
                        "type": "core.ArticlePage",
                        "detail_url": "http://localhost:8000/api/v2/pages/27/"
                    },
                    "title": "Article that is nested"
                }
            }],
        }

        with pytest.raises(ImportedContentInvalid) as exception_info:
            self.record_keeper.record_recommended_articles(
                nested_fields, fake_page_id)
        self.assertEqual(
            exception_info.value.__str__(),
            ("key of 'id' does not exist in related_item of"
             " type: recommended_article")
        )

    def test_record_keeper_throws_content_error2(self):
        fake_page_id = 9999
        nested_fields = {
            "recommended_articles": [{
                "id": 1,
                "meta": {
                    "type": "core.ArticlePageRecommendedSections"
                },
                "REKKOMMENDED_ARTICLE": {  # corrupted field
                    "id": 27,
                    "meta": {
                        "type": "core.ArticlePage",
                        "detail_url": "http://localhost:8000/api/v2/pages/27/"
                    },
                    "title": "Article that is nested"
                }
            }],
        }

        with pytest.raises(ImportedContentInvalid) as exception_info:
            self.record_keeper.record_recommended_articles(nested_fields,
                                                           fake_page_id)
        self.assertEqual(
            exception_info.value.__str__(),
            ("key of 'recommended_article' does not exist in "
             "nested_field of type: recommended_articles")
        )


class TestLogger(TestCase):
    def setUp(self):
        self.logger = importers.Logger()

        self.action_log_args = {
            "log_type": importers.ACTION,
            "message": "action_log_args",
            "context": {
                "foo": "bar",
                "baz": "bonk",
            },
        }

        self.error_log_args = {
            "log_type": importers.ERROR,
            "message": "error_log_args",
            "context": {
                "noo": "boo",
                "can": "haz",
            },
        }

        self.warning_log_args = {
            "log_type": importers.WARNING,
            "message": "warning_log_args",
            "context": {
                "blu": "red",
                "grn": "ylw",
            },
        }

    def test_log(self):

        self.logger.log(**self.action_log_args)

        self.assertEqual(self.logger.record[0], self.action_log_args)

        self.logger.log(**self.error_log_args)

        self.assertEqual(self.logger.record[0], self.action_log_args)
        self.assertEqual(self.logger.record[1], self.error_log_args)

    def test_get_email_logs(self):
        self.logger.record.append(self.error_log_args)
        result = self.logger.get_email_logs()

        # Note that content, not formatting, is being tested
        self.assertTrue(importers.ERROR in result)
        self.assertTrue(self.error_log_args["message"] in result)
        self.assertTrue(self.error_log_args["context"]["noo"] in result)

        self.logger.record.append(self.warning_log_args)
        result = self.logger.get_email_logs()

        self.assertTrue(importers.WARNING in result)
        self.assertTrue(self.warning_log_args["message"] in result)
        self.assertTrue(self.warning_log_args["context"]["blu"] in result)

    def test_get_email_logs_only_errors_warnings(self):
        self.logger.record.append(self.action_log_args)

        result = self.logger.get_email_logs()

        self.assertEqual(result, "")
