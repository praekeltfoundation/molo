import json
import pytest
import responses

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from molo.core.tests.base import MoloTestCaseMixin
from molo.core.known_plugins import known_plugins

from mock import patch, Mock


@pytest.mark.django_db
class TestPages(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.yourmind = self.mk_section(
            self.english, title='Your mind')
        self.yourmind_sub = self.mk_section(
            self.yourmind, title='Your mind subsection')

    def test_breadcrumbs(self):
        self.mk_articles(self.yourmind_sub, count=10)

        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)
        self.assertNotContains(response, 'Home')

        response = self.client.get('/english/your-mind/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, '<span class="active">Your mind</span>')

        response = self.client.get(
            '/english/your-mind/your-mind-subsection/test-page-1/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(
            response,
            '<span class="active">Test page 1</span>')

    def test_section_listing(self):
        self.mk_articles(self.yourmind_sub, count=10)

        self.yourmind.extra_style_hints = 'yellow'
        self.yourmind.save_revision().publish()

        response = self.client.get('/')
        self.assertContains(response, 'Your mind')
        self.assertContains(
            response,
            '<a href="/english/your-mind/">Your mind</a>')
        self.assertContains(response, '<div class="articles nav yellow">')

        # Child page should have extra style from section
        response = self.client.get(
            '/english/your-mind/your-mind-subsection/test-page-1/')
        self.assertContains(response, '<div class="articles nav yellow">')

    def test_latest_listing(self):
        self.mk_articles(self.yourmind_sub, count=10, featured_in_latest=True)

        response = self.client.get('/')
        self.assertContains(response, 'Latest')
        self.assertContains(
            response,
            '<a href="/english/your-mind/your-mind-subsection/test-page-8/">'
            'Test page 8</a>')
        self.assertContains(
            response,
            '<a href="/english/your-mind/your-mind-subsection/test-page-9/">'
            'Test page 9</a>')

    def test_article_page(self):
        self.mk_articles(self.yourmind_sub, count=10)

        response = self.client.get(
            '/english/your-mind/your-mind-subsection/test-page-1/')
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
            '/english/your-mind/your-mind-subsection/test-page-1/')
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

    def test_versions_comparison(self):
        response = self.client.get(reverse('versions'))
        self.assertContains(response, 'Molo')
        self.assertContains(response, 'Profiles')

        with patch('pkg_resources.get_distribution', return_value=Mock(
                version='2.5.0')):
            response = self.client.get(reverse('versions'))
            self.assertContains(response, '2.5.0')

        @responses.activate
        def get_pypi_version():
            for plugin in known_plugins():
                responses.add(
                    responses.GET, (
                        'https://pypi.python.org/pypi/%s/json' % plugin[0]),
                    body=json.dumps({'info': {'version': '3.0.0'}}),
                    content_type="application/json",
                    status=200)

            response = self.client.get(reverse('versions'))
            self.assertContains(response, '3.0.0')
            self.assertContains(response, 'Compare')
            self.assertContains(response, 'Not installed')
        get_pypi_version()
