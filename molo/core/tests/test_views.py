import json
import pytest
import responses

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from molo.core.tests.base import MoloTestCaseMixin
from molo.core.models import SiteLanguage, FooterPage, SiteSettings
from molo.core.known_plugins import known_plugins

from mock import patch, Mock

from wagtail.wagtailcore.models import Site


@pytest.mark.django_db
class TestPages(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.english = SiteLanguage.objects.create(locale='en')
        self.french = SiteLanguage.objects.create(locale='fr')
        self.mk_main()

        self.yourmind = self.mk_section(
            self.section_index, title='Your mind')
        self.yourmind_sub = self.mk_section(
            self.yourmind, title='Your mind subsection')

        self.yourmind_fr = self.mk_section_translation(
            self.yourmind, self.french, title='Your mind in french')
        self.yourmind_sub_fr = self.mk_section_translation(
            self.yourmind_sub, self.french,
            title='Your mind subsection in french')

    def test_breadcrumbs(self):
        self.mk_articles(self.yourmind_sub, count=10)

        response = self.client.get('/')
        print response
        self.assertEquals(response.status_code, 200)
        self.assertNotContains(response, 'Home')

        response = self.client.get('/sections/your-mind/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, '<span class="active">Your mind</span>')

        response = self.client.get(
            '/sections/your-mind/your-mind-subsection/test-page-1/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(
            response,
            '<span class="active">Test page 1</span>')

    def test_footer_pages(self):
        self.footer = FooterPage(
            title='Footer Page',
            slug='footer-page')
        self.footer_index.add_child(instance=self.footer)
        footer_french = self.mk_article_translation(
            self.footer, self.french,
            title='Footer Page in french')

        response = self.client.get('/')
        self.assertContains(response, 'Footer Page')
        self.assertContains(
            response,
            '<a href="/footer-pages/footer-page/">Footer Page</a>')
        self.assertNotContains(
            response,
            '<a href="/%s/">Footer Page in french</a>' % footer_french.slug)

        response = self.client.get(
            '/sections/your-mind/your-mind-subsection/')
        self.assertContains(response, 'Footer Page')
        self.assertNotContains(response, 'Footer Page in french')

    def test_section_listing(self):
        self.mk_articles(self.yourmind_sub, count=10)

        self.yourmind.extra_style_hints = 'yellow'
        self.yourmind.save_revision().publish()

        response = self.client.get('/')
        self.assertContains(response, 'Your mind')
        self.assertContains(
            response,
            '<a href="/sections/your-mind/">Your mind</a>')
        self.assertContains(response, '<div class="articles nav yellow">')

        # Child page should have extra style from section
        response = self.client.get(
            '/sections/your-mind/your-mind-subsection/test-page-1/')
        self.assertContains(response, '<div class="articles nav yellow">')

    def test_section_listing_in_french(self):
        self.yourmind.extra_style_hints = 'yellow'
        self.yourmind.save_revision().publish()

        response = self.client.get('/')
        self.assertContains(
            response,
            '<a href="/sections/your-mind/">Your mind</a>')
        self.assertNotContains(
            response,
            '<a href="/sections/your-mind-in-french/">Your mind in french</a>')

        response = self.client.get('/locale/fr/')
        response = self.client.get('/')

        self.assertNotContains(
            response,
            '<a href="/sections/your-mind/">Your mind</a>')
        self.assertContains(
            response,
            '<a href="/sections/your-mind-in-french/">Your mind in french</a>')

        # unpublished section should fallback to main language
        self.yourmind_fr.unpublish()

        response = self.client.get('/')

        self.assertContains(
            response,
            '<a href="/sections/your-mind/">Your mind</a>')
        self.assertNotContains(
            response,
            '<a href="/sections/your-mind-in-french/">Your mind in french</a>')

    def test_latest_listing(self):
        en_latest = self.mk_articles(
            self.yourmind_sub, count=10, featured_in_latest=True)

        for p in en_latest:
            self.mk_article_translation(
                p, self.french, title=p.title + ' in french')

        response = self.client.get('/')
        self.assertContains(response, 'Latest')
        self.assertContains(
            response,
            '<a href="/sections/your-mind/your-mind-subsection/test-page-8/">'
            'Test page 8</a>')
        self.assertContains(
            response,
            '<a href="/sections/your-mind/your-mind-subsection/test-page-9/">'
            'Test page 9</a>')
        self.assertNotContains(
            response, 'Test page 9 in french')
        self.assertNotContains(
            response, 'in french')

    def test_latest_listing_in_french(self):
        en_latest = self.mk_articles(
            self.yourmind_sub, count=10, featured_in_latest=True)

        for p in en_latest:
            self.mk_article_translation(
                p, self.french, title=p.title + ' in french')

        response = self.client.get('/locale/fr/')
        response = self.client.get('/')

        self.assertContains(response, 'Latest')
        self.assertContains(
            response,
            '<a href="/sections/your-mind/your-mind-subsection/'
            'test-page-8-in-french/">Test page 8 in french</a>')
        self.assertContains(
            response,
            '<a href="/sections/your-mind/your-mind-subsection/'
            'test-page-9-in-french/">Test page 9 in french</a>')
        self.assertNotContains(
            response, 'Test page 9</a>')

        # unpublished article should fallback to main language
        en_latest[9].specific.translations.first().translated_page.unpublish()

        response = self.client.get('/')
        self.assertNotContains(
            response,
            '<a href="/sections/your-mind/your-mind-subsection/'
            'test-page-9-in-french/">Test page 9 in french</a>')
        self.assertContains(
            response, 'Test page 9</a>')

    def test_article_page(self):
        self.mk_articles(self.yourmind_sub, count=10)

        response = self.client.get(
            '/sections/your-mind/your-mind-subsection/test-page-1/')
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
            '/sections/your-mind/your-mind-subsection/test-page-1/')
        self.assertContains(
            response,
            '<strong>Lorem ipsum</strong> dolor <em>sit amet</em>')

    def test_markdown_in_article_page_list(self):
        self.mk_articles(
            self.yourmind_sub, count=10,
            body=json.dumps([
                {'type': 'list',
                 'value': ['<strong>Lorem ipsum</strong>',
                           'dolor <em>sit amet</em>']},
                {'type': 'numbered_list',
                 'value': ['_ad nec_',
                           'aeque *saepe albucius*']}
            ]))

        response = self.client.get(
            '/sections/your-mind/your-mind-subsection/test-page-1/')
        self.assertContains(
            response,
            '<li><strong>Lorem ipsum</strong></li>')
        self.assertContains(
            response,
            '<li>dolor <em>sit amet</em></li>')
        self.assertContains(
            response,
            '<li><em>ad nec</em></li>')
        self.assertContains(
            response,
            '<li>aeque <em>saepe albucius</em></li>')

    def test_featured_homepage_listing(self):
        self.mk_article(self.yourmind_sub, featured_in_homepage=True)
        response = self.client.get('/')
        self.assertContains(
            response,
            '<p>Sample page description for 0</p>')

    def test_featured_homepage_listing_in_french(self):
        en_page = self.mk_article(self.yourmind_sub, featured_in_homepage=True)
        fr_page = self.mk_article_translation(
            en_page, self.french,
            title=en_page.title + ' in french',
            subtitle=en_page.subtitle + ' in french')
        response = self.client.get('/')
        self.assertContains(
            response,
            '<p>Sample page description for 0</p>')
        self.assertNotContains(
            response,
            '<p>Sample page description for 0 in french</p>')

        response = self.client.get('/locale/fr/')
        response = self.client.get('/')

        self.assertNotContains(
            response,
            '<p>Sample page description for 0</p>')
        self.assertContains(
            response,
            '<p>Sample page description for 0 in french</p>')

        # unpublished article should fallback to main language
        fr_page.unpublish()
        response = self.client.get('/')

        self.assertContains(
            response,
            '<p>Sample page description for 0</p>')
        self.assertNotContains(
            response,
            '<p>Sample page description for 0 in french</p>')

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

    def test_translaton_redirects(self):
        en_page = self.mk_article(self.yourmind, featured_in_homepage=True)
        fr_page = self.mk_article_translation(
            en_page, self.french,
            title=en_page.title + ' in french',
            subtitle=en_page.subtitle + ' in french')

        response = self.client.get('/sections/your-mind/')
        self.assertEquals(response.status_code, 200)

        response = self.client.get('/sections/your-mind/test-page-0/')
        self.assertEquals(response.status_code, 200)

        response = self.client.get('/locale/fr/')

        response = self.client.get('/sections/your-mind/')
        self.assertRedirects(response, 'sections/your-mind-in-french/')

        response = self.client.get('/sections/your-mind/test-page-0/')
        self.assertRedirects(response,
                             '/sections/your-mind/test-page-0-in-french/')

        # redirect from translation to main language should also work
        response = self.client.get('/locale/en/')

        response = self.client.get('/sections/your-mind-in-french/')
        self.assertRedirects(response, '/sections/your-mind/')

        response = self.client.get('/sections/your-mind/'
                                   'test-page-0-in-french/')
        self.assertRedirects(response, '/sections/your-mind/test-page-0/')

        # unpublished translation will not result in a redirect
        self.yourmind_fr.unpublish()
        response = self.client.get('/sections/your-mind/')
        self.assertEquals(response.status_code, 200)

        fr_page.unpublish()
        response = self.client.get('/sections/your-mind/test-page-0/')
        self.assertEquals(response.status_code, 200)

    def test_subsection_is_translated(self):
        en_page = self.mk_article(self.yourmind_sub)
        self.mk_article_translation(
            en_page, self.french,
            title=en_page.title + ' in french',
            subtitle=en_page.subtitle + ' in french')

        response = self.client.get('/sections/your-mind/')
        self.assertContains(response, 'Your mind subsection</a>')
        self.assertNotContains(response, 'Your mind subsection in french</a>')

        response = self.client.get('/locale/fr/')
        response = self.client.get('/sections/your-mind-in-french/')

        self.assertContains(response, 'Your mind subsection in french</a>')
        self.assertNotContains(response, 'Your mind subsection</a>')

        # ensure section fallbacks to main language
        self.yourmind_sub_fr.unpublish()
        response = self.client.get('/sections/your-mind-in-french/')

        self.assertContains(response, 'Your mind subsection</a>')
        self.assertNotContains(response, 'Your mind subsection in french</a>')

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
                    body=json.dumps({'info': {'version': '9.0.0'}}),
                    content_type="application/json",
                    status=200)

            response = self.client.get(reverse('versions'))
            self.assertContains(response, '9.0.0')
            self.assertContains(response, 'Compare')
            self.assertContains(response, 'Not installed')
        get_pypi_version()

    def test_ga_tag_manager_setting(self):
        default_site = Site.objects.get(is_default_site=True)
        setting = SiteSettings.objects.create(site=default_site)

        response = self.client.get('/')
        self.assertNotContains(response, 'www.googletagmanager.com')

        setting.ga_tag_manager = 'GTM-1234567'
        setting.save()

        response = self.client.get('/')
        self.assertContains(response, 'www.googletagmanager.com')
        self.assertContains(response, 'GTM-1234567')

    def test_admin_doesnt_translate_when_frontend_locale_changed(self):
        self.client.get('/locale/af/')

        User.objects.create_superuser(
            username='testuser', password='password', email='test@email.com')
        self.client.login(username='testuser', password='password')

        response = self.client.get('/admin/pages/%d/' % self.main.pk)
        self.assertNotContains(response, 'Skrap')

        response = self.client.get('/django-admin/')
        self.assertNotContains(response, 'Voeg')
