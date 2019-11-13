# -*- coding: utf-8 -*-

import responses
from unittest.mock import patch
from django.conf import settings
from django.test import TestCase, override_settings
from django.test.client import Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware

from wagtail.core.models import Site
from wagtail.search.backends import get_search_backend

from molo.core.tests.base import MoloTestCaseMixin
from molo.profiles.models import UserProfilesSettings
from molo.core.middleware import MoloGoogleAnalyticsMiddleware
from molo.core.models import Main, Languages, SiteLanguageRelation


MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'molo.core.middleware.ForceDefaultLanguageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'wagtail.core.middleware.SiteMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',

    'molo.core.middleware.AdminLocaleMiddleware',
    'molo.core.middleware.NoScriptGASessionMiddleware',

    'molo.core.middleware.MoloGoogleAnalyticsMiddleware',
    'molo.core.middleware.MultiSiteRedirectToHomepage',
    'molo.core.middleware.LoginRequiredMiddleware',
]


class TestUtils(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.client = Client()
        # Creates Main language
        self.mk_main()
        self.main = Main.objects.all().first()
        self.english = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(self.main.get_site()),
            locale='en',
            is_active=True)
        # Creates a section under the index page
        self.english_section = self.mk_section(
            self.section_index, title='English section')
        self.user = User.objects.create_superuser(
            username='testuser', password='password', email='test@email.com')

        profile = self.user.profile
        profile.alias = 'The Alias'
        profile.mobile_number = '+27784667723'
        profile.save()

    def make_fake_request(self, url, headers={}, user=None, locale=None):
        """
        We don't have any normal views, so we're creating fake
        views using django's RequestFactory
        """
        rf = RequestFactory()
        request = rf.get(url, **headers)
        if locale:
            request.COOKIES[settings.LANGUAGE_COOKIE_NAME] = locale
        if user:
            request.user = self.user
        session_middleware = SessionMiddleware()
        session_middleware.process_request(request)
        request.session.save()
        return request

    @responses.activate
    @patch("molo.core.middleware.build_ga_params")
    def test_ga_middleware(self, mock_method):
        self.backend = get_search_backend('default')
        self.backend.reset_index()
        self.mk_articles(self.english_section, count=2)
        self.backend.refresh_index()
        response = self.client.get(reverse('search'), {
            'q': 'Test'
        })
        headers = {'HTTP_X_IORG_FBS_UIP': '100.100.200.10'}
        request = self.make_fake_request(
            '/search/?q=Test', headers)

        middleware = MoloGoogleAnalyticsMiddleware()
        account = ''
        response = middleware.submit_tracking(account, request, response)
        self.assertTrue(mock_method.called_with(request.get_full_path()))
        self.assertEquals(
            mock_method._mock_call_args[1]['custom_params']['cd10'],
            self.english.locale)

    @patch('molo.core.middleware.build_ga_params')
    def test_ga_submit_tracking_with_custom_params(self, mock_method):
        self.backend = get_search_backend('default')
        self.backend.reset_index()
        self.mk_articles(self.english_section, count=2)
        self.backend.refresh_index()
        custom_params = {'cd2': '1235-245'}

        response = self.client.get(reverse('search'), {
            'q': 'Test'
        })
        headers = {'HTTP_X_IORG_FBS_UIP': '100.100.200.10'}
        request = self.make_fake_request(
            '/search/?q=Test', headers)

        middleware = MoloGoogleAnalyticsMiddleware()
        account = ''
        middleware.submit_tracking(
            account, request, response, custom_params)

        self.assertTrue('custom_params' in mock_method._mock_call_args[1])
        self.assertFalse('user_id' in mock_method._mock_call_args[1])
        self.assertTrue(mock_method._mock_call_args[1]['custom_params'],
                        custom_params)
        # the language parameter is passed into the request
        self.assertEquals(
            mock_method._mock_call_args[1]['custom_params']['cd10'],
            custom_params['cd10'],
            self.english.locale)

    @patch('molo.core.middleware.build_ga_params')
    def test_ga_submit_tracking_with_custom_params__language_change(
            self, mock_method):
        self.french = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(self.main.get_site()),
            locale='fr',
            is_active=True)
        response = self.client.get('/locale/fr/', follow=True)
        headers = {'HTTP_X_IORG_FBS_UIP': '100.100.200.10'}
        request = self.make_fake_request(
            '/locale/fr/',
            headers, self.user,
            locale=self.french.locale)

        middleware = MoloGoogleAnalyticsMiddleware()
        account = ''
        response = middleware.submit_tracking(account, request, response)
        self.assertTrue(mock_method.called_with(request.get_full_path()))

        self.assertEquals(
            mock_method._mock_call_args[1]['custom_params']['cd10'],
            self.french.locale)

    @patch('molo.core.middleware.build_ga_params')
    def test_ga_submit_tracking_with_custom_params__authenticated(
            self, mock_method):
        self.backend = get_search_backend('default')
        self.backend.reset_index()
        self.mk_articles(self.english_section, count=2)
        self.backend.refresh_index()

        custom_params = {'cd2': '1235-245'}

        response = self.client.get(reverse('search'), {
            'q': 'Test'
        })
        headers = {'HTTP_X_IORG_FBS_UIP': '100.100.200.10'}
        request = self.make_fake_request(
            '/search/?q=Test', headers, self.user)

        middleware = MoloGoogleAnalyticsMiddleware()
        account = ''
        middleware.submit_tracking(
            account, request, response, custom_params,)

        # check if uuid was there
        self.assertTrue('user_id' in mock_method._mock_call_args[1])
        self.assertTrue('custom_params' in mock_method._mock_call_args[1])
        self.assertTrue(mock_method._mock_call_args[1]['custom_params'],
                        custom_params)

    @override_settings(MIDDLEWARE=MIDDLEWARE)
    def test_login_required(self):
        self.client.logout()
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)

        self.client.force_login(self.user)
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)

    @override_settings(MIDDLEWARE=MIDDLEWARE)
    def test_login_required_true(self):
        self.client.logout()

        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)
        profile_settings.require_login = True
        profile_settings.save()

        res = self.client.get('/')
        self.assertEqual(res.url, settings.LOGIN_URL + '?next=/')

        self.client.force_login(self.user)
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
