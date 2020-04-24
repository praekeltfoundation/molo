from django.core.exceptions import ValidationError
from django.test import TestCase

from molo.core.blocks import MarkDownBlock


class TestMarkDownBlock(TestCase):
    def test_save_block_with_html_value_fails_validation(self):
        block = MarkDownBlock()
        with (self.assertRaisesMessage(ValidationError,
              "Please use MarkDown for formatting text instead of HTML.")):
            block.clean(value="<b>Hello</b> There!")
