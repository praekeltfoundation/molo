from dateutil import parser

from django.test import TestCase

from molo.core.models import (
    ArticlePage,
    Tag,
)
from molo.core.api.tests import constants
from molo.core.tests.base import MoloTestCaseMixin


class ImportableMixin(MoloTestCaseMixin, TestCase):
    def setUp(self):
        pass

    def test_tag_importable(self):
        content = constants.TAG_PAGE_RESPONSE
        content_copy = dict(content)
        class_ = Tag

        tag = Tag.create_page(content_copy, class_)

        self.assertEqual(type(tag), Tag)
        self.assertEqual(tag.title, content["title"])
