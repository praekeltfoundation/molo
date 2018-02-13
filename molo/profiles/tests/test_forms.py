# -*- coding: utf-8 -*-
from django.test import TestCase
from django.contrib.auth.models import User

from molo.profiles.forms import (
    ForgotPasswordForm, RegistrationForm, ProfilePasswordChangeForm)
from molo.core.tests.base import MoloTestCaseMixin
from molo.profiles.models import SecurityQuestion, SecurityQuestionIndexPage


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
