# -*- coding: utf-8 -*-

import responses
import mock
from django.test import TestCase
from django.test.client import Client
from django.test.client import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.urlresolvers import reverse

from google_analytics.templatetags.google_analytics_tags import google_analytics  # noqa
from molo.core.middleware import MoloGoogleAnalyticsMiddleware
from molo.core.models import Main, Languages, SiteLanguageRelation
from molo.core.tests.base import MoloTestCaseMixin
from wagtail.wagtailsearch.backends import get_search_backend


class TestUtils(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.client = Client()
        # Creates Main language
        self.mk_main()
        main = Main.objects.all().first()
        self.english = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(main.get_site()),
            locale='en',
            is_active=True)
        # Creates a section under the index page
        self.english_section = self.mk_section(
            self.section_index, title='English section')

    def make_fake_request(self, url, headers={}):
        """
        We don't have any normal views, so we're creating fake
        views using django's RequestFactory
        """
        rf = RequestFactory()
        request = rf.get(url, **headers)
        session_middleware = SessionMiddleware()
        session_middleware.process_request(request)
        request.session.save()
        return request

    @responses.activate
    @mock.patch("google_analytics.utils.build_ga_params")
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
