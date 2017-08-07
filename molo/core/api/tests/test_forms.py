import requests
from mock import patch

from django.test import TestCase

from wagtail.wagtailimages.models import Image
from wagtail.wagtailimages.tests.utils import get_test_image_file

from molo.core.tests.base import MoloTestCaseMixin
from molo.core.api import forms, importers
from molo.core.api.constants import MAIN_IMPORT_FORM_MESSAGES
from molo.core.api.tests import constants
from molo.core.api.tests.utils import mocked_requests_get
from molo.core.models import ArticlePage
from molo.core.models import SectionPage  # noqa


class ArticleImportFormTestCase(MoloTestCaseMixin, TestCase):

    def setUp(self):
        self.mk_main()

        # content must be list of articles as received from the API endpoint
        self.importer = importers.ArticlePageImporter(
            base_url="http://localhost:8000",
            content=constants.AVAILABLE_ARTICLES["items"]
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

    def tearDown(self):
        del self.importer


class MainImportFormTestCase(MoloTestCaseMixin, TestCase):

    def setUp(self):
        self.mk_main()

    @patch("molo.core.api.forms.requests.get", side_effect=mocked_requests_get)
    def test_valid_url_is_given(self, mock_get):
        form_data = {
            "url": "http://localhost:8000/api/v2/pages",
            "content_type": "core.ArticlePage"
        }
        form = forms.MainImportForm(
            data=form_data
        )
        self.assertTrue(form.is_valid())

    @patch("molo.core.api.forms.requests.get",
           side_effect=requests.ConnectionError)
    def test_invalid_url_raises_connection_error(self, mock_get):
        form_data = {
            "url": "http://localhost:8000/api/v2/pages",
            "content_type": "core.ArticlePage"
        }
        form = forms.MainImportForm(
            data=form_data
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            [MAIN_IMPORT_FORM_MESSAGES["connection_error"], ],
            form.errors["url"]
        )

    @patch("molo.core.api.forms.requests.get",
           side_effect=requests.RequestException)
    def test_bad_url_raises_requests_error(self, mock_get):
        form_data = {
            "url": "http://localhost:8000/api/v2/pages",
            "content_type": "core.ArticlePage"
        }
        form = forms.MainImportForm(
            data=form_data
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            [MAIN_IMPORT_FORM_MESSAGES["bad_request"], ],
            form.errors["url"]
        )


class SectionImportFormTestCase(MoloTestCaseMixin, TestCase):

    def setUp(self):
        self.mk_main()
        self.importer = importers.SectionPageImporter(
            base_url="http://localhost:8000",
            content=constants.AVAILABLE_SECTIONS["items"]
        )

    def test_sections_render_as_field_choices(self):
        form = forms.SectionImportForm(
            importer=self.importer,
            parent=self.section_index.id
        )
        self.assertEqual(
            len(form.fields),
            len(constants.AVAILABLE_SECTIONS["items"])
        )

    # @patch("molo.core.api.importers.requests.get",
    #        side_effect=mocked_requests_get)
    # @patch("molo.core.api.importers.get_image")
    # def test_selected_section_can_be_saved(self, mock_image, mock_get):
    #     image = Image.objects.create(
    #         title="Test image",
    #         file=get_test_image_file(),
    #     )
    #     mock_image.return_value = image
    #     form_data = {
    #         "2": True,
    #         "3": False,
    #         "4": False,
    #     }
    #     form = forms.SectionImportForm(
    #         data=form_data,
    #         importer=self.importer,
    #         parent=self.section_index.id
    #     )
    #     self.assertTrue(form.is_valid())
    #
    #     # form.save() saves the selected articles and returns the importer
    #     form.save()
    #     self.assertEqual(ArticlePage.objects.all().count(), 1)
    #     self.assertEqual(SectionPage.objects.all().count(), 2)

    def tearDown(self):
        del self.importer
