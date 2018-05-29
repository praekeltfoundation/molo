from django.test import TestCase
from molo.core.scripts.utils import lint_template


class TestTemplateList(TestCase):
    def test_lint_template_file_pass(self):
        self.assertEqual(
            lint_template(
                """{% load i18n %}
                {% trans "translate me" %}
                """
            ),
            []
        )

    def test_lint_template_file_failure(self):
        self.assertEqual(
            lint_template(
                """{% load i18n %}
                <p>translate me</p>
                """
            ),
            ['Can remove i18n without error']
        )

    def test_lint_template_file_syntax_error(self):
        self.assertEqual(
            lint_template(
                """{% oad i18n %}
                <p>come words</p>
                """
            ),
            [("TemplateSyntaxError while parsing template\n"
              "\tInvalid block tag on line 1: 'oad'. Did you forget to "
              "register or load this tag?")]
        )
