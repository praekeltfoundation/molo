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
        self.assertContains(response, '<span class="active">Your Mind</span>')

        response = self.client.get('/english/your-mind/another-story/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(
            response,
            '<span class="active">This is another story</span>')

    def test_section_listing(self):
        response = self.client.get('/')
        self.assertContains(response, 'About a girl')
        self.assertContains(response, 'about a boy')
        self.assertContains(
            response,
            '<a href="/english/your-mind/another-story/">'
            '<img src="/media/images/f5edfca6af2e4410b029864a2da149fd'
            '.focus-none.width-60.jpeg" width="60" height="39" alt="2 girls">'
            '</a>')

    def test_article_page(self):
        response = self.client.get('/english/your-mind/another-story/')
        self.assertContains(
            response,
            '<span class="active">This is another story</span>')
        self.assertContains(response, 'About a girl')

    def test_markdown_in_article_page(self):
        response = self.client.get('/english/your-mind/story/')
        self.assertContains(
            response,
            '<p>A markdown paragraph with <strong>bold</strong>'
            ' and <em>italics</em></p>')
