import mock
import pytest

from elasticgit.tests.base import ModelBaseTest

from molo.core.models import SiteLanguage, SectionPage, ArticlePage, FooterPage
from molo.core.tests.base import MoloTestCaseMixin
from molo.core.content_import.tests.base import ElasticGitTestMixin
from molo.core.content_import.helper import ContentImportHelper

from unicore.content import models as eg_models

from wagtail.wagtailimages.tests.utils import get_test_image_file


@pytest.mark.django_db
class ContentImportTestCase(
        ModelBaseTest, MoloTestCaseMixin, ElasticGitTestMixin):

    def setUp(self):
        self.english = SiteLanguage.objects.create(
            locale='en',
        )
        self.spanish = SiteLanguage.objects.create(
            locale='es',
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

        # section with invalid source
        self.create_categories(
            self.workspace, locale='spa_ES', source='an-invalid-uuid', count=1)
        # section with no source
        self.create_categories(
            self.workspace, locale='spa_ES', source=None, count=1)

        self.workspace.save(cat_spa_1.update({
            'source': cat_eng_1.uuid,
            'position': 4,
        }), 'Added source to category.')
        self.workspace.save(cat_spa_2.update({
            'source': cat_eng_2.uuid,
            'position': 4,
        }), 'Added source to category.')

        en_pages1 = self.create_pages(
            self.workspace, count=10, locale='eng_GB',
            primary_category=cat_eng_1.uuid)

        en_pages2 = self.create_pages(
            self.workspace, count=10, locale='eng_GB',
            primary_category=cat_eng_2.uuid)

        # main language page with invalid primary category
        self.create_pages(
            self.workspace, count=1, locale='eng_GB',
            primary_category='an-invalid-uuid')

        en_footer_pages = self.create_pages(
            self.workspace, count=2, locale='eng_GB',
            primary_category=None)

        es_pages1 = self.create_pages(
            self.workspace, count=10, locale='spa_ES',
            primary_category=cat_eng_1.uuid)

        es_pages2 = self.create_pages(
            self.workspace, count=10, locale='spa_ES',
            primary_category=cat_eng_2.uuid)

        es_footer_pages = self.create_pages(
            self.workspace, count=2, locale='spa_ES',
            primary_category=None)

        # translation page without a source and primary category
        self.create_pages(
            self.workspace, count=1, locale='spa_ES',
            primary_category=None)

        # page with linked page
        [page_en] = self.create_pages(
            self.workspace, count=1, locale='eng_GB',
            primary_category=cat_eng_1.uuid)
        [page_with_linked_page] = self.create_pages(
            self.workspace, count=1, locale='eng_GB',
            linked_pages=[page_en.uuid], primary_category=cat_eng_1.uuid)

        for i in range(0, 10):
            self.workspace.save(es_pages1[i].update({
                'source': en_pages1[i].uuid,
                'author_tags': ['love'],
            }), 'Added author_tags and source to page.')

            self.workspace.save(es_pages2[i].update({
                'source': en_pages2[i].uuid,
            }), 'Added source to page.')

        for i in range(0, 2):
            self.workspace.save(es_footer_pages[i].update({
                'source': en_footer_pages[i].uuid,
            }), 'Added source to page.')

        self.assertEquals(
            self.workspace.S(eg_models.Category).all().count(), 6)

        self.assertEquals(
            self.workspace.S(eg_models.Page).all().count(), 48)
        self.assertEquals(
            self.workspace.S(eg_models.Localisation).all().count(), 2)

        self.assertEquals(SectionPage.objects.all().count(), 0)
        self.assertEquals(ArticlePage.objects.all().count(), 0)

        ContentImportHelper(self.workspace).import_content_for([
            {'locale': 'eng_GB', 'site_language': 'en', 'is_main': True},
            {'locale': 'spa_ES', 'site_language': 'es', 'is_main': False}])

        self.assertEquals(SectionPage.objects.all().count(), 4)
        self.assertEquals(ArticlePage.objects.all().count(), 46)
        self.assertEquals(
            ArticlePage.objects.filter(metadata_tags__name='love').count(), 10)

        page = ArticlePage.objects.get(uuid=page_with_linked_page.uuid)
        linked_page = ArticlePage.objects.get(uuid=page_en.uuid)
        print "page body --->", page.body.stream_data
        self.assertEquals(page.body.stream_data[2],
                          {u'type': u'page', u'value': linked_page.pk})

        # run import twice
        ContentImportHelper(self.workspace).import_content_for([
            {'locale': 'eng_GB', 'site_language': 'en', 'is_main': True},
            {'locale': 'spa_ES', 'site_language': 'es', 'is_main': False}])

        self.assertEquals(SectionPage.objects.all().count(), 4)
        self.assertEquals(ArticlePage.objects.all().count(), 46)
        self.assertEquals(FooterPage.objects.all().count(), 4)

    @mock.patch('molo.core.content_import.get_image.get_thumbor_image_file')
    def test_image_import(self, mock_get_thumbor_image_file):
        mock_get_thumbor_image_file.return_value = get_test_image_file()

        lang1 = eg_models.Localisation({'locale': 'eng_GB'})
        self.workspace.save(lang1, 'Added english language')

        [cat_eng] = self.create_categories(
            self.workspace, locale='eng_GB', count=1)

        [en_page] = self.create_pages(
            self.workspace, count=1, locale='eng_GB',
            primary_category=cat_eng.uuid,
            image_host='http://thumbor', image='some-uuid-for-the-image')

        ContentImportHelper(self.workspace).import_content_for([
            {'locale': 'eng_GB', 'site_language': 'en', 'is_main': True}])

        self.assertEquals(ArticlePage.objects.all().count(), 1)
        self.assertEquals(
            ArticlePage.objects.all().first().image.title,
            'some-uuid-for-the-image')
