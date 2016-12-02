from django.contrib.auth.models import User
from django.test import TestCase
from django.core.urlresolvers import reverse

from mock import patch

from molo.core.api.tests.utils import mocked_requests_get
from molo.core.tests.base import MoloTestCaseMixin


class MainImportViewTestCase(MoloTestCaseMixin, TestCase):

    def setUp(self):
        self.mk_main()
        User.objects.create_superuser(
            username="admin", email="admin@admin.com", password="admin"
        )
        self.client.login(username="admin", password="admin")

    def test_raises_error_if_data_not_available(self):
        form_data = {
            "url": "http://localhost:8000/api/v2/pages/",
            "content_type": "core.ArticlePage"
        }
        response = self.client.post(
            reverse("molo_api:main-import"),
            data=form_data,
        )
        self.assertFormError(
            response, "form", "url", [u"Please enter a valid URL."]
        )

    @patch("molo.core.api.forms.requests.get", side_effect=mocked_requests_get)
    def test_redirects_to_parent_chooser(self, mock_get):
        form_data = {
            "url": "http://localhost:8000/api/v2/pages/",
            "content_type": "core.ArticlePage"
        }
        response = self.client.post(
            reverse("molo_api:main-import"),
            data=form_data,
        )
        self.assertEqual(response.status_code, 302)
