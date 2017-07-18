import requests
from mock import patch
import json

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.core.urlresolvers import reverse

# from wagtail.wagtailimages.tests.utils import get_test_image_file, Image

from molo.core.api.tests.utils import mocked_requests_get
from molo.core.tests.base import MoloTestCaseMixin
from molo.core.models import (
    Main,
    Languages,
    SiteLanguageRelation,
    # ArticlePage,
)


class APIMoloTestCase(MoloTestCaseMixin, TestCase):
    def setUp(self):
        self.mk_main()
        self.client = Client()

        self.main = Main.objects.all().first()
        self.english = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(self.main.get_site()),
            locale='en',
            is_active=True)
        self.english_section = self.mk_section(
            self.section_index, title='English section')
        self.mk_article(self.english_section)

        User.objects.create_superuser(
            username="admin", email="admin@admin.com", password="admin"
        )
        self.client.login(username="admin", password="admin")


class MainImportViewTestCase(APIMoloTestCase):

    @patch(
        "molo.core.api.forms.requests.get",
        side_effect=requests.ConnectionError
    )
    def test_raises_error_if_data_not_available(self, mock_get):
        form_data = {
            "url": "http://localhost:8000/api/v2/pages/",
            "content_type": "core.ArticlePage"
        }
        response = self.client.post(
            reverse("molo_api:main-import"),
            data=form_data,
            follow=True
        )
        self.assertFormError(
            response, "form", "url", [u"Please enter a valid URL."]
        )

    @patch("molo.core.api.forms.requests.get", side_effect=mocked_requests_get)
    def test_redirects_to_parent_chooser(self, mock_get):
        form_data = {
            "url": "http://localhost:8000/",
            "content_type": "core.ArticlePage"
        }
        response = self.client.post(
            reverse("molo_api:main-import"),
            data=form_data,
            follow=True
        )
        self.assertContains(response, "Add Article")


class ArticleParentChooserTestCase(APIMoloTestCase):

    def test_redirects_to_first_page_if_session_not_set(self):
        response = self.client.get(reverse("molo_api:article-parent-chooser"))
        self.assertEqual(
            response["Location"],
            reverse("molo_api:main-import")
        )


class ArticleImportViewTestCase(APIMoloTestCase):

    def test_redirects_to_main_page_if_session_not_set(self):
        response = self.client.get(
            reverse("molo_api:article-import"),
            follow=True
        )
        url, status_code = response.redirect_chain[-1]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(url, reverse("molo_api:main-import"))

    @patch("molo.core.api.forms.requests.get", side_effect=mocked_requests_get)
    def test_redirect_to_article_chooser_if_session_not_set(self, mock_get):
        form_data = {
            "url": "http://localhost:8000/",
            "content_type": "core.ArticlePage"
        }
        response = self.client.post(
            reverse("molo_api:main-import"),
            data=form_data,
            follow=True
        )
        url, status_code = response.redirect_chain[-1]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(url, reverse("molo_api:article-parent-chooser"))

        # Try to go to the next step of the session before choosing a
        # parent page
        response = self.client.get(reverse("molo_api:article-import"))
        self.assertEqual(
            response["Location"],
            reverse("molo_api:article-parent-chooser")
        )

    # @patch("molo.core.api.importers.requests.get",
    #        side_effect=mocked_requests_get)
    # @patch("molo.core.api.forms.requests.get",
    #        side_effect=mocked_requests_get)
    # @patch("molo.core.api.importers.get_image")
    # def test_articles_can_be_imported(
    #         self, mock_image, mock_get, mock_importer_get
    # ):
    #     initial_article_number = ArticlePage.objects.count()
    #     image = Image.objects.create(
    #         title="Test image",
    #         file=get_test_image_file(),
    #     )
    #     mock_image.return_value = image

    #     # Choose URL and content type on article import first step
    #     form_data = {
    #         "url": "http://localhost:8000/",
    #         "content_type": "core.ArticlePage"
    #     }
    #     response = self.client.post(
    #         reverse("molo_api:main-import"),
    #         data=form_data,
    #         follow=True
    #     )
    #     url, status_code = response.redirect_chain[-1]
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(url, reverse("molo_api:article-parent-chooser"))

    #     # Select a parent for the articles that will be imported
    #     parent = self.mk_section(
    #         self.section_index,
    #         title="Test Parent Section For import"
    #     )
    #     form_data = {
    #         "parent_page": parent.id,
    #     }
    #     response = self.client.post(
    #         reverse("molo_api:article-parent-chooser"),
    #         data=form_data,
    #         follow=True
    #     )
    #     url, status_code = response.redirect_chain[-1]
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(url, reverse("molo_api:article-import"))

    #     # Select the articles that will be saved
    #     form_data = {
    #         "0": True,
    #         "1": False,
    #         "2": True,
    #     }
    #     response = self.client.post(
    #         reverse("molo_api:article-import"),
    #         data=form_data,
    #         follow=True
    #     )

    #     # The articles should be saved, check them in the DB
    #     self.assertEqual(
    #         ArticlePage.objects.all().count(),
    #         initial_article_number + 2)


class SectionParentChooserTestCase(APIMoloTestCase):

    def test_session_redirects_to_first_page_if_session_not_set(self):
        response = self.client.get(reverse("molo_api:section-parent-chooser"))
        self.assertEqual(
            response["Location"],
            reverse("molo_api:main-import")
        )

    @patch("molo.core.api.forms.requests.get", side_effect=mocked_requests_get)
    def test_redirect_to_section_chooser_if_session_not_set(self, mock_get):
        form_data = {
            "url": "http://localhost:8000/",
            "content_type": "core.SectionPage"
        }
        response = self.client.post(
            reverse("molo_api:main-import"),
            data=form_data,
            follow=True
        )
        url, status_code = response.redirect_chain[-1]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(url, reverse("molo_api:section-parent-chooser"))

        # Try to go to the next step of the session before choosing a
        # parent page
        response = self.client.get(reverse("molo_api:section-import"))
        self.assertEqual(
            response["Location"],
            reverse("molo_api:section-parent-chooser")
        )


class LanguageEndpointTestCase(APIMoloTestCase):
    def test_language_list_view(self):

        api_client = Client()
        url = "/api/v2/languages/"
        response = api_client.get(url)

        self.assertEqual(response.status_code, 200)
        obj = json.loads(response.content)['items']

        self.assertEqual(len(obj), 1)

        self.french = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(self.main.get_site()),
            locale='fr',
            is_active=True)

        response = api_client.get(url)
        obj = json.loads(response.content)['items']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(obj), 2)

    def test_language_detail_view(self):
        self.french = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(self.main.get_site()),
            locale='fr',
            is_active=True)

        api_client = Client()
        url = "/api/v2/languages/"

        response = api_client.get("{}{}/".format(url, self.english.id))
        self.assertEqual(response.status_code, 200)
        obj = json.loads(response.content)

        self.assertEqual(obj['locale'], 'en')
        self.assertEqual(obj['is_main_language'], True)
        self.assertEqual(obj['is_active'], True)

        response = api_client.get("{}{}/".format(url, self.french.id))
        self.assertEqual(response.status_code, 200)
        obj = json.loads(response.content)

        self.assertEqual(obj['locale'], 'fr')
        self.assertEqual(obj['is_main_language'], False)
        self.assertEqual(obj['is_active'], True)
