from django.test import TestCase
import pytest


@pytest.mark.django_db
class TestPages(TestCase):
    fixtures = ['molo/core/tests/fixtures/test.json']

    def test_breadcrumbs(self):
        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)
        self.assertNotContains(response, 'Home')

        response = self.client.get('/english/your-mind/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, '<span class="active">Your mind</span>')

        response = self.client.get(
            '/english/your-mind/your-mind-subsection/page-1/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(
            response,
            '<span class="active">Page 1</span>')

    def test_section_listing(self):
        response = self.client.get('/')
        self.assertContains(response, 'Your mind')
        self.assertContains(
            response,
            '<a href="/english/your-mind/">Your mind</a>')

    def test_latest_listing(self):
        response = self.client.get('/')
        self.assertContains(response, 'Latest')
        self.assertContains(
            response,
            '<a href="/english/your-mind/your-mind-subsection/page-1/">'
            'Page 1</a>')
        self.assertContains(
            response,
            '<a href="/english/your-mind/your-mind-subsection/page-2/">'
            'Page 2</a>')

    def test_article_page(self):
        response = self.client.get(
            '/english/your-mind/your-mind-subsection/page-1/')
        self.assertContains(
            response,
            '<span class="active">Page 1</span>')
        self.assertContains(response, 'Lorem ipsum dolor sit amet')

    def test_markdown_in_article_page(self):
        response = self.client.get(
            '/english/your-mind/your-mind-subsection/page-1/')
        self.assertContains(
            response,
            '<strong>Lorem ipsum</strong> dolor <em>sit amet</em>')
