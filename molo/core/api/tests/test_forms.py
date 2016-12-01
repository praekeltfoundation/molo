from django.test import TestCase

from mock import patch

from wagtail.wagtailimages.models import Image
from wagtail.wagtailimages.tests.utils import get_test_image_file

from molo.core.tests.base import MoloTestCaseMixin
from molo.core.api import forms, importers
from molo.core.api.tests import constants
from molo.core.models import ArticlePage


class ArticleImportFormTestCase(MoloTestCaseMixin, TestCase):

    def setUp(self):
        self.mk_main()
        self.importer = importers.ArticlePageImporter(
            base_url="http://localhost:8000",
            content=constants.AVAILABLE_ARTICLES
        )
        self.section = self.mk_section(
            self.section_index,
            title="Parent Section 1",
        )

    def test_article_render_as_field_choices(self):
        form = forms.ArticleImportForm(
            importer=self.importer,
            parent=self.section.id
        )
        self.assertEqual(
            len(form.fields),
            len(constants.AVAILABLE_ARTICLES["items"])
        )

    @patch("molo.core.api.importers.get_image")
    def test_selected_articles_can_be_saved(self, mock_image):
        image = Image.objects.create(
            title="Test image",
            file=get_test_image_file(),
        )
        mock_image.return_value = image
        form_data = {
            "0": True,
            "1": True,
            "2": False,
        }
        form = forms.ArticleImportForm(
            data=form_data,
            importer=self.importer,
            parent=self.section.id
        )
        self.assertTrue(form.is_valid())

        # form.save() saves the selected articles and returns the importer
        form.save()
        self.assertEqual(ArticlePage.objects.all().count(), 2)
