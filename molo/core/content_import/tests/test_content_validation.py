import pytest

from elasticgit.tests.base import ModelBaseTest

from molo.core.models import SiteLanguage
from molo.core.tests.base import MoloTestCaseMixin
from molo.core.content_import.tests.base import ElasticGitTestMixin
from molo.core.content_import.validation import ContentImportValidation

from unicore.content import models as eg_models


@pytest.mark.django_db
class ContentImportValidationTestCase(
        ModelBaseTest, MoloTestCaseMixin, ElasticGitTestMixin):

    def setUp(self):
        self.mk_main()
        self.workspace = self.mk_workspace()

        self.workspace.setup_custom_mapping(eg_models.Localisation, {
            'properties': {
                'locale': {
                    'type': 'string',
                    'index': 'not_analyzed',
                }
            }
        })

        self.workspace.setup_custom_mapping(eg_models.Category, {
            'properties': {
                'uuid': {'type': 'string', 'index': 'not_analyzed'},
                'language': {'type': 'string', 'index': 'not_analyzed'},
                'position': {'type': 'integer', 'index': 'not_analyzed'},
            }
        })
        self.workspace.setup_custom_mapping(eg_models.Page, {
            'properties': {
                'uuid': {'type': 'string', 'index': 'not_analyzed'},
                'language': {'type': 'string', 'index': 'not_analyzed'},
                'position': {'type': 'integer', 'index': 'not_analyzed'},
            }
        })

    def test_language_validation(self):
        self.english = SiteLanguage.objects.create(
            locale='en',
        )

        error = ContentImportValidation(self.workspace).is_validate_for([
            {'locale': 'eng_GB', 'site_language': 'en',
             'is_main': False},
            {'locale': 'spa_ES', 'site_language': 'es',
             'is_main': True}])

        self.assertEquals(error[0]['type'],
                          'wrong_main_language_exist_in_wagtail')

    def test_import_validation(self):
        lang1 = eg_models.Localisation({'locale': 'eng_GB'})
        lang2 = eg_models.Localisation({'locale': 'spa_ES'})

        self.workspace.save(lang1, 'Added english language')
        self.workspace.save(lang2, 'Added french language')

        [eng_cat] = self.create_categories(
            self.workspace, locale='eng_GB', count=1)

        # spanish section with valid source
        self.create_categories(
            self.workspace, title='spanish cat', locale='spa_ES',
            source=eng_cat.uuid, count=1)

        [eng_page] = self.create_pages(
            self.workspace, locale='eng_GB', count=1)

        # spanish page with valid source
        self.create_pages(
            self.workspace, title='spanish page', locale='spa_ES',
            source=eng_page.uuid, count=1)

        # section with invalid source
        self.create_categories(
            self.workspace, locale='spa_ES',
            source='an-invalid-uuid', count=1)

        # page with invalid source
        self.create_pages(
            self.workspace, count=1, locale='spa_ES',
            source='an-invalid-uuid')

        # section with no source
        self.create_categories(
            self.workspace, locale='spa_ES', source=None, count=1)

        # traslated page without a source and an invalid primary category
        self.create_pages(
            self.workspace, source=None, count=1, locale='spa_ES',
            primary_category='an-invalid-primary-category')

        # main language page with invalid primary category
        self.create_pages(
            self.workspace, count=1, locale='eng_GB',
            primary_category='an-invalid-uuid')

        errors = ContentImportValidation(self.workspace).is_validate_for([
            {'locale': 'eng_GB', 'site_language': 'en', 'is_main': True},
            {'locale': 'spa_ES', 'site_language': 'es', 'is_main': False}])

        self.assertEquals(errors[0]['type'], 'no_primary_category')
        self.assertEquals(errors[1]['type'], 'no_source_found_for_category')
        self.assertEquals(errors[2]['type'], 'no_source_found_for_page')
        self.assertEquals(errors[3]['type'], 'no_primary_category')
        self.assertEquals(errors[4]['type'], 'category_source_not_exists')
        self.assertEquals(errors[5]['type'], 'page_source_not_exists')
        self.assertEquals(len(errors), 6)
