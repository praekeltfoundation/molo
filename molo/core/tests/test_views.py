import json
import pytest

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from molo.core.tests.base import MoloTestCaseMixin
from molo.core.models import SiteLanguage, FooterPage


@pytest.mark.django_db
class TestPages(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.english = SiteLanguage.objects.create(
            title='english', code='en'
        )
        self.mk_main()
        self.yourmind = self.mk_section(
            self.main, title='Your mind')
        self.yourmind_sub = self.mk_section(
            self.yourmind, title='Your mind subsection')

    def test_breadcrumbs(self):
        self.mk_articles(self.yourmind_sub, count=10)

        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)
        self.assertNotContains(response, 'Home')

        response = self.client.get('/your-mind/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, '<span class="active">Your mind</span>')

        response = self.client.get(
            '/your-mind/your-mind-subsection/test-page-1/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(
            response,
            '<span class="active">Test page 1</span>')

    def test_footer_pages(self):
        self.footer = FooterPage(
            title='Footer Page',
            slug='footer-page')
        self.main.add_child(instance=self.footer)

        response = self.client.get('/')
        self.assertContains(response, 'Footer Page')
        self.assertContains(
            response,
            '<a href="/footer-page/">Footer Page</a>')

        response = self.client.get(
            '/your-mind/your-mind-subsection/')
        self.assertContains(response, 'Footer Page')

    def test_section_listing(self):
        self.mk_articles(self.yourmind_sub, count=10)

        self.yourmind.extra_style_hints = 'yellow'
        self.yourmind.save_revision().publish()

        response = self.client.get('/')
        self.assertContains(response, 'Your mind')
        self.assertContains(
            response,
            '<a href="/your-mind/">Your mind</a>')
        self.assertContains(response, '<div class="articles nav yellow">')

        # Child page should have extra style from section
        response = self.client.get(
            '/your-mind/your-mind-subsection/test-page-1/')
        self.assertContains(response, '<div class="articles nav yellow">')

    def test_latest_listing(self):
        self.mk_articles(self.yourmind_sub, count=10, featured_in_latest=True)

        response = self.client.get('/')
        self.assertContains(response, 'Latest')
        self.assertContains(
            response,
            '<a href="/your-mind/your-mind-subsection/test-page-8/">'
            'Test page 8</a>')
        self.assertContains(
            response,
            '<a href="/your-mind/your-mind-subsection/test-page-9/">'
            'Test page 9</a>')

    def test_article_page(self):
        self.mk_articles(self.yourmind_sub, count=10)

        response = self.client.get(
            '/your-mind/your-mind-subsection/test-page-1/')
        self.assertContains(
            response,
            '<span class="active">Test page 1</span>')
        self.assertContains(response, 'Sample page content for 1')

    def test_markdown_in_article_page(self):
        self.mk_articles(
            self.yourmind_sub, count=10,
            body=json.dumps([{
                'type': 'paragraph',
                'value': '<strong>Lorem ipsum</strong> '
                         'dolor <em>sit amet</em>'}]))

        response = self.client.get(
            '/your-mind/your-mind-subsection/test-page-1/')
        self.assertContains(
            response,
            '<strong>Lorem ipsum</strong> dolor <em>sit amet</em>')

    def test_featured_homepage_listing(self):
        self.mk_article(self.yourmind_sub, featured_in_homepage=True)
        response = self.client.get('/')
        self.assertContains(
            response,
            'Sample page description for 0')

    def test_health(self):
        response = self.client.get('/health/')
        self.assertEquals(
            response.status_code, 200)

    def test_issue_with_django_admin_not_loading(self):
        User.objects.create_superuser(
            username='testuser', password='password', email='test@email.com')
        self.client.login(username='testuser', password='password')

        response = self.client.get(reverse('admin:index'))
        self.assertEquals(response.status_code, 200)
