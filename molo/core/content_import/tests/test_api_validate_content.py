import pytest

from elasticgit.tests.base import ModelBaseTest

from molo.core.models import SiteLanguage
from molo.core.tests.base import MoloTestCaseMixin
from molo.core.content_import.tests.base import ElasticGitTestMixin
from molo.core.content_import.errors import InvalidParametersError
from molo.core.content_import.api import Repo
from molo.core.content_import import api


@pytest.mark.django_db
class TestValidateContent(
        ModelBaseTest, MoloTestCaseMixin, ElasticGitTestMixin):

    def setUp(self):
        self.mk_main()

    def test_no_main_language(self):
        def run():
            api.validate_content([repo1], [
                {'locale': 'eng_GB', 'site_language': 'en', 'is_main': False},
                {'locale': 'spa_ES', 'site_language': 'es', 'is_main': False}
            ])

        ws1 = self.create_workspace(prefix='1')
        repo1 = Repo(ws1, 'repo1', 'Repo 1')
        self.add_languages(ws1, 'eng_GB', 'spa_ES')
        self.create_category(ws1, locale='eng_GB')
        self.create_category(ws1, locale='spa_ES')

        error = self.catch(InvalidParametersError, run)

        self.assertEqual(
            error.message,
            "Invalid parameters given for content validation")

        self.assertEqual(error.errors, [{
            'type': 'no_main_language_given'
        }])

    def test_multiple_main_languages(self):
        def run():
            api.validate_content([repo1], [
                {'locale': 'eng_GB', 'site_language': 'en', 'is_main': True},
                {'locale': 'spa_ES', 'site_language': 'es', 'is_main': True}
            ])

        ws1 = self.create_workspace(prefix='1')
        repo1 = Repo(ws1, 'repo1', 'Repo 1')
        self.add_languages(ws1, 'eng_GB', 'spa_ES')
        self.create_category(ws1, locale='eng_GB')
        self.create_category(ws1, locale='spa_ES')

        error = self.catch(InvalidParametersError, run)

        self.assertEqual(
            error.message,
            "Invalid parameters given for content validation")

        self.assertEqual(error.errors, [{
            'type': 'multiple_main_languages_given'
        }])

    def test_wagtail_language_validation(self):
        self.english = SiteLanguage.objects.create(locale='en')

        ws1 = self.create_workspace(prefix='1')
        repo1 = Repo(ws1, 'repo1', 'Repo 1')

        self.add_languages(ws1, 'eng_GB', 'spa_ES')
        spa_cat = self.create_category(ws1, locale='spa_ES')
        self.create_category(ws1, locale='eng_GB', source=spa_cat.uuid)

        res = api.validate_content([repo1], [
            {'locale': 'eng_GB', 'site_language': 'en', 'is_main': False},
            {'locale': 'spa_ES', 'site_language': 'es', 'is_main': True}])

        self.assertEquals(res, {
            'warnings': [],
            'errors': [{
                'type': 'wrong_main_language_exist_in_wagtail',
                'details': {
                    'repo': 'repo1',
                    'lang': 'English',
                    'selected_lang': 'Spanish'
                }
            }]
        })

    def test_strays(self):
        self.english = SiteLanguage.objects.create(locale='en')

        ws1 = self.create_workspace(prefix='1')
        repo1 = Repo(ws1, 'repo1', 'Repo 1')

        self.add_languages(ws1, 'eng_GB')
        self.create_category(ws1, locale='eng_GB')

        res = api.validate_content([repo1], [
            {'locale': 'eng_GB', 'site_language': 'en', 'is_main': True},
            {'locale': 'spa_ES', 'site_language': 'es', 'is_main': False}])

        self.assertEquals(res, {
            'errors': [],
            'warnings': [{
                'type': 'language_not_in_repo',
                'details': {
                    'repo': 'repo1',
                    'locale': 'spa_ES'
                }
            }]
        })

    def test_import_validation(self):
        ws1 = self.create_workspace(prefix='1')
        repo1 = Repo(ws1, 'repo1', 'Repo 1')
        self.add_languages(ws1, 'eng_GB', 'spa_ES')

        eng_cat = self.create_category(ws1, locale='eng_GB')

        # spanish section with valid source
        self.create_category(
            ws1, title='spanish cat', locale='spa_ES',
            source=eng_cat.uuid)

        eng_page = self.create_page(ws1, locale='eng_GB')

        # spanish page with valid source
        self.create_page(
            ws1, title='spanish page', locale='spa_ES',
            source=eng_page.uuid)

        # section with invalid source
        self.create_category(
            ws1, locale='spa_ES', source='an-invalid-uuid')

        # page with invalid source
        self.create_page(ws1, locale='spa_ES', source='an-invalid-uuid')

        # section with no source
        self.create_category(
            ws1, locale='spa_ES', source=None)

        # traslated page without a source and an invalid primary category
        self.create_page(
            ws1, source=None, locale='spa_ES',
            primary_category='an-invalid-primary-category')

        # main language page with invalid primary category
        self.create_page(
            ws1, locale='eng_GB',
            primary_category='an-invalid-uuid')

        res = api.validate_content([repo1], [
            {'locale': 'eng_GB', 'site_language': 'en', 'is_main': True},
            {'locale': 'spa_ES', 'site_language': 'es', 'is_main': False}])

        self.assertEquals(res, {
            'warnings': [],
            'errors': [{
                'type': 'no_primary_category',
                'details': {
                    'repo': 'repo1',
                    'lang': 'English (United Kingdom)',
                    'article': 'Test Page 0'
                }
            }, {
                'type': 'no_source_found_for_category',
                'details': {
                    'repo': 'repo1',
                    'lang': 'Spanish (Spain)',
                    'category': 'Test Category 0'
                }
            }, {
                'type': 'no_source_found_for_page',
                'details': {
                    'repo': 'repo1',
                    'lang': 'Spanish (Spain)',
                    'article': 'Test Page 0'
                }
            }, {
                'type': 'no_primary_category',
                'details': {
                    'repo': 'repo1',
                    'lang': 'Spanish (Spain)',
                    'article': 'Test Page 0'
                }
            }, {
                'type': 'category_source_not_exists',
                'details': {
                    'repo': 'repo1',
                    'lang': 'Spanish (Spain)',
                    'category': 'Test Category 0'
                }
            }, {
                'type': 'page_source_not_exists',
                'details': {
                    'repo': 'repo1',
                    'lang': 'Spanish (Spain)',
                    'page': 'Test Page 0'
                }
            }]
        })

    def test_import_validation_multirepo(self):
        ws1 = self.create_workspace(prefix='1')
        repo1 = Repo(ws1, 'repo1', 'Repo 1')

        ws2 = self.create_workspace(prefix='2')
        repo2 = Repo(ws2, 'repo2', 'Repo 2')

        self.add_languages(ws1, 'eng_GB', 'spa_ES')
        self.add_languages(ws2, 'eng_GB', 'spa_ES')
        self.create_category(ws1, locale='eng_GB')
        self.create_category(ws1, locale='spa_ES', source=None)

        self.create_category(ws2, locale='eng_GB')
        self.create_category(ws2, locale='spa_ES', source=None)

        res = api.validate_content([repo1, repo2], [
            {'locale': 'eng_GB', 'site_language': 'en', 'is_main': True},
            {'locale': 'spa_ES', 'site_language': 'es', 'is_main': False}])

        self.assertEquals(res, {
            'warnings': [],
            'errors': [{
                'type': 'no_source_found_for_category',
                'details': {
                    'repo': 'repo1',
                    'lang': 'Spanish (Spain)',
                    'category': 'Test Category 0'
                }
            }, {
                'type': 'no_source_found_for_category',
                'details': {
                    'repo': 'repo2',
                    'lang': 'Spanish (Spain)',
                    'category': 'Test Category 0'
                }
            }]
        })
