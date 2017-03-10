import mock
import pytest

from elasticgit.tests.base import ModelBaseTest

from wagtail.wagtailimages.tests.utils import get_test_image_file

from unicore.content.models import Category, Page, Localisation

from molo.core.models import (
    SiteLanguage, SectionPage, ArticlePage, FooterPage,
    SectionIndexPage, FooterIndexPage, Main, Languages, SiteLanguageRelation)
from molo.core.tests.base import MoloTestCaseMixin
from molo.core.content_import.tests.base import ElasticGitTestMixin
from molo.core.content_import.errors import InvalidParametersError
from molo.core.content_import.api import Repo
from molo.core.content_import.utils import hash
from molo.core.content_import import api


@pytest.mark.django_db
class TestImportContent(
        ModelBaseTest, MoloTestCaseMixin, ElasticGitTestMixin):

    def setUp(self):
        self.main = self.mk_main()

    def test_no_main_language(self):
        def run():
            api.import_content([repo1], [
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
            "Invalid parameters given for content import")

        self.assertEqual(error.errors, [{
            'type': 'no_main_language_given'
        }])

    def test_multiple_main_languages(self):
        def run():
            api.import_content([repo1], [
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
            "Invalid parameters given for content import")

        self.assertEqual(error.errors, [{
            'type': 'multiple_main_languages_given'
        }])

    def test_import_sections_for_primary_language(self):
        main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)
        self.spanish = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='es',
            is_active=True)
        repo1 = Repo(self.create_workspace(), 'repo1', 'Repo 1')
        ws1 = repo1.workspace
        self.add_languages(ws1, 'eng_GB', 'spa_ES')

        [cat_eng_1, cat_eng_2] = self.create_categories(
            ws1, locale='eng_GB', count=2)
        [cat_spa_1, cat_spa_2] = self.create_categories(
            ws1, locale='spa_ES', count=2)

        # section with invalid source
        self.create_categories(
            ws1, locale='spa_ES', source='an-invalid-uuid', count=1)
        # section with no source
        self.create_categories(
            ws1, locale='spa_ES', source=None, count=1)

        ws1.save(cat_spa_1.update({
            'source': cat_eng_1.uuid,
            'position': 4,
        }), 'Added source to category.')
        ws1.save(cat_spa_2.update({
            'source': cat_eng_2.uuid,
            'position': 4,
        }), 'Added source to category.')

        en_pages1 = self.create_pages(
            ws1, count=10, locale='eng_GB',
            primary_category=cat_eng_1.uuid)

        en_pages2 = self.create_pages(
            ws1, count=10, locale='eng_GB',
            primary_category=cat_eng_2.uuid)

        # main language page with invalid primary category
        self.create_pages(
            ws1, count=1, locale='eng_GB',
            primary_category='an-invalid-uuid')

        en_footer_pages = self.create_pages(
            ws1, count=2, locale='eng_GB',
            primary_category=None)

        es_pages1 = self.create_pages(
            ws1, count=10, locale='spa_ES',
            primary_category=cat_eng_1.uuid)

        es_pages2 = self.create_pages(
            ws1, count=10, locale='spa_ES',
            primary_category=cat_eng_2.uuid)

        es_footer_pages = self.create_pages(
            ws1, count=2, locale='spa_ES',
            primary_category=None)

        # translation page without a source and primary category
        self.create_pages(
            ws1, count=1, locale='spa_ES',
            primary_category=None)

        # page with linked page
        [page_en] = self.create_pages(
            ws1, count=1, locale='eng_GB',
            primary_category=cat_eng_1.uuid)
        [page_with_linked_page] = self.create_pages(
            ws1, count=1, locale='eng_GB',
            linked_pages=[page_en.uuid], primary_category=cat_eng_1.uuid)

        for i in range(0, 10):
            ws1.save(es_pages1[i].update({
                'source': en_pages1[i].uuid,
                'author_tags': ['love'],
            }), 'Added author_tags and source to page.')

            ws1.save(es_pages2[i].update({
                'source': en_pages2[i].uuid,
            }), 'Added source to page.')

        for i in range(0, 2):
            ws1.save(es_footer_pages[i].update({
                'source': en_footer_pages[i].uuid,
            }), 'Added source to page.')

        self.assertEquals(ws1.S(Category).all().count(), 6)
        self.assertEquals(ws1.S(Page).all().count(), 48)
        self.assertEquals(ws1.S(Localisation).all().count(), 2)

        self.assertEquals(SectionPage.objects.all().count(), 0)
        self.assertEquals(ArticlePage.objects.all().count(), 0)

        api.import_content([repo1], [
            {'locale': 'eng_GB', 'site_language': 'en', 'is_main': True},
            {'locale': 'spa_ES', 'site_language': 'es', 'is_main': False}])

        self.assertEquals(SectionPage.objects.all().count(), 4)
        self.assertEquals(ArticlePage.objects.all().count(), 46)
        self.assertEquals(
            ArticlePage.objects.filter(metadata_tags__name='love').count(), 10)

        page = ArticlePage.objects.get(uuid=page_with_linked_page.uuid)
        linked_page = ArticlePage.objects.get(uuid=page_en.uuid)

        self.assertEquals(page.body.stream_data[1], {
            'type': 'page',
            'value': linked_page.pk
        })

        # run import twice
        api.import_content([repo1], [
            {'locale': 'eng_GB', 'site_language': 'en', 'is_main': True},
            {'locale': 'spa_ES', 'site_language': 'es', 'is_main': False}])

        self.assertEquals(SectionPage.objects.all().count(), 4)
        self.assertEquals(ArticlePage.objects.all().count(), 46)
        self.assertEquals(FooterPage.objects.all().count(), 4)

        # check that the main language no longer
        # needs to be first in the list of locales
        api.import_content([repo1], [
            {'locale': 'eng_GB', 'site_language': 'en', 'is_main': False},
            {'locale': 'spa_ES', 'site_language': 'es', 'is_main': True}])
        self.assertEquals(str(SiteLanguage.objects.filter(
            is_main_language=True).first()), 'English')
        self.assertEquals(str(SiteLanguage.objects.filter(
            is_main_language=False).first()), 'Spanish')

    def test_import_page(self):
        repo = Repo(self.create_workspace(), 'repo1', 'Repo 1')
        ws = repo.workspace
        self.add_languages(ws, 'eng_GB')

        self.create_page(
            ws,
            locale='eng_GB',
            title='Foo',
            description='bar baz',
            content='Quux. Corge Grault')

        api.import_content([repo], [{
            'locale': 'eng_GB',
            'site_language': 'en',
            'is_main': True
        }])

        [article] = ArticlePage.objects.all()

        self.assertEqual(article.title, 'Foo')
        self.assertEqual(article.subtitle, 'bar baz')
        self.assertTrue('Quux. Corge Grault' in str(article.body))

    def test_import_multirepo(self):
        repo1 = Repo(self.create_workspace(), 'repo1', 'Repo 1')
        repo2 = Repo(self.create_workspace(), 'repo2', 'Repo 2')
        ws1 = repo1.workspace
        ws2 = repo2.workspace

        self.add_languages(ws1, 'eng_GB', 'spa_ES')
        self.add_languages(ws2, 'eng_GB', 'spa_ES')

        a_eng = self.create_category(
            ws1, locale='eng_GB', title='A Eng')
        a_spa = self.create_category(
            ws1, locale='spa_ES', title='A Spa', source=a_eng.uuid)
        a1_eng = self.create_page(
            ws1, locale='eng_GB', title='A1 Eng', primary_category=a_eng.uuid)
        self.create_page(
            ws1, locale='spa_ES', title='A1 Spa',
            source=a1_eng.uuid, primary_category=a_spa.uuid)

        b_eng = self.create_category(
            ws2, locale='eng_GB', title='B Eng')
        b_spa = self.create_category(
            ws2, locale='spa_ES', title='B Spa', source=b_eng.uuid)
        b1_eng = self.create_page(
            ws2, locale='eng_GB', title='B1 Eng', primary_category=b_eng.uuid)
        self.create_page(
            ws2, locale='spa_ES', title='B1 Spa',
            source=b1_eng.uuid, primary_category=b_spa.uuid)

        api.import_content([repo1, repo2], [
            {'locale': 'eng_GB', 'site_language': 'en', 'is_main': True},
            {'locale': 'spa_ES', 'site_language': 'es', 'is_main': False}])

        index = SectionIndexPage.objects.all().first()
        languages = SiteLanguage.objects.all().order_by('locale')
        sections = SectionPage.objects.all().order_by('title', 'uuid')
        articles = ArticlePage.objects.all().order_by('title')

        self.assertEqual(languages.count(), 2)
        self.assertEqual(sections.all().count(), 8)
        self.assertEqual(articles.all().count(), 4)

        self.assert_collection_attrs_equal(languages, [{
            'locale': 'en',
            'is_main_language': True,
        }, {
            'locale': 'es',
            'is_main_language': False,
        }])

        self.assert_collection_attrs_equal(sections, [{
            'title': 'A Eng',
        }, {
            'title': 'A Spa',
        }, {
            'title': 'B Eng',
        }, {
            'title': 'B Spa',
        }, {
            'uuid': hash(('repo1', 'eng_GB')),
            'title': 'Repo 1',
        }, {
            'uuid': hash(('repo1', 'spa_ES')),
            'title': 'Repo 1',
        }, {
            'uuid': hash(('repo2', 'eng_GB')),
            'title': 'Repo 2',
        }, {
            'uuid': hash(('repo2', 'spa_ES')),
            'title': 'Repo 2',
        }])

        self.assert_collection_attrs_equal(articles, [{
            'title': 'A1 Eng',
        }, {
            'title': 'A1 Spa',
        }, {
            'title': 'B1 Eng',
        }, {
            'title': 'B1 Spa',
        }])

        self.assert_has_children(index, [
            sections.get(uuid=hash(('repo1', 'eng_GB'))),
            sections.get(uuid=hash(('repo1', 'spa_ES'))),
            sections.get(uuid=hash(('repo2', 'eng_GB'))),
            sections.get(uuid=hash(('repo2', 'spa_ES')))])

        self.assert_has_children(
            sections.get(uuid=hash(('repo1', 'eng_GB'))),
            [sections.get(title='A Eng')])

        self.assert_has_children(
            sections.get(uuid=hash(('repo1', 'spa_ES'))),
            [sections.get(title='A Spa')])

        self.assert_has_children(
            sections.get(uuid=hash(('repo2', 'eng_GB'))),
            [sections.get(title='B Eng')])

        self.assert_has_children(
            sections.get(uuid=hash(('repo2', 'spa_ES'))),
            [sections.get(title='B Spa')])

        self.assert_has_children(sections.get(title='A Eng'), [
            articles.get(title='A1 Eng'),
            articles.get(title='A1 Spa')
        ])

        self.assert_has_children(sections.get(title='B Eng'), [
            articles.get(title='B1 Eng'),
            articles.get(title='B1 Spa')
        ])

        self.assert_has_translation(
            articles.get(title='A1 Eng'),
            articles.get(title='A1 Spa'))

        self.assert_has_translation(
            articles.get(title='B1 Eng'),
            articles.get(title='B1 Spa'))

        self.assert_has_language(
            articles.get(title='A1 Eng'),
            languages.get(locale='en'))

        self.assert_has_language(
            articles.get(title='A1 Spa'),
            languages.get(locale='es'))

        self.assert_has_language(
            articles.get(title='B1 Eng'),
            languages.get(locale='en'))

        self.assert_has_language(
            articles.get(title='B1 Spa'),
            languages.get(locale='es'))

    def test_import_multirepo_idempotent(self):
        repo1 = Repo(self.create_workspace(), 'repo1', 'Repo 1')
        repo2 = Repo(self.create_workspace(), 'repo2', 'Repo 2')
        ws1 = repo1.workspace
        ws2 = repo2.workspace

        self.add_languages(ws1, 'eng_GB', 'spa_ES')
        self.add_languages(ws2, 'eng_GB', 'spa_ES')

        a_eng = self.create_category(ws1, locale='eng_GB')
        a_spa = self.create_category(ws1, locale='spa_ES', source=a_eng.uuid)
        a1_eng = self.create_page(
            ws1, locale='eng_GB', primary_category=a_eng.uuid)
        self.create_page(
            ws1, locale='spa_ES', source=a1_eng.uuid,
            primary_category=a_spa.uuid)

        b_eng = self.create_category(
            ws2, locale='eng_GB')
        b_spa = self.create_category(
            ws2, locale='spa_ES', source=b_eng.uuid)
        b1_eng = self.create_page(
            ws2, locale='eng_GB', primary_category=b_eng.uuid)
        self.create_page(
            ws2, locale='spa_ES', source=b1_eng.uuid,
            primary_category=b_spa.uuid)

        api.import_content([repo1, repo2], [
            {'locale': 'eng_GB', 'site_language': 'en', 'is_main': True},
            {'locale': 'spa_ES', 'site_language': 'es', 'is_main': False}])

        self.assertEqual(SiteLanguage.objects.all().count(), 2)
        self.assertEqual(SectionPage.objects.all().count(), 8)
        self.assertEqual(ArticlePage.objects.all().count(), 4)

        api.import_content([repo1, repo2], [
            {'locale': 'eng_GB', 'site_language': 'en', 'is_main': True},
            {'locale': 'spa_ES', 'site_language': 'es', 'is_main': False}])

        self.assertEqual(SiteLanguage.objects.all().count(), 2)
        self.assertEqual(SectionPage.objects.all().count(), 8)
        self.assertEqual(ArticlePage.objects.all().count(), 4)

    def test_import_no_primary_category(self):
        repo1 = Repo(self.create_workspace(), 'repo1', 'Repo 1')
        ws1 = repo1.workspace

        self.add_languages(ws1, 'eng_GB', 'spa_ES')

        eng = self.create_page(ws1, locale='eng_GB', title='Eng')
        self.create_page(ws1, locale='spa_ES', title='Spa', source=eng.uuid)

        api.import_content([repo1], [
            {'locale': 'eng_GB', 'site_language': 'en', 'is_main': True},
            {'locale': 'spa_ES', 'site_language': 'es', 'is_main': False}])

        sections = SectionPage.objects.all().order_by('title', 'uuid')
        articles = ArticlePage.objects.all().order_by('title')
        footer_index = FooterIndexPage.objects.all().first()

        self.assertEqual(sections.all().count(), 0)
        self.assertEqual(articles.all().count(), 2)

        self.assert_collection_attrs_equal(articles, [
            {'title': 'Eng'},
            {'title': 'Spa'}])

        self.assert_has_children(footer_index, [
            articles.get(title='Eng'),
            articles.get(title='Spa')
        ])

        self.assert_has_translation(
            articles.get(title='Eng'),
            articles.get(title='Spa'))

    def test_import_multirepo_no_primary_category(self):
        repo1 = Repo(self.create_workspace(), 'repo1', 'Repo 1')
        repo2 = Repo(self.create_workspace(), 'repo2', 'Repo 2')
        ws1 = repo1.workspace
        ws2 = repo2.workspace

        self.add_languages(ws1, 'eng_GB', 'spa_ES')
        self.add_languages(ws2, 'eng_GB', 'spa_ES')

        a1_eng = self.create_page(ws1, locale='eng_GB', title='A Eng')
        self.create_page(
            ws1, locale='spa_ES', title='A Spa', source=a1_eng.uuid)

        b1_eng = self.create_page(ws2, locale='eng_GB', title='B Eng')
        self.create_page(
            ws2, locale='spa_ES', title='B Spa', source=b1_eng.uuid)

        api.import_content([repo1, repo2], [
            {'locale': 'eng_GB', 'site_language': 'en', 'is_main': True},
            {'locale': 'spa_ES', 'site_language': 'es', 'is_main': False}])

        index = SectionIndexPage.objects.all().first()
        languages = SiteLanguage.objects.all().order_by('locale')
        sections = SectionPage.objects.all().order_by('title', 'uuid')
        articles = ArticlePage.objects.all().order_by('title')

        self.assertEqual(languages.count(), 2)
        self.assertEqual(sections.all().count(), 4)
        self.assertEqual(articles.all().count(), 4)

        self.assert_collection_attrs_equal(languages, [{
            'locale': 'en',
            'is_main_language': True,
        }, {
            'locale': 'es',
            'is_main_language': False,
        }])

        self.assert_collection_attrs_equal(sections, [{
            'uuid': hash(('repo1', 'eng_GB')),
            'title': 'Repo 1',
        }, {
            'uuid': hash(('repo1', 'spa_ES')),
            'title': 'Repo 1',
        }, {
            'uuid': hash(('repo2', 'eng_GB')),
            'title': 'Repo 2',
        }, {
            'uuid': hash(('repo2', 'spa_ES')),
            'title': 'Repo 2',
        }])

        self.assert_collection_attrs_equal(articles, [{
            'title': 'A Eng',
        }, {
            'title': 'A Spa',
        }, {
            'title': 'B Eng',
        }, {
            'title': 'B Spa',
        }])

        self.assert_has_children(index, [
            sections.get(uuid=hash(('repo1', 'eng_GB'))),
            sections.get(uuid=hash(('repo1', 'spa_ES'))),
            sections.get(uuid=hash(('repo2', 'eng_GB'))),
            sections.get(uuid=hash(('repo2', 'spa_ES')))])

        self.assert_has_translation(
            articles.get(title='A Eng'),
            articles.get(title='A Spa'))

        self.assert_has_translation(
            articles.get(title='B Eng'),
            articles.get(title='B Spa'))

        self.assert_has_language(
            articles.get(title='A Eng'),
            languages.get(locale='en'))

        self.assert_has_language(
            articles.get(title='A Spa'),
            languages.get(locale='es'))

        self.assert_has_language(
            articles.get(title='B Eng'),
            languages.get(locale='en'))

        self.assert_has_language(
            articles.get(title='B Spa'),
            languages.get(locale='es'))

    @mock.patch(
        'molo.core.content_import.helpers.get_image.get_thumbor_image_file')
    def test_image_import(self, mock_get_thumbor_image_file):
        repo1 = Repo(self.create_workspace(), 'repo1', 'Repo 1')
        ws1 = repo1.workspace

        mock_get_thumbor_image_file.return_value = get_test_image_file()

        self.add_languages(ws1, 'eng_GB')

        [cat_eng] = self.create_categories(
            ws1, locale='eng_GB', count=1)

        [en_page] = self.create_pages(
            ws1, count=1, locale='eng_GB',
            primary_category=cat_eng.uuid,
            image_host='http://thumbor', image='some-uuid-for-the-image')

        api.import_content([repo1], [
            {'locale': 'eng_GB', 'site_language': 'en', 'is_main': True}])

        self.assertEquals(ArticlePage.objects.all().count(), 1)
        self.assertEquals(
            ArticlePage.objects.all().first().image.title,
            'some-uuid-for-the-image')

    def test_strays_omitted(self):
        repo1 = Repo(self.create_workspace(), 'repo1', 'Repo 1')
        ws1 = repo1.workspace

        self.add_languages(ws1, 'eng_GB')
        self.create_category(ws1, locale='eng_GB', title='A Eng')

        api.import_content([repo1], [
            {'locale': 'eng_GB', 'site_language': 'en', 'is_main': True},
            {'locale': 'spa_ES', 'site_language': 'es', 'is_main': False}])

        languages = SiteLanguage.objects.all().order_by('locale')
        sections = SectionPage.objects.all().order_by('title', 'uuid')

        self.assertEqual(languages.count(), 1)
        self.assertEqual(sections.all().count(), 1)
