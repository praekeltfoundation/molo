from django.test import TestCase
import pytest


@pytest.mark.django_db
class TestPages(TestCase):
    fixtures = ['molo/core/tests/fixtures/test.json']

    def test_breadcrumbs(self):
        response = self.client.get('')
        assert response.status_code == 200
        assert 'Home' not in response.content

        response = self.client.get('/english/your-mind/')
        assert response.status_code == 200
        assert '<span class="active">Your Mind</span>' in response.content

        response = self.client.get('/english/your-mind/another-story/')
        assert response.status_code == 200
        assert (
            '<span class="active">This is another story</span>'
            in response.content)
