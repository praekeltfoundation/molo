# -*- coding: utf-8 -*-

import responses
from unittest.mock import patch
from django.conf import settings
from django.test import TestCase, RequestFactory
from django.test.client import Client
from django.contrib.sessions.middleware import SessionMiddleware
from django.urls import reverse

from molo.core.middleware import MoloGoogleAnalyticsMiddleware
from django.contrib.auth.models import User
from molo.core.models import Main, Languages, SiteLanguageRelation
from molo.core.tests.base import MoloTestCaseMixin
from wagtail.search.backends import get_search_backend


class TestUtils(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        # Creates Main language
        self.mk_main()
        self.main = Main.objects.all().first()
        self.site = self.main.get_site()
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
        request._wagtail_site = self.site
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
        request = self.factory.get('/search/?q=Test', headers)
        request._wagtail_site = self.site
        mock_method.return_value = {
            'utm_url': 'http://url',
            'user_id': 75,
            'user_agent': 'agent',
            'language': 'en',
            'COOKIE_USER_PERSISTENCE': 30,
            'COOKIE_NAME': 'name',
            'COOKIE_PATH': '/'}
        middleware = MoloGoogleAnalyticsMiddleware()
        account = ''
        response = middleware.submit_tracking(account, request, response)
        self.assertTrue(mock_method.called_with(request.get_full_path()))
        self.assertEqual(
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
        request = self.factory.get('/')
        request._wagtail_site = self.site
        mock_method.return_value = {
            'utm_url': 'url',
            'user_agent': 'agent',
            'language': 'en',
            'COOKIE_USER_PERSISTENCE': 30,
            'COOKIE_NAME': 'name',
            'COOKIE_PATH': '/'}
        middleware = MoloGoogleAnalyticsMiddleware()
        account = ''
        middleware.submit_tracking(
            account, request, response, custom_params)

        self.assertTrue('custom_params' in mock_method._mock_call_args[1])
        self.assertFalse('user_id' in mock_method._mock_call_args[1])
        self.assertTrue(mock_method._mock_call_args[1]['custom_params'],
                        custom_params)
        # the language parameter is passed into the request
        self.assertEqual(
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
        request._wagtail_site = self.site
        mock_method.return_value = {
            'utm_url': 'url',
            'user_agent': 'agent',
            'language': 'fr',
            'COOKIE_USER_PERSISTENCE': 30,
            'COOKIE_NAME': 'name',
            'COOKIE_PATH': '/'}
        middleware = MoloGoogleAnalyticsMiddleware()
        account = ''
        response = middleware.submit_tracking(account, request, response)
        self.assertTrue(mock_method.called_with(request.get_full_path()))

        self.assertEqual(
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
        request._wagtail_site = self.site
        mock_method.return_value = {
            'utm_url': 'http://url',
            'user_id': 75,
            'user_agent': 'agent',
            'language': 'en',
            'COOKIE_USER_PERSISTENCE': 30,
            'COOKIE_NAME': 'name',
            'COOKIE_PATH': '/'}
        middleware = MoloGoogleAnalyticsMiddleware()
        account = ''
        middleware.submit_tracking(
            account, request, response, custom_params,)

        # check if uuid was there
        self.assertTrue('user_id' in mock_method._mock_call_args[1])
        self.assertTrue('custom_params' in mock_method._mock_call_args[1])
        self.assertTrue(mock_method._mock_call_args[1]['custom_params'],
                        custom_params)
