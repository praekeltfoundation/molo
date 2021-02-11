# -*- coding: utf-8 -*-
from datetime import date
from django.utils import timezone
from django.urls import re_path, include
from django.contrib.auth.models import User
from django.core.cache import cache
from django.contrib.auth.tokens import default_token_generator

from django.urls import reverse
from django.http import QueryDict
from django.test import TestCase, override_settings, Client

from molo.profiles.forms import (
    RegistrationForm, EditProfileForm,
    ProfilePasswordChangeForm, ForgotPasswordForm)
from molo.profiles.models import (
    SecurityQuestion, SecurityAnswer,
    UserProfile, SecurityQuestionIndexPage, UserProfilesSettings
)
from molo.core.models import Main, FooterPage, Languages, SiteLanguageRelation

from molo.core.tests.base import MoloTestCaseMixin

from wagtail.core.models import Site

from bs4 import BeautifulSoup

from django.contrib import admin
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls


urlpatterns = [
    re_path(r'^django-admin/', admin.site.urls),
    re_path(r'^admin/', include(wagtailadmin_urls)),
    re_path(r'', include('molo.core.urls')),
    re_path(r'^profiles/', include((
        'molo.profiles.urls', 'molo.profiles'), namespace='molo.profiles')),
    re_path('^', include('django.contrib.auth.urls')),
    re_path(r'', include(wagtail_urls)),
]

DEFAULT_MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'molo.core.middleware.ForceDefaultLanguageMiddleware',
    'molo.core.middleware.SetSiteMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'wagtail.contrib.redirects.middleware.RedirectMiddleware',

    'molo.core.middleware.AdminLocaleMiddleware',
    'molo.core.middleware.NoScriptGASessionMiddleware',

    'molo.core.middleware.MoloGoogleAnalyticsMiddleware',
    'molo.core.middleware.MultiSiteRedirectToHomepage',
]


@override_settings(
    ROOT_URLCONF='molo.profiles.tests.test_views', LOGIN_URL='/login/')
@override_settings(ENABLE_SSO=False)
@override_settings(MIDDLEWARE=DEFAULT_MIDDLEWARE)
class RegistrationViewTest(TestCase, MoloTestCaseMixin):

    def setUp(self):
        cache.clear()
        self.mk_main()
        self.client = Client()
        self.main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)
        self.mk_main2()
        self.main2 = Main.objects.all().last()
        self.language_setting2 = Languages.objects.create(
            site_id=self.main2.get_site().pk)
        self.english2 = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting2,
            locale='en',
            is_active=True)
        self.security_index = SecurityQuestionIndexPage(
            title='Security Questions',
            slug='security_questions',
        )
        self.security_index2 = SecurityQuestionIndexPage(
            title='Security Questions',
            slug='security_questions_2',
        )
        self.main.add_child(instance=self.security_index)
        self.security_index.save()
        self.main2.add_child(instance=self.security_index2)
        self.security_index2.save()
        self.question = SecurityQuestion(
            title="How old are you?",
            slug="how-old-are-you",
        )
        self.security_index.add_child(instance=self.question)
        self.question.save()

    def test_register_view(self):
        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertTrue(isinstance(response.context['form'], RegistrationForm))

    def test_password_auto_complete(self):
        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertContains(response, 'autocomplete="off"')

        response = self.client.get(reverse('molo.profiles:auth_login'))
        self.assertContains(response, 'autocomplete="off"')

    def test_register_view_invalid_form(self):
        # NOTE: empty form submission
        response = self.client.post(reverse('molo.profiles:user_register'), {
        })
        self.assertFormError(
            response, 'form', 'username', ['This field is required.'])
        self.assertFormError(
            response, 'form', 'password', ['This field is required.'])

    def test_register_auto_login(self):
        # Not logged in, redirects to login page
        response = self.client.get(reverse('molo.profiles:edit_my_profile'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'],
            '/login/?next=/profiles/edit/myprofile/')

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'testing',
            'password': '1234',
            'terms_and_conditions': True

        })

        # After registration, doesn't redirect
        response = self.client.get(reverse('molo.profiles:edit_my_profile'))
        self.assertEqual(response.status_code, 200)

    def test_superuser_user_can_log_into_any_admin(self):
        self.login()
        response = self.client.post('/admin/login/?next=/admin/', {
            'username': 'superuser',
            'password': 'pass'
        })
        self.assertEqual(response['Location'], '/admin/')
        client = Client(HTTP_HOST=self.site2.hostname)
        response = client.login(username='superuser', password='pass')
        response = client.post('/admin/login/?next=/admin/', {
            'username': 'superuser',
            'password': 'pass'
        })
        self.assertEqual(response['Location'], '/admin/')

    def test_superuser_only_users_from_site_show(self):
        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'testing1',
            'password': '1234',
            'terms_and_conditions': True

        })
        client = Client(HTTP_HOST=self.site2.hostname)
        response = client.post('/profiles/register/', {
            'username': 'testing2',
            'password': '1234',
            'terms_and_conditions': True

        })
        self.login()
        self.client.login(username='superuser', password='pass')
        response = self.client.get('/admin/auth/user/')
        self.assertNotContains(response, 'testing2')
        self.assertContains(response, 'testing1')
        client.login(username='superuser', password='pass')
        response = client.get('/admin/auth/user/')
        self.assertContains(response, 'testing2')
        self.assertNotContains(response, 'testing1')

    def test_login_to_different_registration_site(self):
        self.assertEqual(User.objects.count(), 0)
        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'testing',
            'password': '1234',
            'terms_and_conditions': True

        })
        user = User.objects.all().first()
        self.assertEqual(User.objects.count(), 1)
        self.assertTrue(user.profile)
        self.assertEqual(user.profile.site, self.main.get_site())
        client = Client(HTTP_HOST=self.site2.hostname)
        response = client.post(reverse('molo.profiles:auth_login'), {
            'username': user.username,
            'password': user.password
        })
        # assert that logging into a different site throws permission denied
        self.assertContains(
            response,
            'Your username and password do not match. Please try again.')

    def test_logout(self):
        response = self.client.get('%s?next=%s' % (
            reverse('molo.profiles:auth_logout'),
            reverse('molo.profiles:user_register')))
        self.assertRedirects(response, reverse('molo.profiles:user_register'))

    def test_login(self):
        response = self.client.get(reverse('molo.profiles:auth_login'))
        self.assertContains(response, 'Forgotten your password?')

    def test_warning_message_shown_in_wagtail_if_no_country_code(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.show_mobile_number_field = True
        profile_settings.save()

        User.objects.create_superuser(
            username='testuser', password='password', email='test@email.com')
        self.client.login(username='testuser', password='password')

        response = self.client.get(reverse('wagtailadmin_home'))
        self.assertContains(
            response, 'You have activated mobile number in registration form,'
            ' but you have not added a country calling code for this site.')

    def test_mobile_number_field_exists_in_registration_form(self):
        profile_settings = UserProfilesSettings.for_site(self.main.get_site())

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertNotContains(response, 'ENTER YOUR MOBILE NUMBER')

        profile_settings.show_mobile_number_field = True
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertNotContains(response, 'ENTER YOUR MOBILE NUMBER')

        profile_settings.country_code = '+27'
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertContains(response, 'ENTER YOUR MOBILE NUMBER')

        # check that it does not show for site 2
        client = Client(HTTP_HOST=self.site2.hostname)
        response = client.get(reverse('molo.profiles:user_register'))
        self.assertNotContains(response, 'ENTER YOUR MOBILE NUMBER')

    def test_email_field_exists_in_registration_form(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertNotContains(response, 'ENTER YOUR EMAIL ADDRESS')

        profile_settings.show_email_field = True
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertContains(response, 'ENTER YOUR EMAIL ADDRESS')

    def test_date_of_birth_field_exists_in_registration_form(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertNotContains(response, 'SELECT DATE OF BIRTH')

        profile_settings.activate_dob = True
        profile_settings.capture_dob_on_reg = True
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertContains(response, 'SELECT DATE OF BIRTH')

    def test_display_name_field_exists_in_registration_form(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertNotContains(response, 'CHOOSE A DISPLAY NAME')

        profile_settings.activate_display_name = True
        profile_settings.capture_display_name_on_reg = True
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertContains(response, 'CHOOSE A DISPLAY NAME')

    def test_gender_field_exists_in_registration_form(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertNotContains(response, 'I IDENTIFY MY GENDER AS:')

        profile_settings.activate_gender = True
        profile_settings.capture_gender_on_reg = True
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertContains(response, 'I IDENTIFY MY GENDER AS:')

    def test_location_field_exists_in_registration_form(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertNotContains(response, 'WHERE DO YOU LIVE?')

        profile_settings.activate_location = True
        profile_settings.capture_location_on_reg = True
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertContains(response, 'WHERE DO YOU LIVE?')

    def test_education_level_field_exists_in_registration_form(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertNotContains(response, 'WHAT IS YOUR HIGHEST '
                                         'LEVEL OF EDUCATION?')

        profile_settings.activate_education_level = True
        profile_settings.capture_education_level_on_reg = True
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertContains(response, 'WHAT IS YOUR HIGHEST '
                                      'LEVEL OF EDUCATION?')

    def test_mobile_number_field_is_optional(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.show_mobile_number_field = True
        profile_settings.mobile_number_required = False
        profile_settings.country_code = '+27'
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'mobile_number': '',
            'terms_and_conditions': True
        })
        self.assertEqual(response.status_code, 302)

    def test_mobile_number_field_is_required(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.show_mobile_number_field = True
        profile_settings.mobile_number_required = True
        profile_settings.country_code = '+27'
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'terms_and_conditions': True
        })
        self.assertFormError(
            response, 'form', 'mobile_number', ['This field is required.'])

    def test_email_field_is_required(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.show_email_field = True
        profile_settings.email_required = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'terms_and_conditions': True
        })
        self.assertFormError(
            response, 'form', 'email', ['This field is required.'])

    def test_display_name_field_is_required(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.activate_display_name = True
        profile_settings.capture_display_name_on_reg = True
        profile_settings.display_name_required = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'foo',
            'password': '1234',
            'terms_and_conditions': True
        })
        self.assertFormError(
            response, 'form', 'alias', ['This field is required.'])

    def test_display_name_is_not_required(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.activate_display_name = True
        profile_settings.capture_display_name_on_reg = True
        profile_settings.display_name_required = False
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'terms_and_conditions': True
        })

        # When successful
        response = self.client.get(reverse('molo.profiles:registration_done'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Thank you for joining!')

    def test_date_of_birth_field_is_required(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.activate_dob = True
        profile_settings.capture_dob_on_reg = True
        profile_settings.dob_required = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'foo',
            'password': '1234',
            'terms_and_conditions': True
        })
        self.assertFormError(
            response, 'form', 'date_of_birth', ['This field is required.'])

    def test_date_of_birth_field_not_required(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.activate_location = True
        profile_settings.capture_location_on_reg = True
        profile_settings.dob_required = False
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'terms_and_conditions': True
        })
        self.assertEqual(response.status_code, 302)

        # When successful
        response = self.client.get(reverse('molo.profiles:registration_done'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Thank you for joining!')

    def test_gender_field_is_required(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.activate_gender = True
        profile_settings.capture_gender_on_reg = True
        profile_settings.gender_required = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'foo',
            'password': '1234',
            'terms_and_conditions': True
        })
        self.assertFormError(
            response, 'form', 'gender', ['This field is required.'])

    def test_gender_not_required(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.activate_gender = True
        profile_settings.capture_gender_on_reg = True
        profile_settings.gender_required = False
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'terms_and_conditions': True
        })

        # When successful
        response = self.client.get(reverse('molo.profiles:registration_done'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Thank you for joining!')

    def test_location_field_is_required(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.activate_location = True
        profile_settings.capture_location_on_reg = True
        profile_settings.location_required = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'foo',
            'password': '1234',
            'terms_and_conditions': True
        })
        self.assertFormError(
            response, 'form', 'location', ['This field is required.'])

    def test_location_not_required(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.activate_location = True
        profile_settings.capture_location_on_reg = True
        profile_settings.location_required = False
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'terms_and_conditions': True
        })

        # When successful
        response = self.client.get(reverse('molo.profiles:registration_done'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Thank you for joining!')

    def test_education_level_field_is_required(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.activate_education_level = True
        profile_settings.capture_education_level_on_reg = True
        profile_settings.activate_education_level_required = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'foo',
            'password': '1234',
            'terms_and_conditions': True
        })
        self.assertFormError(
            response, 'form', 'education_level', ['This field is required.'])

    def test_education_level_not_required(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.activate_education_level = True
        profile_settings.capture_education_level_on_reg = True
        profile_settings.activate_education_level_required = False
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'terms_and_conditions': True
        })

        # When successful
        response = self.client.get(reverse('molo.profiles:registration_done'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Thank you for joining!')

    def test_mobile_num_is_required_but_show_mobile_num_field_is_false(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.show_mobile_number_field = False
        profile_settings.mobile_number_required = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'terms_and_conditions': True
        })
        self.assertEqual(response.status_code, 302)

    def test_email_is_required_but_show_email_field_is_false(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.show_email_field = False
        profile_settings.email_required = True
        profile_settings.save()
        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'terms_and_conditions': True
        })
        self.assertEqual(response.status_code, 302)

    def test_invalid_mobile_number(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.show_mobile_number_field = True
        profile_settings.mobile_number_required = True
        profile_settings.country_code = '+27'
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'mobile_number': '27785577743'
        })
        self.assertFormError(
            response, 'form', 'mobile_number', ['Enter a valid phone number.'])

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'mobile_number': '+2785577743'
        })
        self.assertFormError(
            response, 'form', 'mobile_number', ['Enter a valid phone number.'])
        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'mobile_number': '+089885577743'
        })
        self.assertFormError(
            response, 'form', 'mobile_number', ['Enter a valid phone number.'])

    def test_invalid_email(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.show_email_field = True
        profile_settings.email_required = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'email': 'example@'
        })
        self.assertFormError(
            response, 'form', 'email', ['Enter a valid email address.'])

    def test_valid_mobile_number(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)
        profile_settings.show_mobile_number_field = True
        profile_settings.mobile_number_required = True
        profile_settings.country_code = '+27'
        profile_settings.save()
        self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'mobile_number': '0784500003',
            'terms_and_conditions': True
        })
        self.assertEqual(UserProfile.objects.get().mobile_number,
                         '+27784500003')

    def test_valid_mobile_number_edit_profile(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)
        profile_settings.show_mobile_number_field = True
        profile_settings.mobile_number_required = True
        profile_settings.country_code = '+27'
        profile_settings.save()
        self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'mobile_number': '0784500003',
            'terms_and_conditions': True
        })
        self.assertEqual(UserProfile.objects.get().mobile_number,
                         '+27784500003')
        self.client.post(reverse('molo.profiles:edit_my_profile'), {
            'mobile_number': '0784500004',
        })
        self.assertEqual(UserProfile.objects.get().mobile_number,
                         '+27784500004')

    def test_valid_mobile_number_with_plus(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)
        profile_settings.show_mobile_number_field = True
        profile_settings.mobile_number_required = True
        profile_settings.country_code = '+27'
        profile_settings.save()
        self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'mobile_number': '+27784500003',
            'terms_and_conditions': True
        })
        self.assertEqual(UserProfile.objects.get().mobile_number,
                         '+27784500003')
        self.client.post(reverse('molo.profiles:edit_my_profile'), {
            'mobile_number': '0784500004',
        })
        self.assertEqual(UserProfile.objects.get().mobile_number,
                         '+27784500004')

    def test_valid_mobile_number_without_zero(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)
        profile_settings.show_mobile_number_field = True
        profile_settings.mobile_number_required = True
        profile_settings.country_code = '+27'
        profile_settings.save()
        self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'mobile_number': '784500003',
            'terms_and_conditions': True
        })
        self.assertEqual(UserProfile.objects.get().mobile_number,
                         '+27784500003')
        self.client.post(reverse('molo.profiles:edit_my_profile'), {
            'mobile_number': '+27784500005',
        })
        self.assertEqual(UserProfile.objects.get().mobile_number,
                         '+27784500005')

    def test_valid_email(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.show_email_field = True
        profile_settings.email_required = True
        profile_settings.save()
        self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'email': 'example@foo.com',
            'terms_and_conditions': True
        })
        self.assertEqual(UserProfile.objects.get().user.email,
                         'example@foo.com')

    def test_email_or_phone_not_allowed_in_username(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.prevent_phone_number_in_username = True
        profile_settings.prevent_email_in_username = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test@test.com',
            'password': '1234',
            'email': 'example@foo.com',
            'terms_and_conditions': True
        })
        expected_validation_message = "Sorry, but that is an invalid " \
                                      "username. Please don&#x27;t use " \
                                      "your phone number or email address " \
                                      "in your username."

        self.assertContains(response, expected_validation_message)

    def test_email_not_allowed_in_username(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.prevent_email_in_username = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test@test.com',
            'password': '1234',
            'email': 'example@foo.com',
            'terms_and_conditions': True
        })

        expected_validation_message = "Sorry, but that is an invalid" \
                                      " username. Please don&#x27;t use" \
                                      " your email address in your" \
                                      " username."

        self.assertContains(response, expected_validation_message)

    def test_ascii_code_not_allowed_in_username(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.prevent_email_in_username = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'A bad username 😁',
            'password': '1234',
            'email': 'example@foo.com',
            'terms_and_conditions': True
        })

        expected_validation_message = "This value must contain only letters,"\
                                      " numbers and underscores."
        self.assertContains(response, expected_validation_message)

    def test_phone_number_not_allowed_in_username(self):
        site = Site.objects.first()
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.prevent_phone_number_in_username = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': '021123123123',
            'password': '1234',
            'email': 'example@foo.com',
            'terms_and_conditions': True
        })
        expected_validation_message = "Sorry, but that is an invalid" \
                                      " username. Please don&#x27;t use" \
                                      " your phone number in your username."

        self.assertContains(response, expected_validation_message)

    def test_security_questions(self):
        # setup for site 1
        profile_settings = UserProfilesSettings.for_site(self.main.get_site())
        sq = SecurityQuestion(
            title="What is your name?",
            slug="what-is-your-name",
        )
        self.security_index.add_child(instance=sq)
        sq.save()
        profile_settings.show_security_question_fields = True
        profile_settings.security_questions_required = True
        profile_settings.save()

        # setup for site 2
        profile_settings2 = UserProfilesSettings.for_site(
            self.main2.get_site())
        sq2 = SecurityQuestion(
            title="Who are you?",
            slug="who-are-you",
        )
        self.security_index2.add_child(instance=sq2)
        sq2.save()
        profile_settings2.show_security_question_fields = True
        profile_settings2.security_questions_required = True
        profile_settings2.save()

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertContains(response, "What is your name")
        self.assertNotContains(response, "Who are you")

        # register with security questions
        response = self.client.post(
            reverse("molo.profiles:user_register"),
            {
                "username": "tester",
                "password": "0000",
                "question_0": "answer",
                'terms_and_conditions': True
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)

        client = Client(HTTP_HOST=self.site2.hostname)
        response = client.get(reverse('molo.profiles:user_register'))
        self.assertNotContains(response, "What is your name")
        self.assertContains(response, "Who are you")

        # register with security questions
        response = client.post(
            reverse("molo.profiles:user_register"),
            {
                "username": "tester",
                "password": "0000",
                "question_0": "answer",
                'terms_and_conditions': True
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)


@override_settings(
    ROOT_URLCONF='molo.profiles.tests.test_views')
class RegistrationDone(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.mk_main2()
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')
        self.client = Client()
        self.client.login(username='tester', password='tester')

    def test_date_of_birth_on_done(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.activate_dob = True
        profile_settings.capture_dob_on_reg = False
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:registration_done'))
        self.assertContains(response, 'Let us know more about yourself '
                            'to get access to exclusive content.')
        self.assertContains(response, 'Thank you for joining!')

        response = self.client.post(reverse(
            'molo.profiles:registration_done'), {
            'date_of_birth': '2000-01-01',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='tester')
        self.assertEqual(user.profile.date_of_birth, date(2000, 1, 1))

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

        # test not required for site 2
        profile_settings2 = UserProfilesSettings.for_site(
            self.main2.get_site())
        profile_settings2.activate_dob = False
        profile_settings2.save()
        client = Client(HTTP_HOST=self.main2.get_site().hostname)
        client.post('/profiles/register/', {
            'username': 'testing2',
            'password': '1234',
            'terms_and_conditions': True

        })
        response = client.get(reverse('molo.profiles:registration_done'))
        self.assertNotContains(response, "SELECT DATE OF BIRTH")

    def test_display_name_on_done(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.activate_display_name = True
        profile_settings.capture_display_name_on_reg = False
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:registration_done'))
        self.assertContains(response, 'Let us know more about yourself '
                            'to get access to exclusive content.')
        self.assertContains(response, 'Thank you for joining!')

        response = self.client.post(reverse(
            'molo.profiles:registration_done'), {
            'alias': 'foo',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='tester')
        self.assertEqual(user.profile.alias, ('foo'))

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_gender_on_done(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.activate_gender = True
        profile_settings.capture_gender_on_reg = False
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:registration_done'))
        self.assertContains(response, 'Let us know more about yourself '
                            'to get access to exclusive content.')
        self.assertContains(response, 'Thank you for joining!')

        response = self.client.post(reverse(
            'molo.profiles:registration_done'), {
            'gender': 'male',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='tester')
        self.assertEqual(user.profile.gender, ('male'))

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_location_on_done(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.activate_location = True
        profile_settings.capture_location_on_reg = False
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:registration_done'))
        self.assertContains(response, 'Let us know more about yourself '
                            'to get access to exclusive content.')
        self.assertContains(response, 'Thank you for joining!')
        response = self.client.post(reverse(
            'molo.profiles:registration_done'), {
            'location': 'mlazi',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='tester')
        self.assertEqual(user.profile.location, ('mlazi'))

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_education_level_on_done(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.activate_education_level = True
        profile_settings.capture_education_level_on_reg = False
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:registration_done'))
        self.assertContains(response, 'Let us know more about yourself '
                            'to get access to exclusive content.')
        self.assertContains(response, 'Thank you for joining!')
        response = self.client.post(reverse(
            'molo.profiles:registration_done'), {
            'education_level': 'level 0',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='tester')
        self.assertEqual(user.profile.education_level, ('level 0'))

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


@override_settings(
    ROOT_URLCONF='molo.profiles.tests.test_views')
class TestTermsAndConditions(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.footer = FooterPage(
            title='terms and conditions', slug='terms-and-conditions')
        self.footer_index.add_child(instance=self.footer)
        self.footer.save()
        self.security_index = SecurityQuestionIndexPage(
            title='Security Questions',
            slug='security_questions',
        )
        self.main.add_child(instance=self.security_index)
        self.security_index.save()
        self.question = SecurityQuestion(
            title="How old are you?",
            slug="how-old-are-you",
        )
        self.security_index.add_child(instance=self.question)
        self.question.save()

    def test_terms_and_conditions_linked_to_terms_and_conditions_page(self):
        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertNotContains(
            response,
            '<a href="/footer-pages/terms-and-conditions/"'
            ' for="id_terms_and_conditions" class="profiles__terms">'
            'I accept the Terms and Conditions</a>')
        self.assertContains(
            response,
            '<label for="id_terms_and_conditions"'
            ' class="profiles__terms">'
            'I accept the Terms and Conditions</label>')

        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.terms_and_conditions = self.footer
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertContains(
            response,
            '<a href="/footers-main-1/terms-and-conditions/"'
            ' for="id_terms_and_conditions" class="profiles__terms">'
            'I accept the Terms and Conditions</a>')


@override_settings(
    ROOT_URLCONF='molo.profiles.tests.test_views',
    TEMPLATE_CONTEXT_PROCESSORS=[
        'molo.profiles.context_processors.get_profile_data',
    ])
class MyProfileViewTest(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')
        # Update the userprofile without touching (and caching) user.profile
        UserProfile.objects.filter(user=self.user).update(alias='The Alias')
        self.client = Client()

    def test_view(self):
        self.client.login(username='tester', password='tester')
        response = self.client.get(reverse('molo.profiles:view_my_profile'))
        self.assertContains(response, 'tester')
        self.assertContains(response, 'The Alias')

        self.assertTrue(isinstance(
            response.context['password_change_form'],
            ProfilePasswordChangeForm,
        ))


@override_settings(
    ROOT_URLCONF='molo.profiles.tests.test_views', LOGIN_URL='/login/')
class LoginTestView(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='1234')
        # Update the userprofile without touching (and caching) user.profile
        UserProfile.objects.filter(user=self.user).update(alias='The Alias')
        self.client = Client()

    def test_login_success(self):
        self.client.login(username='tester', password='1234')

        response = self.client.get(reverse('molo.profiles:auth_login'))
        self.assertContains(response, 'value="/profiles/login-success/"')

        response = self.client.get(reverse('molo.profiles:login_success'))
        self.assertContains(response, 'Welcome Back!')

    def test_login_success_redirects(self):
        self.client.login(username='tester', password='1234')

        response = self.client.post(
            reverse('molo.profiles:auth_login'),
            data={'username': 'tester', 'password': '1234',
                  'next': '/profiles/login-success/'},
            follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response, reverse('molo.profiles:login_success'))


@override_settings(
    ROOT_URLCONF='molo.profiles.tests.test_views')
class MyProfileEditTest(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.mk_main2()
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')
        self.client = Client()
        self.client.login(username='tester', password='tester')

    def test_view(self):
        response = self.client.get(reverse('molo.profiles:edit_my_profile'))
        form = response.context['form']
        self.assertTrue(isinstance(form, EditProfileForm))

    def test_update_alias_only(self):
        response = self.client.post(reverse('molo.profiles:edit_my_profile'),
                                    {
            'alias': 'foo'
        })
        self.assertRedirects(
            response, reverse('molo.profiles:view_my_profile'))
        self.assertEqual(UserProfile.objects.get(user=self.user).alias,
                         'foo')

    def test_gender_field_exists_in_edit_form(self):
        profile_settings = UserProfilesSettings.for_site(self.main.get_site())
        response = self.client.get(reverse('molo.profiles:edit_my_profile'))
        self.assertNotContains(response, 'Update your gender:')

        profile_settings.activate_gender = True
        profile_settings.gender_required = True
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:edit_my_profile'))
        self.assertContains(response, 'Update your gender:')

        client = Client(HTTP_HOST=self.main2.get_site().hostname)
        client.post('/profiles/register/', {
            'username': 'testing2',
            'password': '1234',
            'terms_and_conditions': True

        })
        response = client.get(reverse('molo.profiles:edit_my_profile'))
        self.assertNotContains(response, 'Update your gender:')

    def test_location_field_exists_in_edit_form(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        response = self.client.get(reverse('molo.profiles:edit_my_profile'))
        self.assertNotContains(response, 'Update where you live:')

        profile_settings.activate_location = True
        profile_settings.location_required = True
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:edit_my_profile'))
        self.assertContains(response, 'Update where you live:')

    def test_education_level_field_exists_in_edit_form(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        response = self.client.get(reverse('molo.profiles:edit_my_profile'))
        self.assertNotContains(response, 'Update your Education Level:')

        profile_settings.activate_education_level = True
        profile_settings.activate_education_level_required = True
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:edit_my_profile'))
        self.assertContains(response, 'Update your Education Level:')

    def test_email_showing_in_edit_view(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.show_email_field = True
        profile_settings.email_required = True
        profile_settings.save()
        response = self.client.get(reverse('molo.profiles:edit_my_profile'))
        self.assertContains(response, 'tester@example.com')

    # Test for update with dob only is in ProfileDateOfBirthEditTest

    def test_update_no_input(self):
        response = self.client.post(reverse('molo.profiles:edit_my_profile'),
                                    {})
        self.assertEqual(response.status_code, 302)

    def test_update_alias_and_dob(self):
        response = self.client.post(reverse('molo.profiles:edit_my_profile'),
                                    {
            'alias': 'foo',
            'date_of_birth': '2000-01-01'
        })
        self.assertRedirects(
            response, reverse('molo.profiles:view_my_profile'))
        self.assertEqual(UserProfile.objects.get(user=self.user).alias,
                         'foo')
        self.assertEqual(UserProfile.objects.get(user=self.user).date_of_birth,
                         date(2000, 1, 1))

    def test_update_mobile_number(self):
        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'mobile_number': '+27788888813'})
        self.assertRedirects(
            response, reverse('molo.profiles:view_my_profile'))
        self.assertEqual(UserProfile.objects.get(user=self.user).mobile_number,
                         '+27788888813')

    def test_update_gender(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)
        profile_settings.activate_gender = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'gender': 'male'})
        self.assertRedirects(
            response, reverse('molo.profiles:view_my_profile'))
        self.assertEqual(UserProfile.objects.get(user=self.user).gender,
                         'male')

    def test_update_location(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)
        profile_settings.activate_location = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'location': 'mlazi'})
        self.assertRedirects(
            response, reverse('molo.profiles:view_my_profile'))
        self.assertEqual(UserProfile.objects.get(user=self.user).location,
                         'mlazi')

    def test_update_education_level(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)
        profile_settings.activate_education_level = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'education_level': 'level0'})
        self.assertRedirects(
            response, reverse('molo.profiles:view_my_profile'))
        self.assertEqual(
            UserProfile.objects.get(user=self.user).education_level,
            'level0')

    def test_update_email(self):
        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'email': 'example@foo.com'})
        self.assertRedirects(
            response, reverse('molo.profiles:view_my_profile'))
        self.assertEqual(UserProfile.objects.get(user=self.user).user.email,
                         'example@foo.com')

    def test_update_when_email_optional(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.show_email_field = True
        profile_settings.email_required = False
        profile_settings.save()
        # user removes their mobile number
        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'email': ''})
        self.assertRedirects(
            response, reverse('molo.profiles:view_my_profile'))

    def test_update_when_email_required(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.show_email_field = True
        profile_settings.email_required = True
        profile_settings.save()
        # user removes their mobile number
        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'email': ''})
        self.assertFormError(
            response, 'form', 'email', ['This field is required.'])

    def test_update_when_mobile_number_optional(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.show_mobile_number_field = True
        profile_settings.mobile_number_required = False
        profile_settings.country_code = '+27'
        profile_settings.save()
        # user removes their mobile number
        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'mobile_number': ''})
        self.assertRedirects(
            response, reverse('molo.profiles:view_my_profile'))

    def test_update_when_mobile_number_required(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.show_mobile_number_field = True
        profile_settings.mobile_number_required = True
        profile_settings.country_code = '+27'
        profile_settings.save()
        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'mobile_number': ''})
        self.assertFormError(
            response, 'form', 'mobile_number', ['This field is required.'])

    def test_gender_field_is_required_on_edit_form(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.activate_gender = True
        profile_settings.gender_required = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'gender': ''})
        self.assertFormError(
            response, 'form', 'gender', ['This field is required.'])

    def test_gender_not_required_on_edit_form(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.activate_gender = True
        profile_settings.gender_required = False
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'gender': ''})

        self.assertRedirects(
            response, reverse('molo.profiles:view_my_profile'))

        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'gender': 'male'})
        response = self.client.get(reverse('molo.profiles:view_my_profile'))
        self.assertContains(response, 'male')

    def test_location_field_is_required_on_edit_form(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.activate_location = True
        profile_settings.location_required = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'location': ''})
        self.assertFormError(
            response, 'form', 'location', ['This field is required.'])

    def test_location_not_required_on_edit_form(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.activate_location = True
        profile_settings.location_required = False
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'location': ''})

        self.assertRedirects(
            response, reverse('molo.profiles:view_my_profile'))

        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'location': 'mlazi'})
        response = self.client.get(reverse('molo.profiles:view_my_profile'))
        self.assertContains(response, 'mlazi')

    def test_education_level_field_is_required_on_edit_form(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.activate_education_level = True
        profile_settings.activate_education_level_required = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'education_level': ''})
        self.assertFormError(
            response, 'form', 'education_level', ['This field is required.'])

    def test_education_level_not_required_on_edit_form(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.activate_education_level = True
        profile_settings.activate_education_level_required = False
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'education_level': ''})

        self.assertRedirects(
            response, reverse('molo.profiles:view_my_profile'))

        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'education_level': 'level0'})
        response = self.client.get(reverse('molo.profiles:view_my_profile'))
        self.assertContains(response, 'level0')

    def test_gender_required_location_not_required(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)
        profile_settings.activate_location = True
        profile_settings.activate_gender = True
        profile_settings.gender_required = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'gender': 'male'})
        self.assertRedirects(
            response, reverse('molo.profiles:view_my_profile'))

        response = self.client.get(reverse('molo.profiles:view_my_profile'))
        self.assertContains(response, 'male')


@override_settings(
    ROOT_URLCONF='molo.profiles.tests.test_views')
class ProfileDateOfBirthEditTest(MoloTestCaseMixin, TestCase):

    def setUp(self):
        self.mk_main()
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')
        self.client = Client()
        self.client.login(username='tester', password='tester')

    def test_view(self):
        response = self.client.get(
            reverse('molo.profiles:edit_my_profile'))
        form = response.context['form']
        self.assertTrue(isinstance(form, EditProfileForm))

    def test_update_date_of_birth(self):
        response = self.client.post(reverse(
            'molo.profiles:edit_my_profile'), {
            'date_of_birth': '2000-01-01',
        })
        self.assertRedirects(
            response, reverse('molo.profiles:view_my_profile'))
        self.assertEqual(UserProfile.objects.get(user=self.user).date_of_birth,
                         date(2000, 1, 1))


@override_settings(
    ROOT_URLCONF='molo.profiles.tests.test_views')
class ProfilePasswordChangeViewTest(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='0000')
        self.client = Client()
        self.client.login(username='tester', password='0000')

    def test_view(self):
        response = self.client.get(
            reverse('molo.profiles:profile_password_change'))
        form = response.context['form']
        self.assertTrue(isinstance(form, ProfilePasswordChangeForm))

    def test_update_invalid_old_password(self):
        response = self.client.post(
            reverse('molo.profiles:profile_password_change'), {
                'old_password': '1234',
                'new_password': '4567',
                'confirm_password': '4567',
            })
        [message] = response.context['messages']
        self.assertEqual(message.message, 'The old password is incorrect.')

    def test_update_passwords_not_matching(self):
        response = self.client.post(
            reverse('molo.profiles:profile_password_change'), {
                'old_password': '0000',
                'new_password': '1234',
                'confirm_password': '4567',
            })
        form = response.context['form']
        [error] = form.non_field_errors().as_data()
        self.assertEqual(error.message, 'New passwords do not match.')

    def test_update_passwords(self):
        response = self.client.post(
            reverse('molo.profiles:profile_password_change'), {
                'old_password': '0000',
                'new_password': '1234',
                'confirm_password': '1234',
            })
        self.assertEqual(response['location'], '/profiles/view/myprofile/')
        # Avoid cache by loading from db
        user = User.objects.get(pk=self.user.pk)
        self.assertTrue(user.check_password('1234'))


@override_settings(
    ROOT_URLCONF="molo.profiles.tests.test_views",
)
class ForgotPasswordViewTest(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.client = Client()
        self.user = User.objects.create_user(
            username="tester",
            email="tester@example.com",
            password="0000")
        self.main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)

        self.security_index = SecurityQuestionIndexPage(
            title='Security Questions',
            slug='security_questions',
        )
        self.main.add_child(instance=self.security_index)
        self.security_index.save()
        self.question = SecurityQuestion(
            title="How old are you?",
            slug="how-old-are-you",
        )
        self.security_index.add_child(instance=self.question)
        self.question.save()

        # create answers for this user
        self.a1 = SecurityAnswer.objects.create(
            user=self.user.profile, question=self.question, answer="20"
        )

    def test_view(self):
        response = self.client.get(
            reverse("molo.profiles:forgot_password"))
        form = response.context["form"]
        self.assertTrue(isinstance(form, ForgotPasswordForm))

    def test_unidentified_user_gets_error(self):
        error_message = ("The username that you entered appears to be invalid."
                         " Please try again.")
        response = self.client.post(
            reverse("molo.profiles:forgot_password"), {
                "username": "bogus",
                "question_0": "20",
            }
        )
        self.assertContains(response, error_message)

    def test_suspended_user_gets_error(self):
        error_message = "The username and security question(s) combination " \
                        "do not match."
        self.user.is_active = False
        self.user.save()
        response = self.client.post(
            reverse("molo.profiles:forgot_password"), {
                "username": "tester",
                "question_0": "20",
            }
        )
        self.assertContains(response, error_message)
        self.user.is_active = True
        self.user.save()

    def test_incorrect_security_answer_gets_error(self):
        error_message = "The username and security question(s) combination " \
                        "do not match."
        response = self.client.post(
            reverse("molo.profiles:forgot_password"), {
                "username": "tester",
                "question_0": "21",
            }
        )
        self.assertContains(response, error_message)

    def test_too_many_retries_result_in_error(self):
        error_message = ("Too many attempts")
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        # post more times than the set number of retries
        for i in range(profile_settings.password_recovery_retries + 5):
            response = self.client.post(
                reverse("molo.profiles:forgot_password"), {
                    "username": self.user.username,
                    "question_0": "200",
                }
            )
        self.assertContains(response, error_message)

    def test_correct_username_and_answer_results_in_redirect(self):
        response = self.client.post(
            reverse("molo.profiles:forgot_password"), {
                "username": "tester",
                "question_0": "20",
            },
            follow=True
        )
        self.assertContains(response, "Reset PIN")

    def test_user_with_no_security_questions(self):
        # register without security questions
        response = self.client.post(
            reverse("molo.profiles:user_register"),
            {
                "username": "newuser",
                "password": "0000",
                'terms_and_conditions': True
            },
            follow=True
        )
        profile_settings = UserProfilesSettings.for_site(self.main.get_site())
        sq = SecurityQuestion(
            title="What is your name?",
            slug="what-is-your-name",
        )
        self.security_index.add_child(instance=sq)
        sq.save()

        sq2 = SecurityQuestion(
            title="What is your pet name?",
            slug="what-is-your-pet-name",
        )
        self.security_index.add_child(instance=sq2)
        sq2.save()

        profile_settings.show_security_question_fields = True
        profile_settings.security_questions_required = False
        profile_settings.save()

        response = self.client.post(
            reverse("molo.profiles:forgot_password"), {
                "username": "newuser",
                "question_0": "saeed",
                "question_1": "pishy",
            }
        )
        self.assertContains(
            response,
            "There are no security questions"
            " stored against your profile.")


class SecurityQuestionsTest(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.client = Client()
        self.questions_section = self.mk_section(
            self.section_index, title='Security Questions')

        # Creates Main language
        self.main = Main.objects.all().first()
        self.language_setting, _ = Languages.objects.get_or_create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)
        self.french = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='fr',
            is_active=True)

        self.security_index = SecurityQuestionIndexPage(
            title='Security Questions',
            slug='security_questions',
        )
        self.main.add_child(instance=self.security_index)
        self.security_index.save()

        self.q1 = SecurityQuestion(
            title="How old are you?",
            slug="how-old-are-you",
        )
        self.security_index.add_child(instance=self.q1)
        self.q1.save()

        self.q2 = SecurityQuestion(
            title="What is your name?",
            slug="what-is-your-name",
            latest_revision_created_at=timezone.now()
        )
        self.security_index.add_child(instance=self.q2)
        self.q2.save()
        profile_settings = UserProfilesSettings.for_site(self.main.get_site())
        profile_settings.show_security_question_fields = True
        profile_settings.save()

    def test_deleting_security_question(self):
        User.objects.create_superuser(
            username='testuser', password='password', email='test@email.com')
        self.client.login(username='testuser', password='password')

        # delete a security question that doesn't have answer linked to
        response = self.client.post(
            reverse('wagtailadmin_pages:delete', args=(self.q2.id, )))
        # Check that the security question is gone
        self.assertFalse(
            SecurityQuestion.objects.filter(
                slug='what-is-your-name').exists())

        response = self.client.post(
            reverse("molo.profiles:user_register"),
            {
                "username": "tester",
                "password": "0000",
                "question_0": "20",
                'terms_and_conditions': True
            },
            follow=True
        )
        self.client.login(username='testuser', password='password')
        # delete a security question that has a security answer linked to
        response = self.client.post(
            reverse('wagtailadmin_pages:delete', args=(self.q1.id, )))

        self.assertContains(response, "Users have used")
        self.assertContains(
            response, "<strong>%s</strong>" % self.q1.title, html=True)

        # Check that the security question exists
        self.assertTrue(
            SecurityQuestion.objects.filter(
                slug='how-old-are-you').exists())


class TranslatedSecurityQuestionsTest(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.client = Client()
        self.questions_section = self.mk_section(
            self.section_index, title='Security Questions')

        # Creates Main language
        self.main = Main.objects.all().first()
        self.language_setting, _ = Languages.objects.get_or_create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)
        self.french = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='fr',
            is_active=True)

        self.security_index = SecurityQuestionIndexPage(
            title='Security Questions',
            slug='security_questions',
        )
        self.main.add_child(instance=self.security_index)
        self.security_index.save()
        self.q1 = SecurityQuestion(
            title="How old are you?",
            slug="how-old-are-you",
        )
        self.security_index.add_child(instance=self.q1)
        self.q1.save()

    def test_translated_question_appears_on_registration(self):
        # make translation for the security question
        fr_question = SecurityQuestion(
            title="How old are you in french",
            slug="how-old-are-you-in-french",
        )
        self.security_index.add_child(instance=fr_question)
        fr_question.language = self.french
        fr_question.translated_pages.add(self.q1)
        fr_question.save_revision().publish()
        self.q1.translated_pages.add(fr_question)
        self.q1.save_revision().publish()
        self.client.get('/locale/fr/')
        response = self.client.get(reverse("molo.profiles:forgot_password"))
        self.assertContains(response, "How old are you in french")

        # switch locale to english and check that the english question
        # is asked
        self.client.get('/locale/en/')
        response = self.client.get(reverse("molo.profiles:forgot_password"))
        self.assertNotContains(response, "How old are you in french")


class ResetPasswordViewTest(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.client = Client()
        self.user = User.objects.create_user(
            username="tester",
            email="tester@example.com",
            password="0000")

        self.main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)

        self.security_index = SecurityQuestionIndexPage(
            title='Security Questions',
            slug='security_questions',
        )
        self.main.add_child(instance=self.security_index)
        self.security_index.save()
        self.question = SecurityQuestion(
            title="How old are you?",
            slug="how-old-are-you",
        )
        self.security_index.add_child(instance=self.question)
        self.question.save()

        # create answers for this user
        self.a1 = SecurityAnswer.objects.create(
            user=self.user.profile, question=self.question, answer="20"
        )

    def test_none_type_security_answer(self):
        self.assertFalse(self.a1.check_answer(None))

    def proceed_to_reset_password_page(self):
        expected_token = default_token_generator.make_token(self.user)
        expected_query_params = QueryDict(mutable=True)
        expected_query_params["user"] = self.user.username
        expected_query_params["token"] = expected_token
        expected_redirect_url = "{0}?{1}".format(
            reverse("molo.profiles:reset_password"),
            expected_query_params.urlencode()
        )

        response = self.client.post(
            reverse("molo.profiles:forgot_password"), {
                "username": self.user.username,
                "question_0": "20",
            }
        )
        self.assertRedirects(response, expected_redirect_url)

        return expected_token, expected_redirect_url

    def test_reset_password_view_pin_mismatch(self):
        expected_token, expected_redirect_url = \
            self.proceed_to_reset_password_page()

        response = self.client.post(expected_redirect_url, {
            "username": self.user.username,
            "token": expected_token,
            "password": "1234",
            "confirm_password": "4321"
        })
        self.assertContains(response, "The two PINs that you entered do not "
                                      "match. Please try again.")

    def test_reset_password_view_requires_query_params(self):
        response = self.client.get(reverse("molo.profiles:reset_password"))
        self.assertEqual(403, response.status_code)

    def test_reset_password_view_invalid_username(self):
        expected_token, expected_redirect_url = \
            self.proceed_to_reset_password_page()

        response = self.client.post(expected_redirect_url, {
            "username": "invalid",
            "token": expected_token,
            "password": "1234",
            "confirm_password": "1234"
        })

        self.assertEqual(403, response.status_code)

    def test_reset_password_view_inactive_user(self):
        expected_token, expected_redirect_url = \
            self.proceed_to_reset_password_page()

        self.user.is_active = False
        self.user.save()

        response = self.client.post(expected_redirect_url, {
            "username": self.user.username,
            "token": expected_token,
            "password": "1234",
            "confirm_password": "1234"
        })

        self.assertEqual(403, response.status_code)

    def test_reset_password_view_invalid_token(self):
        expected_token, expected_redirect_url = \
            self.proceed_to_reset_password_page()

        response = self.client.post(expected_redirect_url, {
            "username": self.user.username,
            "token": "invalid",
            "password": "1234",
            "confirm_password": "1234"
        })

        self.assertEqual(403, response.status_code)

    def test_happy_path(self):
        expected_token, expected_redirect_url = \
            self.proceed_to_reset_password_page()

        response = self.client.post(expected_redirect_url, {
            "username": self.user.username,
            "token": expected_token,
            "password": "1234",
            "confirm_password": "1234"
        })

        self.assertRedirects(
            response,
            reverse("molo.profiles:reset_password_success")
        )

        self.assertTrue(
            self.client.login(username="tester", password="1234")
        )


@override_settings(
    ROOT_URLCONF='molo.profiles.tests.test_views')
class TestDeleteButtonRemoved(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)
        self.login()

        self.security_question_index = SecurityQuestionIndexPage(
            title='Security Questions',
            slug='security-questions')
        self.main.add_child(instance=self.security_question_index)
        self.security_question_index.save_revision().publish()

    def test_delete_button_removed_for_sec_ques_index_page_in_main(self):
        main_page = Main.objects.first()

        response = self.client.get('/admin/pages/{0}/'
                                   .format(str(main_page.pk)))
        self.assertEqual(response.status_code, 200)

        security_q_index_page_title = (
            SecurityQuestionIndexPage.objects.first().title)

        soup = BeautifulSoup(response.content, 'html.parser')
        index_page_rows = soup.find_all('tbody')[0].find_all('tr')

        for row in index_page_rows:
            if row.h2.a.string == security_q_index_page_title:
                self.assertTrue(row.find('a', string='Edit'))
                self.assertFalse(row.find('a', string='Delete'))

    def test_delete_button_removed_from_dropdown_menu_main(self):
        security_q_index_page = SecurityQuestionIndexPage.objects.first()

        response = self.client.get('/admin/pages/{0}/'
                                   .format(str(security_q_index_page.pk)))
        self.assertEqual(response.status_code, 200)

        delete_link = ('<a href="/admin/pages/{0}/delete/" '
                       'title="Delete this page" class="u-link '
                       'is-live ">Delete</a>'
                       .format(str(security_q_index_page.pk)))
        self.assertNotContains(response, delete_link, html=True)

    def test_delete_button_removed_in_edit_menu(self):
        security_q_index_page = SecurityQuestionIndexPage.objects.first()

        response = self.client.get('/admin/pages/{0}/edit/'
                                   .format(str(security_q_index_page.pk)))
        self.assertEqual(response.status_code, 200)

        delete_button = ('<li><a href="/admin/pages/{0}/delete/" '
                         'class="shortcut">Delete</a></li>'
                         .format(str(security_q_index_page.pk)))
        self.assertNotContains(response, delete_button, html=True)
