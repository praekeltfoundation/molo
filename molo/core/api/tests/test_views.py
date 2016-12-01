from django.test import TestCase
from django.core.urlresolvers import reverse

from molo.core.tests.base import MoloTestCaseMixin


class MainImportViewTestCase(MoloTestCaseMixin, TestCase):

    def setUp(self):
        self.mk_main()

    def test_specified_url_is_processed(self):
        form_data = {
            "url": "http://localhost:8000/api/v2/pages",
            "content_type": "core.ArticlePage"
        }
        response = self.client.post(
            reverse("molo_api:main-import"),
            data=form_data,
        )
        self.assertEqual(response.status_code, 302)
