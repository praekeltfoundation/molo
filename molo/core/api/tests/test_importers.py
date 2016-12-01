"""
Test the importing module.
This module relies heavily on an external service and requires
quite a bit of mocking.
"""

import pytest

from django.test import TestCase

from mock import patch
from wagtail.wagtailimages.tests.utils import Image, get_test_image_file

from molo.core.tests.base import MoloTestCaseMixin
from molo.core.api import importers
from molo.core.api.tests import constants
from molo.core.models import ArticlePage


@pytest.mark.django_db
class ArticleImportTestCase(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.importer = importers.ArticlePageImporter(
            base_url="http://localhost:8000",
            content=constants.AVAILABLE_ARTICLES
        )

    def test_importer_initializtion(self):
        self.assertEqual(
            self.importer.articles(),
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
            self.section_index, title="Parent Test Section",
            slug="parent-test-section"
        )
        self.assertEqual(ArticlePage.objects.all().count(), 0)

        # Save the articles
        # Save the first available article
        self.importer.save_articles([0, ], section.id)
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
