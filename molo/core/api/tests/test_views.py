from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.core.urlresolvers import reverse

from mock import patch

from molo.core.api.tests.utils import mocked_requests_get
from molo.core.tests.base import MoloTestCaseMixin


class MainImportViewTestCase(MoloTestCaseMixin, TestCase):

    def setUp(self):
        self.mk_main()
        self.client = Client()
        User.objects.create_superuser(
            username="admin", email="admin@admin.com", password="admin"
        )
        self.client.login(username="admin", password="admin")

    # def test_raises_error_if_data_not_available(self):
    #     form_data = {
    #         "url": "http://localhost:8000/api/v2/pages/",
    #         "content_type": "core.ArticlePage"
    #     }
    #     response = self.client.post(
    #         reverse("molo_api:main-import"),
    #         data=form_data,
    #         follow=True
    #     )
    #     self.assertFormError(
    #         response, "form", "url", [u"Please enter a valid URL."]
    #     )

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


class ArticleParentChooserTestCase(MoloTestCaseMixin, TestCase):

    def setUp(self):
        self.mk_main()
        self.client = Client()
        User.objects.create_superuser(
            username="admin", email="admin@admin.com", password="admin"
        )
        self.client.login(username="admin", password="admin")

    def test_redirects_to_first_page_if_session_not_set(self):
        response = self.client.get(reverse("molo_api:article-parent-chooser"))
        self.assertEqual(
            response["Location"],
            reverse("molo_api:main-import")
        )


class ArticleImportViewTestCase(MoloTestCaseMixin, TestCase):

    def setUp(self):
        self.mk_main()
        self.client = Client()
        User.objects.create_superuser(
            username="admin", email="admin@admin.com", password="admin"
        )
        self.client.login(username="admin", password="admin")

    def test_redirects_to_main_page_if_session_not_set(self):
        response = self.client.get(
            reverse("molo_api:article-import"),
            follow=True
        )
        url, status_code = response.redirect_chain[-1]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(url, reverse("molo_api:main-import"))

    @patch("molo.core.api.forms.requests.get", side_effect=mocked_requests_get)
    def test_articles_can_be_imported(self, mock_get):
        # Choose URL and content type on article import first step
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

        # Select a parent for the articles that will be imported
        # parent = self.mk_section(
        #     self.section_index,
        #     title="Test Parent Section For import"
        # )

        # TODO: test that a parent can be chosen

        # TODO: test that an article can be saved
