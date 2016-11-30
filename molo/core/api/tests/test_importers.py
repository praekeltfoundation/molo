"""
Test the importing module.
This module relies heavily on an external service and requires
quite a bit of mocking.
"""
import json

from django.test import TestCase

from molo.core.tests.base import MoloTestCaseMixin
from molo.core.content_import.api import importers
from molo.core.content_import.api.tests import constants


class ArticleImportTestCase(MoloTestCaseMixin, TestCase):

    def setUp(self):
        self.mk_main()

    def test_importer_initializtion(self):
        content = json.dumps(constants.AVAILABLE_ARTICLES)
        importer = importers.ArticlePageImporter(content=content)