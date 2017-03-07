from os import environ
import json
import pytest
import responses

from datetime import timedelta, datetime
from urlparse import parse_qs

from django.core.files.base import ContentFile
from django.test import TestCase, override_settings
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.utils import timezone

from molo.core.tests.base import MoloTestCaseMixin
from molo.core.models import (SiteLanguage, FooterPage,
                              SiteSettings, ArticlePage,
                              ArticlePageRecommendedSections,
                              Main, BannerIndexPage,
                              SectionIndexPage,
                              FooterIndexPage)
from molo.core.known_plugins import known_plugins
from molo.core.tasks import promote_articles
from molo.core.templatetags.core_tags import \
    load_descendant_articles_for_section

from mock import patch, Mock
from six import b
from bs4 import BeautifulSoup

from wagtail.wagtailcore.models import Site
from wagtail.wagtailimages.tests.utils import Image, get_test_image_file
from wagtailmedia.models import Media


@pytest.mark.django_db
@override_settings(GOOGLE_ANALYTICS={})
class TestPages(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.english = SiteLanguage.objects.create(locale='en')
        self.french = SiteLanguage.objects.create(locale='fr')
        self.spanish = SiteLanguage.objects.create(locale='es')
        self.arabic = SiteLanguage.objects.create(locale='ar')
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

        # Create an image for running tests on
        self.image = Image.objects.create(
            title="Test image",
            file=get_test_image_file(),
        )

    def test_breadcrumbs(self):
        self.mk_articles(self.yourmind_sub, count=10)

        response = self.client.get('/')
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

    def test_switching_between_child_languages(self):
        self.yourmind_es = self.mk_section_translation(
            self.yourmind, self.spanish, title='Your mind in spanish')
        self.yourmind_ar = self.mk_section_translation(
            self.yourmind, self.arabic, title='Your mind in arabic')
        en_page = self.mk_article(self.yourmind)

        response = self.client.get('/')
        self.assertContains(
            response,
            '<a href="/sections/your-mind/">Your mind</a>')

        response = self.client.get('/sections/your-mind/%s/' % (en_page.slug))
        self.assertContains(
            response,
            ' <p>Sample page content for 0</p>')

        fr_page = self.mk_article_translation(
            en_page, self.french,
            title=en_page.title + ' in french',
            subtitle=en_page.subtitle + ' in french',
            body=json.dumps([{
                            'type': 'paragraph',
                            'value': 'Sample page content for %s' % (
                                en_page.title + ' in french')}]),
        )

        response = self.client.get('/locale/fr/')

        response = self.client.get('/sections/your-mind/%s/' % (fr_page.slug))
        self.assertContains(response, 'Sample page content for %s' % (
            en_page.title + ' in french'))

        self.mk_article_translation(
            en_page, self.spanish,
            title=en_page.title + ' in spanish',
            subtitle=en_page.subtitle + ' in spanish',
            body=json.dumps([{
                            'type': 'paragraph',
                            'value': 'Sample page content for %s' % (
                                en_page.title + ' in spanish')}]),
        )

        response = self.client.get(
            '/locale/es/?next=/sections/your-mind/%s/' % (fr_page.slug),
            follow=True)
        self.assertContains(response, 'Sample page content for %s' % (
            en_page.title + ' in spanish'))

    def test_latest_listing(self):
        en_latest = self.mk_articles(
            self.yourmind_sub, count=10,
            featured_in_latest_start_date=datetime.now())
        promote_articles()
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

    def test_latest(self):
        en_latest = self.mk_articles(
            self.yourmind_sub, count=4,
            featured_in_latest_start_date=datetime.now())
        promote_articles()
        for p in en_latest:
            self.mk_article_translation(
                p, self.french, title=p.title + ' in french')

        fr_articles = self.mk_articles(self.yourmind_sub, count=10)
        for p in fr_articles:
            self.mk_article_translation(
                p, self.french, title=p.title + ' in french')

        self.assertEquals(self.main.latest_articles().count(), 4)

    def test_latest_listing_in_french(self):
        en_latest = self.mk_articles(
            self.yourmind_sub, count=10,
            featured_in_latest_start_date=datetime.now())
        promote_articles()

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
        self.mk_article(
            self.yourmind_sub, featured_in_homepage_start_date=datetime.now())
        promote_articles()
        response = self.client.get('/')
        self.assertContains(
            response,
            '<p>Sample page description for 0</p>')

    def test_featured_homepage_listing_draft_articles(self):
        article = self.mk_article(
            self.yourmind_sub, featured_in_homepage_start_date=datetime.now())
        article2 = self.mk_article(
            self.yourmind_sub, featured_in_homepage_start_date=datetime.now())
        promote_articles()
        article2.unpublish()
        self.assertEquals(ArticlePage.objects.live().count(), 1)
        featured_in_homepage_articles = load_descendant_articles_for_section(
            {}, self.yourmind_sub, featured_in_homepage=True)
        self.assertEquals(featured_in_homepage_articles.count(), 1)
        self.assertEquals(
            featured_in_homepage_articles.first().title, article.title)

    def test_featured_topic_of_the_day(self):
        promote_date = timezone.now() + timedelta(days=-1)
        demote_date = timezone.now() + timedelta(days=1)
        self.mk_article(
            self.yourmind_sub,
            feature_as_topic_of_the_day=True,
            promote_date=promote_date,
            demote_date=demote_date
        )
        response = self.client.get('/')
        self.assertContains(
            response,
            'Topic of the Day')

    def test_social_media_footer(self):
        default_site = Site.objects.get(is_default_site=True)
        setting = SiteSettings.objects.create(site=default_site)
        setting.social_media_links_on_footer_page = json.dumps([
            {
                'type': 'social_media_site',
                'value': {
                    'title': 'Social Media Site',
                    'link': 'www.socialmediasite.com',
                    'image': 0,
                }}
        ])
        setting.save()

        self.footer = FooterPage(
            title='Footer Page',
            slug='footer-page')
        self.footer_index.add_child(instance=self.footer)

        response = self.client.get('/')
        self.assertContains(
            response,
            'www.socialmediasite.com')

    def test_social_media_facebook_sharing(self):
        default_site = Site.objects.get(is_default_site=True)
        setting = SiteSettings.objects.create(site=default_site)
        setting.facebook_sharing = True
        setting.facebook_image = self.image
        setting.save()

        self.mk_articles(self.yourmind_sub, count=10)

        response = self.client.get(
            '/sections/your-mind/your-mind-subsection/test-page-1/')
        self.assertContains(
            response,
            'href="http://www.facebook.com/sharer.php?u=http')

    def test_social_media_twitter_sharing(self):
        default_site = Site.objects.get(is_default_site=True)
        setting = SiteSettings.objects.create(site=default_site)
        setting.twitter_sharing = True
        setting.twitter_image = self.image
        setting.save()

        self.mk_articles(self.yourmind_sub, count=10)

        response = self.client.get(
            '/sections/your-mind/your-mind-subsection/test-page-1/')
        self.assertContains(
            response,
            'href="https://twitter.com/share?url=http')

    def test_featured_homepage_listing_in_french(self):
        en_page = self.mk_article(
            self.yourmind_sub, featured_in_homepage_start_date=datetime.now())
        promote_articles()
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

    def test_page_moving(self):
        # Login
        self.user = self.login()

        self.yourmind_fr = self.mk_section_translation(
            self.yourmind, self.french, title='Your mind in french')
        self.yourmind_ar = self.mk_section_translation(
            self.yourmind, self.arabic, title='Your mind in arabic')
        en_page = self.mk_article(self.yourmind)

        response = self.client.get('/')
        self.assertContains(
            response, '<a href="/sections/your-mind/">Your mind</a>')
        response = self.client.get('/sections/your-mind/%s/' % (en_page.slug))
        self.assertContains(
            response, ' <p>Sample page content for 0</p>')
        fr_page = self.mk_article_translation(
            en_page, self.french,
            title=en_page.title + ' in french',
            subtitle=en_page.subtitle + ' in french',
            body=json.dumps([{
                            'type': 'paragraph',
                            'value': 'Sample page content for %s' % (
                                en_page.title + ' in french')}]),
        )

        response = self.client.get('/locale/fr/')

        response = self.client.get('/sections/your-mind/%s/' % (fr_page.slug))
        self.assertContains(response, 'Sample page content for %s' % (
            en_page.title + ' in french'))

        response = self.client.post(reverse(
            'wagtailadmin_pages:move_confirm',
            args=(en_page.id, self.yourmind_sub.id)), data={'blank': 'blank'})
        self.assertEqual(response.status_code, 302)

        page_en = ArticlePage.objects.get(pk=en_page.pk)
        self.assertEquals(page_en.get_parent().specific, self.yourmind_sub)

        page_fr = ArticlePage.objects.get(pk=fr_page.pk)
        self.assertEquals(page_fr.get_parent().specific, self.yourmind_sub)

    def test_health(self):
        environ['MARATHON_APP_ID'] = 'marathon-app-id'
        environ['MARATHON_APP_VERSION'] = 'marathon-app-version'
        response = self.client.get('/health/')
        self.assertEquals(
            response.status_code, 200)
        self.assertEquals(
            json.loads(response.content), {
                'id': 'marathon-app-id',
                'version': 'marathon-app-version',
            })

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
        self.assertRedirects(response, '/sections/your-mind-in-french/?')

        response = self.client.get('/sections/your-mind/test-page-0/')
        self.assertRedirects(response,
                             '/sections/your-mind/test-page-0-in-french/?')

        # redirect from translation to main language should also work
        response = self.client.get('/locale/en/')

        response = self.client.get('/sections/your-mind-in-french/')
        self.assertRedirects(response, '/sections/your-mind/?')

        response = self.client.get('/sections/your-mind/'
                                   'test-page-0-in-french/')
        self.assertRedirects(response, '/sections/your-mind/test-page-0/?')

        # unpublished translation will not result in a redirect
        self.yourmind_fr.unpublish()
        response = self.client.get('/sections/your-mind/')
        self.assertEquals(response.status_code, 200)

        fr_page.unpublish()
        response = self.client.get('/sections/your-mind/test-page-0/')
        self.assertEquals(response.status_code, 200)

    def test_sitemap_translaton_redirects(self):
        self.yourmind_fr = self.mk_section_translation(
            self.yourmind, self.french, title='Your mind in french')
        response = self.client.get('/sections/your-mind/noredirect/')
        self.assertEquals(response.status_code, 200)

        response = self.client.get(
            '/sections/your-mind/your-mind-subsection/noredirect/')
        self.assertEquals(response.status_code, 200)

        response = self.client.get('/locale/fr/')

        response = self.client.get('/sections/your-mind-in-french/noredirect/')
        self.assertContains(response, 'Your mind subsection in french</a>')

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

    def test_ga_session_for_noscript_middleware(self):
        # GA session doesn't exist until the middleware sets it
        self.assertFalse('MOLO_GA_SESSION_FOR_NOSCRIPT' in self.client.session)

        self.client.get('/')
        self.assertTrue('MOLO_GA_SESSION_FOR_NOSCRIPT' in self.client.session)

        current_session_key = self.client.session[
            'MOLO_GA_SESSION_FOR_NOSCRIPT']

        self.client.get('/')

        # session key should be the same after subsequent requests
        self.assertEquals(
            self.client.session['MOLO_GA_SESSION_FOR_NOSCRIPT'],
            current_session_key)

    def test_local_ga_tag_manager_setting(self):
        default_site = Site.objects.get(is_default_site=True)
        setting = SiteSettings.objects.create(site=default_site)

        response = self.client.get('/')
        self.assertNotContains(response, 'www.googletagmanager.com')

        setting.ga_tag_manager = 'GTM-1234567'
        setting.save()

        response = self.client.get('/')
        self.assertContains(response, 'www.googletagmanager.com')
        self.assertContains(response, 'GTM-1234567')

        self.assertTrue('MOLO_GA_SESSION_FOR_NOSCRIPT' in self.client.session)
        self.assertContains(
            response, self.client.session['MOLO_GA_SESSION_FOR_NOSCRIPT'])

    @responses.activate
    def test_local_ga_tracking_code_setting(self):
        default_site = Site.objects.get(is_default_site=True)
        setting = SiteSettings.objects.create(site=default_site)

        responses.add(
            responses.GET, 'http://www.google-analytics.com/collect',
            body='',
            status=200)

        self.client.get('/')
        self.assertEqual(len(responses.calls), 0)

        setting.local_ga_tracking_code = 'GA-1234567'
        setting.save()

        self.client.get('/')
        self.assertEqual(len(responses.calls), 1)
        self.assertTrue(responses.calls[0].request.url.startswith(
            'http://www.google-analytics.com/collect'))

    @responses.activate
    def test_global_ga_tracking_code_setting(self):
        default_site = Site.objects.get(is_default_site=True)
        setting = SiteSettings.objects.create(site=default_site)

        self.client.get('/')
        self.assertEqual(len(responses.calls), 0)

        setting.global_ga_tracking_code = 'GA-1234567'
        setting.save()

        self.client.get('/')
        self.assertEqual(len(responses.calls), 1)
        self.assertTrue(responses.calls[0].request.url.startswith(
            'http://www.google-analytics.com/collect'))

    @responses.activate
    def test_ga_title_is_filled_in_using_middleware(self):
        default_site = Site.objects.get(is_default_site=True)
        setting = SiteSettings.objects.create(site=default_site)

        self.client.get('/')
        self.assertEqual(len(responses.calls), 0)

        setting.local_ga_tracking_code = 'GA-1234567'
        setting.save()

        self.client.get('/')
        self.assertEqual(len(responses.calls), 1)
        self.assertTrue(responses.calls[0].request.url.startswith(
            'http://www.google-analytics.com/collect'))
        self.assertTrue('GA-1234567' in responses.calls[0].request.url)

        ga_url = responses.calls[0].request.url

        self.assertEqual(parse_qs(ga_url).get('t'), ['pageview'])
        self.assertEqual(parse_qs(ga_url).get('dp'), ['/'])
        self.assertEqual(parse_qs(ga_url).get('dt'), ['Main'])
        self.assertEqual(parse_qs(ga_url).get('tid'), ['GA-1234567'])

    def test_global_ga_tag_manager_setting(self):
        default_site = Site.objects.get(is_default_site=True)
        setting = SiteSettings.objects.create(site=default_site)

        response = self.client.get('/')
        self.assertNotContains(response, 'www.googletagmanager.com')

        setting.global_ga_tag_manager = 'GTM-2345678'
        setting.save()

        response = self.client.get('/')
        self.assertContains(response, 'www.googletagmanager.com')
        self.assertContains(response, 'GTM-2345678')

        self.assertTrue('MOLO_GA_SESSION_FOR_NOSCRIPT' in self.client.session)
        self.assertContains(
            response, self.client.session['MOLO_GA_SESSION_FOR_NOSCRIPT'])

    def test_admin_doesnt_translate_when_frontend_locale_changed(self):
        self.client.get('/locale/af/')

        User.objects.create_superuser(
            username='testuser', password='password', email='test@email.com')
        self.client.login(username='testuser', password='password')

        response = self.client.get('/admin/pages/%d/' % self.main.pk)
        self.assertNotContains(response, 'Skrap')

        response = self.client.get('/django-admin/')
        self.assertNotContains(response, 'Voeg')

    def test_pagination_for_articles_in_sections(self):
        self.mk_articles(self.yourmind, count=15)

        response = self.client.get('/sections/your-mind/')
        self.assertContains(response, 'Page 1 of 3')
        self.assertContains(response, '&rarr;')
        self.assertNotContains(response, '&larr;')

        response = self.client.get('/sections/your-mind/?p=2')

        self.assertContains(response, 'Page 2 of 3')
        self.assertContains(response, '&rarr;')
        self.assertContains(response, '&larr;')

        response = self.client.get('/sections/your-mind/?p=3')

        self.assertContains(response, 'Page 3 of 3')
        self.assertNotContains(response, '&rarr;')
        self.assertContains(response, '&larr;')

    def test_pagination_for_translated_articles_in_sections(self):
        en_articles = self.mk_articles(self.yourmind, count=12)
        self.mk_articles(self.yourmind, count=3)

        for p in en_articles:
            self.mk_article_translation(
                p, self.french, title=p.title + ' in french')

        self.client.get('/locale/fr/')

        response = self.client.get('/sections/your-mind-in-french/')
        self.assertContains(response, 'Page 1 of 3')
        self.assertContains(response, 'Test page 0 in french')

        response = self.client.get('/sections/your-mind-in-french/?p=2')
        self.assertContains(response, 'Page 2 of 3')
        self.assertContains(response, 'Test page 7 in french')

        response = self.client.get(
            '/locale/en/?next=/sections/your-mind-in-french/?p=3', follow=True)

        self.assertContains(response, 'Page 3 of 3')
        self.assertNotContains(response, 'Test page 11 in french')
        self.assertContains(response, 'Test page 11')

    def test_pagination_for_articles_in_sub_sections(self):
        self.mk_articles(self.yourmind_sub, count=15)

        response = self.client.get('/sections/your-mind/')
        self.assertNotContains(response, 'Page 1 of 3')

        response = self.client.get('/sections/your-mind/your-mind-subsection/')
        self.assertContains(response, 'Page 1 of 3')
        self.assertContains(response, '&rarr;')
        self.assertNotContains(response, '&larr;')

        response = self.client.get(
            '/sections/your-mind/your-mind-subsection/?p=2')

        self.assertContains(response, 'Page 2 of 3')
        self.assertContains(response, '&rarr;')
        self.assertContains(response, '&larr;')

        response = self.client.get(
            '/sections/your-mind/your-mind-subsection/?p=3')

        self.assertContains(response, 'Page 3 of 3')
        self.assertNotContains(response, '&rarr;')
        self.assertContains(response, '&larr;')


class MultimediaViewTest(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.english = SiteLanguage.objects.create(locale='en')

        self.yourmind = self.mk_section(
            self.section_index, title='Your mind')

        self.article_page = self.mk_article(self.yourmind,
                                            title='Test Article')

    def add_media(self, media_type):
        fake_file = ContentFile(b("media"))
        fake_file.name = 'media.mp3'
        self.media = Media.objects.create(title="Test Media",
                                          file=fake_file,
                                          duration=100,
                                          type=media_type)

        self.article_page.body = json.dumps([{
            'type': 'media',
            'value': self.media.id,
        }])

        self.article_page.save_revision().publish()

    def test_audio_media(self):
        self.add_media('audio')
        response = self.client.get('/sections/your-mind/test-article/')
        self.assertContains(
            response,
            '''<div><audio controls><source src="{0}"
type="audio/mpeg">Click here to download
<a href="{0}">{1}</a></audio></div>'''
            .format(self.media.file.url, self.media.title)
        )

    def test_video_media(self):
        self.add_media('video')
        response = self.client.get('/sections/your-mind/test-article/')
        self.assertContains(
            response,
            '''<div><video width="320" height="240" controls>
<source src="{0}" type="video/mp4">Click here to download
<a href="{0}">{1}</a></video></div>'''
            .format(self.media.file.url, self.media.title)
        )


class TestArticlePageRelatedSections(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.english = SiteLanguage.objects.create(locale='en')
        self.french = SiteLanguage.objects.create(locale='fr')

    def test_article_related_section(self):
        section_a = self.mk_section(self.section_index, title='Section A')
        section_b = self.mk_section(self.section_index, title='Section B')

        article_a = self.mk_article(section_a, title='Article A')
        self.mk_article_translation(
            article_a, self.french, title=article_a.title + ' in french',)
        article_b = self.mk_article(section_b, title='Article B')
        self.mk_article_translation(
            article_b, self.french, title=article_b.title + ' in french',)

        article_a.related_sections.create(page=article_a, section=section_b)
        article_a.save_revision().publish()

        # check article A from section A exist in section A and B
        response = self.client.get('/sections/section-a/')
        self.assertContains(response, '/sections/section-a/article-a/')
        response = self.client.get('/sections/section-b/')
        self.assertContains(response, '/sections/section-a/article-a/')

        # check article A from section A exist in section A and B
        # when switching to french language and section B is not translated
        self.client.get('/locale/fr/')

        response = self.client.get('/sections/section-a/')
        self.assertContains(
            response, '/sections/section-a/article-a-in-french/')

        response = self.client.get('/sections/section-b/')
        self.assertContains(
            response, '/sections/section-a/article-a-in-french/')
        self.assertContains(
            response, '/sections/section-b/article-b-in-french/')

        # check article A from section A exist in section A and B
        # when switching to french language and section B is translated
        self.mk_section_translation(
            section_b, self.french, title=section_b.title + ' in french')

        response = self.client.get('/sections/section-a/')
        self.assertContains(
            response, '/sections/section-a/article-a-in-french/')

        response = self.client.get('/sections/section-b-in-french/')
        self.assertContains(
            response, '/sections/section-b/article-b-in-french/')
        self.assertContains(
            response, '/sections/section-a/article-a-in-french/')


class TestArticleTags(MoloTestCaseMixin, TestCase):
    def setUp(self):
        self.mk_main()

    def test_articles_with_the_same_tag(self):
        # create two articles with the same tag and check that they can
        # be retrieved
        new_section = self.mk_section(
            self.section_index, title="New Section", slug="new-section")
        first_article = self.mk_article(new_section, title="First article", )
        second_article = self.mk_article(new_section, title="Second article", )

        # add common tag to both articles
        first_article.tags.add("common")
        first_article.save_revision().publish()
        second_article.tags.add("common")
        second_article.save_revision().publish()

        # create another article that doesn't have the tag, and check that
        # it will be excluded from the return list
        self.mk_article(new_section, title="Third article", )

        response = self.client.get(
            reverse("tags_list", kwargs={"tag_name": "common"})
        )
        self.assertEqual(
            list(response.context["object_list"]),
            [first_article, second_article]
        )


class TestArticlePageRecommendedSections(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.english = SiteLanguage.objects.create(locale='en')
        self.french = SiteLanguage.objects.create(locale='fr')

        self.section_a = self.mk_section(self.section_index, title='Section A')

        self.section_a.enable_recommended_section = True
        self.section_a.save()

        self.article_a = self.mk_article(self.section_a, title='Article A')
        self.article_a.save_revision().publish()
        self.article_b = self.mk_article(self.section_a, title='Article B')
        self.article_b.save_revision().publish()
        self.article_c = self.mk_article(self.section_a, title='Article C')
        self.article_c.save_revision().publish()
        self.article_d = self.mk_article(self.section_a, title='Article D')
        self.article_d.save_revision().publish()

        self.mk_article_translation(
            self.article_a,
            self.french,
            title=self.article_a.title + ' in french',)
        self.mk_article_translation(
            self.article_b, self.french,
            title=self.article_b.title + ' in french',)
        self.mk_article_translation(
            self.article_c, self.french,
            title=self.article_c.title + ' in french',)

        self.mk_article_translation(
            self.article_d, self.french,
            title=self.article_d.title + ' in french',)

        self.recommended_article_1 = ArticlePageRecommendedSections(
            page=self.article_a,
            recommended_article=self.article_b)
        self.recommended_article_1.save()

        self.recommended_article_2 = ArticlePageRecommendedSections(
            page=self.article_a,
            recommended_article=self.article_c)
        self.recommended_article_2.save()

    def test_article_recommended_section_enabled_disabled(self):

        self.assertTrue(
            self.article_a.get_parent_section()
            .enable_recommended_section)

        self.assertEquals(
            self.article_b,
            self.article_a.recommended_articles.first()
            .recommended_article.specific)

        response = self.client.get('/sections/section-a/article-a/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'Recommended')
        self.assertContains(response, self.article_b.title)

        self.section_a.enable_recommended_section = False
        self.section_a.save()

        response = self.client.get('/sections/section-a/article-a/')
        self.assertNotContains(response, 'Recommended')
        self.assertNotContains(response, self.article_b.title)

    def test_article_recommended_section_multi_language(self):
        self.client.get('/locale/fr/')

        response = self.client.get('/sections/section-a/article-a-in-french/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, self.article_b.title + ' in french')
        self.assertContains(response, self.article_c.title + ' in french')

    def test_article_recommended_section_untranslated(self):
        ArticlePage.objects.get(
            title=self.article_b.title + ' in french').delete()

        self.client.get('/locale/fr/')

        response = self.client.get(
            '/sections/section-a/article-a-in-french/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, self.article_b.title)
        self.assertContains(response, self.article_c.title + ' in french')

    def test_article_recommended_section_only_translated(self):
        default_site = Site.objects.get(is_default_site=True)
        setting = SiteSettings.objects.create(site=default_site)
        setting.show_only_translated_pages = True
        setting.save()

        ArticlePage.objects.get(
            title=self.article_b.title + ' in french').delete()

        self.client.get('/locale/fr/')

        response = self.client.get(
            '/sections/section-a/article-a-in-french/')
        self.assertEquals(response.status_code, 200)
        self.assertNotContains(response, self.article_b.title)
        self.assertNotContains(response, self.article_b.title + 'in french')
        self.assertContains(response, self.article_c.title + ' in french')

    def test_article_recommended_custom_recommended_per_language(self):
        self.article_a_fr = ArticlePage.objects.get(
            title=self.article_a.title + ' in french')
        self.article_c_fr = ArticlePage.objects.get(
            title=self.article_c.title + ' in french')

        self.client.get('/locale/fr/')

        response = self.client.get(
            '/sections/section-a/article-a-in-french/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, self.article_b.title + ' in french')
        self.assertContains(response, self.article_c_fr.title)

        self.recommended_article_3 = ArticlePageRecommendedSections(
            page=self.article_a_fr,
            recommended_article=self.article_c_fr)
        self.recommended_article_3.save()

        self.recommended_article_4 = ArticlePageRecommendedSections(
            page=self.article_a_fr,
            recommended_article=self.article_d)
        self.recommended_article_4.save()

        response = self.client.get(
            '/sections/section-a/article-a-in-french/')
        self.assertEquals(response.status_code, 200)
        self.assertNotContains(response, self.article_b.title + ' in french')
        self.assertContains(response, self.article_d.title + ' in french')
        self.assertContains(response, self.article_c_fr.title)


class TestArticlePageNextArticle(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.english = SiteLanguage.objects.create(locale='en')
        self.french = SiteLanguage.objects.create(locale='fr')

        self.section_a = self.mk_section(self.section_index, title='Section A')

        self.section_a.enable_next_section = True
        self.section_a.save()

        self.article_a = self.mk_article(self.section_a, title='Article A')
        self.article_a.save_revision().publish()
        self.article_b = self.mk_article(self.section_a, title='Article B')
        self.article_b.save_revision().publish()
        self.article_c = self.mk_article(self.section_a, title='Article C')
        self.article_c.save_revision().publish()

        self.mk_article_translation(
            self.article_a,
            self.french,
            title=self.article_a.title + ' in french',)
        self.mk_article_translation(
            self.article_b, self.french,
            title=self.article_b.title + ' in french',)
        self.mk_article_translation(
            self.article_c, self.french,
            title=self.article_c.title + ' in french',)

    def test_next_article_main_language(self):
        # assumes articles loop
        self.assertTrue(
            self.article_b.get_parent_section().enable_next_section)

        response = self.client.get('/sections/section-a/article-c/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'Next up in ' + self.section_a.title)
        self.assertContains(response, self.article_b.title)

        response = self.client.get('/sections/section-a/article-b/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'Next up in ' + self.section_a.title)
        self.assertContains(response, self.article_a.title)

        response = self.client.get('/sections/section-a/article-a/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'Next up in ' + self.section_a.title)
        self.assertContains(response, self.article_c.title)

        self.section_a.enable_next_section = False
        self.section_a.save()

        response = self.client.get('/sections/section-a/article-c/')
        self.assertEquals(response.status_code, 200)
        self.assertNotContains(response, 'Next up in ' + self.section_a.title)
        self.assertNotContains(response, self.article_b.title)

    def test_next_article_not_main_language(self):
        # assumes articles loop
        self.client.get('/locale/fr/')

        response = self.client.get('/sections/section-a/article-c-in-french/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, self.article_b.title + ' in french')

        response = self.client.get('/sections/section-a/article-b-in-french/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, self.article_a.title + ' in french')

        response = self.client.get('/sections/section-a/article-a-in-french/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, self.article_c.title + ' in french')

    def test_next_article_show_untranslated_pages(self):
        response = self.client.get('/sections/section-a/article-c/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'Next up in ' + self.section_a.title)
        self.assertContains(response, self.article_b.title)

        ArticlePage.objects.get(
            title=self.article_b.title + ' in french').delete()

        self.client.get('/locale/fr/')

        response = self.client.get('/sections/section-a/article-c-in-french/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, self.article_b.title)

    def test_next_article_show_only_translated_pages(self):
        default_site = Site.objects.get(is_default_site=True)
        setting = SiteSettings.objects.create(site=default_site)
        setting.show_only_translated_pages = True
        setting.save()

        response = self.client.get('/sections/section-a/article-c/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'Next up in ' + self.section_a.title)
        self.assertContains(response, self.article_b.title)

        ArticlePage.objects.get(
            title=self.article_b.title + ' in french').delete()

        self.client.get('/locale/fr/')

        response = self.client.get('/sections/section-a/article-c-in-french/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, self.article_a.title + ' in french')

    def test_next_article_with_related_section(self):
        self.section_b = self.mk_section(self.section_index, title='Section B')
        self.section_b.enable_next_section = True
        self.section_b.save()

        self.article_1 = self.mk_article(self.section_b, title='Article 1')
        self.article_1.save_revision().publish()
        self.article_2 = self.mk_article(self.section_b, title='Article 2')
        self.article_2.related_sections.create(page=self.article_2,
                                               section=self.section_a)
        self.article_2.save_revision().publish()

        response = self.client.get('/sections/section-b/article-2/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, self.article_1.title)
        self.assertContains(response, 'Next up in ' + self.section_b.title)

    def test_next_article_not_displayed_for_single_article(self):
        self.section_b = self.mk_section(self.section_index, title='Section B')

        self.article_1 = self.mk_article(self.section_b, title='Article 1')
        self.article_1.save_revision().publish()

        response = self.client.get('/sections/section-b/article-1/')
        self.assertEquals(response.status_code, 200)
        self.assertNotContains(response, 'Next up in')

    def test_next_article_not_displayd_single_article_only_translated(self):
        default_site = Site.objects.get(is_default_site=True)
        setting = SiteSettings.objects.create(site=default_site)
        setting.show_only_translated_pages = True
        setting.save()

        self.section_b = self.mk_section(self.section_index, title='Section B')

        self.article_1 = self.mk_article(self.section_b, title='Article 1')
        self.article_1.save_revision().publish()

        response = self.client.get('/sections/section-b/article-1/')
        self.assertEquals(response.status_code, 200)
        self.assertNotContains(response, 'Next up in')


class TestDjangoAdmin(TestCase):

    def test_upload_download_links(self):
        User.objects.create_superuser(
            username='testuser', password='password', email='test@email.com')
        self.client.login(username='testuser', password='password')

        response = self.client.get(reverse('admin:index'))

        self.assertEquals(response.status_code, 200)
        self.assertContains(
            response,
            '<a href="/django-admin/upload_media/">Upload Media</a>'
        )
        self.assertContains(
            response,
            '<a href="/django-admin/download_media/">Download Media</a>'
        )


class TestDeleteButtonRemoved(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.english = SiteLanguage.objects.create(locale='en')

        self.login()

    def test_delete_button_removed_for_index_pages_in_main(self):

        index_titles = [
            BannerIndexPage.objects.first().title,
            SectionIndexPage.objects.first().title,
            FooterIndexPage.objects.first().title,
        ]

        main_page = Main.objects.first()
        response = self.client.get('/admin/pages/{0}/'
                                   .format(str(main_page.pk)))
        self.assertEquals(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        # Get all the rows in the body of the table
        index_page_rows = soup.find_all('tbody')[0].find_all('tr')

        for row in index_page_rows:
            if row.h2.a.string in index_titles:
                self.assertTrue(row.find('a', string='Edit'))
                self.assertFalse(row.find('a', string='Delete'))

    def test_delete_button_removed_from_dropdown_menu_main(self):
        # Remove 'Delete' from drop-down menu
        main_page = Main.objects.first()
        response = self.client.get('/admin/pages/{0}/'
                                   .format(str(main_page.pk)))
        delete_link = ('<a href="/admin/pages/{0}/delete/" '
                       'title="Delete this page" class="u-link '
                       'is-live ">Delete</a>'.format(str(main_page.pk)))

        self.assertEquals(response.status_code, 200)
        self.assertNotContains(response, delete_link, html=True)

    def test_delete_button_removed_in_edit_menu(self):
        main_page = Main.objects.first()
        response = self.client.get('/admin/pages/{0}/edit/'
                                   .format(str(main_page.pk)))

        delete_button = ('<li><a href="/admin/pages/{0}/delete/" '
                         'class="shortcut">Delete</a></li>'
                         .format(str(main_page.pk)))

        self.assertEquals(response.status_code, 200)
        self.assertNotContains(response, delete_button, html=True)

    def test_delete_button_not_removed_in_edit_menu_for_sections(self):
        section_page = self.mk_section(self.section_index, title='Section A')
        response = self.client.get('/admin/pages/{0}/edit/'
                                   .format(str(section_page.pk)))

        delete_button = ('<li><a href="/admin/pages/{0}/delete/" '
                         'class="shortcut">Delete</a></li>'
                         .format(str(section_page.pk)))

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, delete_button, html=True)


class TestWagtailAdmin(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.english = SiteLanguage.objects.create(locale='en')
        self.superuser = User.objects.create_superuser(
            username='testuser', password='password', email='test@email.com')

        self.expert_group, _created = Group.objects.get_or_create(
            name='Expert')

        # Create wagtail group with wagtail admin permissions
        self.wagtail_login_only_group, _created = Group.objects.get_or_create(
            name='Wagtail Login Only')

        wagtailadmin_content_type, created = ContentType.objects.get_or_create(
            app_label='wagtailadmin',
            model='admin'
        )

        # Create admin permission
        admin_permission, created = Permission.objects.get_or_create(
            content_type=wagtailadmin_content_type,
            codename='access_admin',
            name='Can access Wagtail admin'
        )

        # add the wagtail login permissions to group
        access_admin = Permission.objects.get(codename='access_admin')
        self.wagtail_login_only_group.permissions.add(access_admin)

        self.admin_user = User.objects.create_user(
            username='username', password='password', email='login@email.com')

    def can_see_explorer(self, client):
        response = client.get('/admin/')
        self.assertEquals(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertTrue(soup.find('a', string='Explorer'))

    def test_superuser_explorer_access(self):
        self.client.login(username='testuser', password='password')

        self.can_see_explorer(self.client)

        self.superuser.groups.set([self.expert_group])

        self.can_see_explorer(self.client)

    def test_wagtail_login_only_user_cannot_see_explorer(self):
        self.admin_user.groups.set([self.wagtail_login_only_group])

        self.client.login(
            username=self.admin_user.username,
            password='password')

        response = self.client.get('/admin/')

        self.assertEquals(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertFalse(soup.find('a', string='Explorer'))
