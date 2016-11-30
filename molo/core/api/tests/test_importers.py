"""
Test the importing module.
This module relies heavily on an external service and requires
quite a bit of mocking.
"""
import json

from django.test import TestCase

from molo.core.tests.base import MoloTestCaseMixin
from molo.core.api import importers
from molo.core.api.tests import constants


class ArticleImportTestCase(MoloTestCaseMixin, TestCase):

    def setUp(self):
        self.mk_main()
        self.importer = importers.ArticlePageImporter(
            content=constants.AVAILABLE_ARTICLES
        )

    def test_importer_initializtion(self):
        self.assertEqual(
            self.importer.articles(),
            constants.AVAILABLE_ARTICLES
        )

    def test_articles_can_be_saved(self):
        pass

    def test_nested_fields_can_be_extracted(self):
        pass

    def test_related_image_can_be_retrieved(self):
        pass
