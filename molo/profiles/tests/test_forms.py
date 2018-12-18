# -*- coding: utf-8 -*-
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User

from molo.profiles.forms import (
    ForgotPasswordForm, RegistrationForm, ProfilePasswordChangeForm, DoneForm)
from molo.core.tests.base import MoloTestCaseMixin
from molo.profiles.models import (SecurityQuestion, SecurityQuestionIndexPage,
                                  UserProfilesSettings)

from wagtail.core.models import Site


class RegisterTestCase(MoloTestCaseMixin, TestCase):

    def setUp(self):
        self.mk_main()
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')

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

    def test_register_username_correct(self):
        form_data = {
            'username': 'Jeyabal@-1',
            'password': '1234',
            'terms_and_conditions': True
        }
        form = RegistrationForm(
            data=form_data,
            questions=[self.question, ]
        )
        self.assertEqual(form.is_valid(), True)

    def test_register_username_incorrect(self):
        form_data = {
            'username': 'Jeyabal#',
            'password': '1234',
            'terms_and_conditions': True

        }
        form = RegistrationForm(
            data=form_data,
            questions=[self.question, ]
        )
        self.assertEqual(form.is_valid(), False)

    def test_register_password_incorrect(self):
        form_data = {
            'username': 'Jeyabal#',
            'password': '12345',
            'terms_and_conditions': True

        }
        form = RegistrationForm(
            data=form_data,
            questions=[self.question, ]
        )
        self.assertEqual(form.is_valid(), False)

    def test_password_change_incorrect(self):
        form_data = {
            'old_password': '123',
            'new_password': 'jey123',
            'confirm_password': 'jey123',
        }
        form = ProfilePasswordChangeForm(
            data=form_data,
        )
        self.assertEqual(form.is_valid(), False)

    def test_password_change_correct(self):
        form_data = {
            'old_password': '1234',
            'new_password': '3456',
            'confirm_password': '3456',
        }
        form = ProfilePasswordChangeForm(
            data=form_data,
        )
        self.assertEqual(form.is_valid(), True)

    def test_username_exists(self):
        User.objects.create_user(
            'testing', 'testing@example.com', 'testing')
        form_data = {
            'username': 'testing',
            'password': '1234',
        }
        form = RegistrationForm(
            data=form_data,
            questions=[self.question, ]
        )
        self.assertFalse(form.is_valid())
        [validation_error] = form.errors.as_data()['username']
        self.assertEqual(
            'Username already exists.', validation_error.message)

    def test_terms_and_conditions_is_required(self):
        form_data = {
            'username': 'test',
            'password': '1234',
        }
        form = RegistrationForm(
            data=form_data,
            questions=[self.question, ]
        )
        self.assertEqual(form.is_valid(), False)

    def test_security_questions_can_contain_non_ascii(self):
        question_accents = SecurityQuestion(
            title=u'Non-ascii characters? ê ờ ប အ',
            slug='non-ascii-characters',
        )
        self.security_index.add_child(instance=question_accents)
        question_accents.save()
        form_data = {
            'username': 'test',
            'password': '1234',
            'terms_and_conditions': True,
        }
        form = RegistrationForm(
            data=form_data,
            questions=[question_accents]
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.fields['question_0'].label,
            u'Non-ascii characters? ê ờ ប အ',
        )

    def test_future_date_of_birth(self):
        tomorrow = timezone.now() + timedelta(days=1)
        form_data = {
            'username': 'testusername',
            'password': '1234',
            'date_of_birth_year': tomorrow.year,
            'date_of_birth_month': tomorrow.month,
            'date_of_birth_day': tomorrow.day,
            'terms_and_conditions': True
        }
        form = RegistrationForm(
            data=form_data,
            questions=[self.question, ]
        )
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(
            u'Date of birth can not be in the future.',
            form.errors['date_of_birth'][0]
        )

    def test_date_of_birth(self):
        yesterday = timezone.now() - timedelta(days=1)
        form_data = {
            'username': 'testusername',
            'password': '1234',
            'date_of_birth_year': yesterday.year,
            'date_of_birth_month': yesterday.month,
            'date_of_birth_day': yesterday.day,
            'terms_and_conditions': True
        }
        form = RegistrationForm(
            data=form_data,
            questions=[self.question, ]
        )
        self.assertEqual(form.is_valid(), True)

    def test_if_date_of_birth_required_but_not_on_reg(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)
        profile_settings.activate_dob = True
        profile_settings.capture_dob_on_reg = False
        profile_settings.dob_required = True
        profile_settings.save()

        form_data = {
            'username': 'testusername',
            'password': '1234',
            'terms_and_conditions': True
        }
        form = RegistrationForm(
            data=form_data,
            questions=[self.question, ]
        )
        self.assertEqual(form.is_valid(), True)

    def test_if_alias_on_reg_is_not_on_form_done(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)
        profile_settings.activate_display_name = True
        profile_settings.capture_display_name_on_reg = True
        profile_settings.display_name_required = True
        profile_settings.activate_dob = True

        profile_settings.save()

        yesterday = timezone.now() - timedelta(days=1)
        form_data = {
            'date_of_birth_year': yesterday.year,
            'date_of_birth_month': yesterday.month,
            'date_of_birth_day': yesterday.day,
        }
        form = DoneForm(
            data=form_data,
        )
        self.assertEqual(form.is_valid(), True)


class PasswordRecoveryTestCase(MoloTestCaseMixin, TestCase):

    def setUp(self):
        self.mk_main()
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')

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

    def test_username_and_security_answer(self):
        form_data = {
            "username": "tester",
            "question_0": "20"
        }
        form = ForgotPasswordForm(
            data=form_data,
            questions=[self.question, ]
        )
        self.assertEqual(form.is_valid(), True)
