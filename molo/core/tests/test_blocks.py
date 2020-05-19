from django.core.exceptions import ValidationError
from django.test import TestCase

from molo.core.blocks import MarkDownBlock


class TestMarkDownBlock(TestCase):
    def test_save_block_with_html_value_fails_validation(self):
        # Test with some commonly used html tags
        block = MarkDownBlock()
        with (self.assertRaisesMessage(ValidationError,
              "Please use MarkDown for formatting text instead of HTML.")):
            block.clean(value="<b>Hello</b> There!")
        with (self.assertRaisesMessage(ValidationError,
              "Please use MarkDown for formatting text instead of HTML.")):
            block.clean(value="<p>Hello There!</p>")
        with (self.assertRaisesMessage(ValidationError,
              "Please use MarkDown for formatting text instead of HTML.")):
            block.clean(value='<a href="">Hello There!</a>')
        with (self.assertRaisesMessage(ValidationError,
              "Please use MarkDown for formatting text instead of HTML.")):
            block.clean(value='<em>Hello There!</em>')
        with (self.assertRaisesMessage(ValidationError,
              "Please use MarkDown for formatting text instead of HTML.")):
            block.clean(value='Hello There!<br>')

        # Test that a commonly used but invalid tag is also caught
        with (self.assertRaisesMessage(ValidationError,
              "Please use MarkDown for formatting text instead of HTML.")):
            block.clean(value="Hello There!</br>")
