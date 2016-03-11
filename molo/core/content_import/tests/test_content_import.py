import pytest

from elasticgit.tests.base import ModelBaseTest

from molo.core.models import SiteLanguage, SectionPage, ArticlePage
from molo.core.tests.base import MoloTestCaseMixin
from molo.core.content_import.tests.base import ElasticGitTestMixin
from molo.core.content_import.helper import ContentImportHelper

from unicore.content import models as eg_models


@pytest.mark.django_db
class ContentImportTestCase(
        ModelBaseTest, MoloTestCaseMixin, ElasticGitTestMixin):

    def setUp(self):
        self.english = SiteLanguage.objects.create(
            locale='en',
        )
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
                'language': {'type': 'string', 'index': 'not_analyzed'},
                'position': {'type': 'integer', 'index': 'not_analyzed'},
            }
        })
        self.workspace.setup_custom_mapping(eg_models.Page, {
            'properties': {
                'language': {'type': 'string', 'index': 'not_analyzed'},
                'position': {'type': 'integer', 'index': 'not_analyzed'},
            }
        })

    def test_import_sections_for_primary_language(self):
        lang1 = eg_models.Localisation({'locale': 'eng_GB'})
        lang2 = eg_models.Localisation({'locale': 'spa_ES'})

        self.workspace.save(lang1, 'Added english language')
        self.workspace.save(lang2, 'Added french language')

        [cat_eng_1, cat_eng_2] = self.create_categories(
            self.workspace, locale='eng_GB', count=2)
        [cat_spa_1, cat_spa_2] = self.create_categories(
            self.workspace, locale='spa_ES', count=2)

        self.workspace.save(cat_spa_1.update({
            'source': cat_eng_1.uuid,
            'position': 4,
        }), 'Added source to category.')
        self.workspace.save(cat_spa_2.update({
            'source': cat_eng_2.uuid,
            'position': 4,
        }), 'Added source to category.')

        self.create_pages(
            self.workspace, count=10, locale='eng_GB',
            primary_category=cat_eng_1.uuid)

        self.create_pages(
            self.workspace, count=10, locale='eng_GB',
            primary_category=cat_eng_2.uuid)

        self.create_pages(
            self.workspace, count=10, locale='spa_ES',
            primary_category=cat_eng_1.uuid)

        self.create_pages(
            self.workspace, count=10, locale='spa_ES',
            primary_category=cat_eng_2.uuid)

        self.assertEquals(
            self.workspace.S(eg_models.Category).all().count(), 4)
        self.assertEquals(
            self.workspace.S(eg_models.Page).all().count(), 40)
        self.assertEquals(
            self.workspace.S(eg_models.Localisation).all().count(), 2)

        self.assertEquals(SectionPage.objects.all().count(), 0)
        self.assertEquals(ArticlePage.objects.all().count(), 0)

        ContentImportHelper(self.workspace).import_content_for(
            [{'locale': 'eng_GB', 'site_language': 'en'}])

        self.assertEquals(SectionPage.objects.all().count(), 2)
        self.assertEquals(ArticlePage.objects.all().count(), 20)
