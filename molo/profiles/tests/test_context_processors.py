from datetime import date

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, AnonymousUser

from molo.profiles.context_processors import get_profile_data
from molo.core.tests.base import MoloTestCaseMixin
from wagtail.core.models import Site


class ContextProcessorsTest(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.main = self.mk_main()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')
        self.site = Site.objects.first()

    def test_get_profile_data_authenticated_anonymous(self):
        request = self.factory.get('/')
        request.user = self.user
        request._wagtail_site = self.site
        context = get_profile_data(request)
        self.assertEqual(context['username'], 'tester')
        self.assertEqual(context['alias'], 'Anonymous')

    def test_get_profile_data_authenticated_alias(self):
        profile = self.user.profile
        profile.alias = 'The Alias'
        profile.save()
        request = self.factory.get('/')
        request.user = self.user
        request._wagtail_site = self.site
        context = get_profile_data(request)
        self.assertEqual(context['alias'], 'The Alias')

    def test_get_profile_data_authenticated_dob(self):
        profile = self.user.profile
        profile.date_of_birth = date(1980, 1, 1)
        profile.save()
        request = self.factory.get('/')
        request.user = self.user
        request._wagtail_site = self.site
        context = get_profile_data(request)
        self.assertEqual(context['date_of_birth'], date(1980, 1, 1))

    def test_get_profile_data_unauthenticated(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()
        request._wagtail_site = self.site
        context = get_profile_data(request)
        self.assertEqual(context['username'], '')
        self.assertEqual(context['date_of_birth'], '')
        self.assertEqual(context['alias'], '')
