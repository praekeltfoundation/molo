from django.test import TestCase

from molo.core.blocks import MarkDownBlock


class TestMarkDownBlock(TestCase):
    def test_get_api_rep_converts_html_to_markdown(self):
        # Test with some commonly used html tags
        block = MarkDownBlock()
        self.assertEqual(
            block.get_api_representation(value="<b>Hello</b> There!"),
            "__Hello__ There!")
        self.assertEqual(
            block.get_api_representation(value="<b>**Hello**</b> There!"),
            "__Hello__ There!")
        self.assertEqual(
            block.get_api_representation(value="<p>Hello\nThere!</p>"),
            "Hello There!")
        self.assertEqual(
            block.get_api_representation(value="**Hello**<br/>There!"),
            "__Hello__  \nThere!")
        self.assertEqual(
            block.get_api_representation(value="<u>Hello</u> There!"),
            "Hello There!")
        self.assertEqual(
            block.get_api_representation(
                value="<ul><li>Hello</li>\n<li>There!</li></ul>"),
            "*   Hello\n *   There!")
        self.assertEqual(
            block.get_api_representation(
                value="<p>Hello</p>\n\n<p>There!</p>"),
            "Hello\n\nThere!")
        self.assertEqual(
            block.get_api_representation(value='<a href="Hello">There!</a>'),
            "[There!](Hello)")
        self.assertEqual(
            block.get_api_representation(value="<em>#Hello There!</em>"),
            "_#Hello There!_")
