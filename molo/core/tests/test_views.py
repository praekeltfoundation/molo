from django.test import TestCase
import pytest


@pytest.mark.django_db
class TestPages(TestCase):
    fixtures = ['molo/core/tests/fixtures/test.json']

    def test_breadcrumbs(self):
        response = self.client.get('/')
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

    def test_section_listing(self):
        response = self.client.get('/')
        assert 'About a girl' in response.content
        assert 'about a boy' in response.content
        assert (
            '<a href="/english/your-mind/another-story/">'
            '<img src="/media/images/f5edfca6af2e4410b029864a2da149fd'
            '.focus-none.width-60.jpeg" width="60" height="39" alt="2 girls">'
            '</a>' in response.content)

    def test_article_page(self):
        response = self.client.get('/english/your-mind/another-story/')
        assert (
            '<span class="active">This is another story</span>'
            in response.content)
        assert 'About a girl' in response.content
