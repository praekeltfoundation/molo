from mock import patch
from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.conf.urls import patterns, url, include

try:
    from django.template.base import TemplateDoesNotExist
except ImportError:  # Removed in Django 1.9
    from django.template import TemplateDoesNotExist

from molo.core.tests.base import MoloTestCaseMixin
from molo.core.urls import urlpatterns

from wagtail.wagtailadmin import urls as wagtailadmin_urls

urlpatterns += patterns(
    '',
    url(
        r'^profiles/login/$',
        'django.contrib.auth.views.login',
        name='auth_login'),
    url(
        r'^profiles/logout/$',
        'django.contrib.auth.views.logout',
        name='auth_logout'),
    url(r'^admin/', include(wagtailadmin_urls)),
)


class CASTestCase(TestCase, MoloTestCaseMixin):

    def test_login_redirect(self):
        response = self.client.get('/admin/', follow=True)

        self.assertEquals(
            response.request.get('QUERY_STRING'),
            'service=http%3A%2F%2Ftestserver'
            '%2Fadmin%2Flogin%2F%3Fnext%3D%252Fadmin%252F')

    @patch('cas.CASClientV2.verify_ticket')
    def test_succesful_login(self, mock_verify):
        service = ('http%3A%2F%2Ftestserver'
                   '%2Fadmin%2Flogin%2F%3Fnext%3D%252Fadmin%252F')

        mock_verify.return_value = (
            'test@example.com',
            {'ticket': 'fake-ticket', 'service': service, 'has_perm': 'True'},
            None)

        response = self.client.get(
            '/admin/login/',
            {'ticket': 'fake-ticket', 'next': '/admin/'},
            follow=True)

        self.assertContains(response, 'Welcome to the base Wagtail CMS')

    @patch('cas.CASClientV2.verify_ticket')
    def test_failed_login(self, mock_verify):
        service = ('http%3A%2F%2Ftestserver'
                   '%2Fadmin%2Flogin%2F%3Fnext%3D%252Fadmin%252F')

        mock_verify.return_value = (
            None,
            {'ticket': 'fake-ticket', 'service': service},
            None)

        response = self.client.get(
            '/admin/login/',
            {'ticket': 'fake-ticket', 'next': '/admin/'},
            follow=True)

        self.assertContains(
            response, 'You do not have permssion to access this site.',
            status_code=403)

    @patch('cas.CASClientV2.verify_ticket')
    def test_successful_login_but_no_permissions(self, mock_verify):
        service = ('http%3A%2F%2Ftestserver'
                   '%2Fadmin%2Flogin%2F%3Fnext%3D%252Fadmin%252F')

        mock_verify.return_value = (
            'test@example.com',
            {'ticket': 'fake-ticket', 'service': service, 'has_perm': 'False'},
            None)

        response = self.client.get(
            '/admin/login/',
            {'ticket': 'fake-ticket', 'next': '/admin/'},
            follow=True)

        self.assertContains(
            response, 'You do not have permssion to access this site.',
            status_code=403)

    def test_normal_user_login_has_no_permissions(self):
        User.objects.create_user(
            username='testuser', password='password', email='test@email.com')
        self.client.login(username='testuser', password='password')

        response = self.client.get('/admin/')
        self.assertContains(
            response, 'You do not have permssion to access this site.',
            status_code=403)

    @patch('cas.CASClientV2.verify_ticket')
    def test_succesful_logout(self, mock_verify):
        service = ('http%3A%2F%2Ftestserver'
                   '%2Fadmin%2Flogin%2F%3Fnext%3D%252Fadmin%252F')

        mock_verify.return_value = (
            'test@example.com',
            {'ticket': 'fake-ticket', 'service': service, 'has_perm': 'True'},
            None)

        # login a user
        response = self.client.get(
            '/admin/login/',
            {'ticket': 'fake-ticket', 'next': '/admin/'},
            follow=True)

        # logout
        response = self.client.get('/admin/logout/', follow=True)
        self.assertEquals(
            response.request.get('QUERY_STRING'),
            'service=http%3A%2F%2Ftestserver%2F')

    @override_settings(ROOT_URLCONF='molo.core.tests.test_cas')
    def test_normal_profiles_login_works_when_cas_enabled(self):
        self.mk_main()

        client = Client()
        try:
            client.get('/profiles/login/')

            # this should always fail. We're expecting an error
            self.assertFalse(True)
        except TemplateDoesNotExist:
            pass

    @override_settings(ROOT_URLCONF='molo.core.tests.test_cas')
    def test_normal_profiles_logout_works_when_cas_enabled(self):
        client = Client()
        User.objects.create_user(
            username='testuser', password='password', email='test@email.com')
        client.login(username='testuser', password='password')

        response = client.get('/profiles/logout/?next=/health/')
        self.assertRedirects(response, '/health/')

    def test_normal_views_after_login_when_cas_enabled(self):
        self.mk_main()

        client = Client()
        User.objects.create_user(
            username='testuser', password='password', email='test@email.com')
        client.login(username='testuser', password='password')

        response = client.get('/')
        self.assertEquals(response.status_code, 200)
