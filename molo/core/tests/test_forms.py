from django.test import TestCase

from molo.core.forms import ArticlePageForm
from molo.core.tests.base import MoloTestCaseMixin


class EditArticlePageTestCase(MoloTestCaseMixin, TestCase):

    def setUp(self):
        self.mk_main()

    def test_topic_of_the_day_not_selected(self):
        form_data = {
            "feature_as_topic_of_the_day": True,
            # 'password': '1234',
            # 'terms_and_conditions': True
        }
        form = ArticlePageForm(
            data=form_data,
        )
        self.assertEqual(form.is_valid(), True)