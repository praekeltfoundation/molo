from os import environ
import json
import pytest
import responses

from datetime import timedelta
from urlparse import parse_qs

from django.core.files.base import ContentFile
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils import timezone

from molo.core.tests.base import MoloTestCaseMixin
from molo.core.models import SiteLanguage, FooterPage, SiteSettings
from molo.core.known_plugins import known_plugins

from mock import patch, Mock
from six import b

from wagtail.wagtailcore.models import Site
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
