from django.test import TestCase

from molo.core.tests.base import MoloTestCaseMixin
from molo.core.management.commands.move_page_links_to_recomended_articles import convert_articles  # noqa

body = [
    {
        "type": "paragraph",
        "value": "paragraph 1"
    },
    {
        "type": "page",
        "value": 48
    },
    {
        "type": "paragraph",
        "value": "paragraph 1"
    },
]


class TestCommands(MoloTestCaseMixin, TestCase):
    '''
    Test Cases:
    - page links to RA
    - end page links only
    - existing Recommended Articles
    '''
    def setUp(self):
        self.mk_main()

    def test_convert_articles(self):
        convert_articles()
