from datetime import date

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, AnonymousUser

from molo.profiles.context_processors import get_profile_data
from molo.core.tests.base import MoloTestCaseMixin


class ContextProcessorsTest(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')

    def test_get_profile_data_authenticated_anonymous(self):
        request = self.factory.get('/')
        request.user = self.user
        context = get_profile_data(request)
        self.assertEqual(context['username'], 'tester')
        self.assertEqual(context['alias'], 'Anonymous')

    def test_get_profile_data_authenticated_alias(self):
        profile = self.user.profile
        profile.alias = 'The Alias'
        profile.save()
        request = self.factory.get('/')
        request.user = self.user
        context = get_profile_data(request)
        self.assertEqual(context['alias'], 'The Alias')

    def test_get_profile_data_authenticated_dob(self):
        profile = self.user.profile
        profile.date_of_birth = date(1980, 1, 1)
        profile.save()
        request = self.factory.get('/')
        request.user = self.user
        context = get_profile_data(request)
        self.assertEqual(context['date_of_birth'], date(1980, 1, 1))

    def test_get_profile_data_unauthenticated(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()
        context = get_profile_data(request)
        self.assertEqual(context['username'], '')
        self.assertEqual(context['date_of_birth'], '')
        self.assertEqual(context['alias'], '')
