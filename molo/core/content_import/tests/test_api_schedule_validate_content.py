import mock
import pytest

from django.test import TestCase, override_settings
from django.core import mail

from elasticgit.tests.base import ModelBaseTest

from molo.core.tests.base import MoloTestCaseMixin
from molo.core.content_import.tests.base import ElasticGitTestMixin
from molo.core.content_import.api import schedule_validate_content
from molo.core.content_import.tests.utils import (
    fake_repos, find_repos_from_data)


@pytest.mark.django_db
class TestScheduleValidateContent(
        TestCase, ModelBaseTest, MoloTestCaseMixin, ElasticGitTestMixin):

    def setUp(self):
        self.mk_main()

    @mock.patch('molo.core.tasks.api')
    @override_settings(
        FROM_EMAIL='from@example.org',
        CONTENT_IMPORT_SUBJECT='Content Import')
    def test_validate_successful(self, api):
        repos = fake_repos('r1', 'r2')

        api.get_repos.side_effect = lambda names, **kw: (
            find_repos_from_data(repos, names))

        api.validate_content = lambda repos, *a: {
            repos: {
                'errors': [],
                'warnings': []
            }
        }[repos]

        schedule_validate_content(
            repos,
            ['en', 'fr'],
            'us3r',
            'to@example.org',
            'h0st',
            delay=False)

        self.assertEqual(len(mail.outbox), 1)
        [email] = mail.outbox
        self.assertEqual(email.subject, 'Content Import')
        self.assertEqual(email.from_email, 'from@example.org')
        self.assertEqual(email.to, ['to@example.org'])

        self.assertTrue('us3r' in email.body)
        self.assertTrue('h0st' in email.body)
        self.assertTrue('is complete' in email.body)
        self.assertFalse('Warnings' in email.body)
        self.assertFalse('Errors' in email.body)

    @mock.patch('molo.core.tasks.api')
    @override_settings(
        FROM_EMAIL='from@example.org',
        CONTENT_IMPORT_SUBJECT='Content Import')
    def test_validate_warnings(self, api):
        repos = fake_repos('r1', 'r2')

        api.get_repos.side_effect = lambda names, **kw: (
            find_repos_from_data(repos, names))

        api.validate_content = lambda *a, **kw: {
            'errors': [],
            'warnings': [{'type': 'fake_warning'}]
        }

        schedule_validate_content(
            repos,
            ['en', 'fr'],
            'us3r',
            'to@example.org',
            'h0st',
            delay=False)

        self.assertEqual(len(mail.outbox), 1)
        [email] = mail.outbox

        self.assertEqual(email.subject, 'Content Import')
        self.assertEqual(email.from_email, 'from@example.org')
        self.assertEqual(email.to, ['to@example.org'])

        self.assertTrue('us3r' in email.body)
        self.assertTrue('h0st' in email.body)
        self.assertTrue('is complete' in email.body)
        self.assertTrue('Warnings' in email.body)
        self.assertTrue('fake_warning' in email.body)
        self.assertFalse('Errors' in email.body)

    @mock.patch('molo.core.tasks.api')
    @override_settings(
        FROM_EMAIL='from@example.org',
        CONTENT_IMPORT_SUBJECT='Content Import')
    def test_validate_errors(self, api):
        repos = fake_repos('r1', 'r2')

        api.get_repos.side_effect = lambda names, **kw: (
            find_repos_from_data(repos, names))

        api.validate_content = lambda *a, **kw: {
            'errors': [{'type': 'fake_error'}],
            'warnings': []
        }

        schedule_validate_content(
            repos,
            ['en', 'fr'],
            'us3r',
            'to@example.org',
            'h0st',
            delay=False)

        self.assertEqual(len(mail.outbox), 1)
        [email] = mail.outbox

        self.assertEqual(email.subject, 'Content Import')
        self.assertEqual(email.from_email, 'from@example.org')
        self.assertEqual(email.to, ['to@example.org'])

        self.assertTrue('us3r' in email.body)
        self.assertTrue('h0st' in email.body)
        self.assertTrue('failed' in email.body)
        self.assertFalse('Warnings' in email.body)
        self.assertTrue('Errors' in email.body)
        self.assertTrue('fake_error' in email.body)

    @mock.patch('molo.core.tasks.api')
    @override_settings(
        FROM_EMAIL='from@example.org',
        CONTENT_IMPORT_SUBJECT='Content Import')
    def test_validate_errors_and_warnings(self, api):
        repos = fake_repos('r1', 'r2')

        api.get_repos.side_effect = lambda names, **kw: (
            find_repos_from_data(repos, names))

        api.validate_content = lambda *a, **kw: {
            'errors': [{'type': 'fake_error'}],
            'warnings': [{'type': 'fake_warning'}]
        }

        schedule_validate_content(
            repos,
            ['en', 'fr'],
            'us3r',
            'to@example.org',
            'h0st',
            delay=False)

        self.assertEqual(len(mail.outbox), 1)
        [email] = mail.outbox

        self.assertEqual(email.subject, 'Content Import')
        self.assertEqual(email.from_email, 'from@example.org')
        self.assertEqual(email.to, ['to@example.org'])

        self.assertTrue('us3r' in email.body)
        self.assertTrue('h0st' in email.body)
        self.assertTrue('failed' in email.body)

        self.assertTrue('Warnings' in email.body)
        self.assertTrue('fake_warning' in email.body)

        self.assertTrue('Errors' in email.body)
        self.assertTrue('fake_error' in email.body)
