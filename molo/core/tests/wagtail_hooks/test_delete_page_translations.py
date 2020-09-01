from django.test import TestCase

from molo.core.models import ArticlePage, Languages, SiteLanguageRelation
from molo.core.tests.base import MoloTestCaseMixin


class TestHookDeletePageTranslations(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()

        language_setting = Languages.for_site(self.main.get_site())

        SiteLanguageRelation.objects.create(
            language_setting=language_setting,
            locale='en',
        )

        zulu = SiteLanguageRelation.objects.create(
            language_setting=language_setting,
            locale='zu',
        )

        xhosa = SiteLanguageRelation.objects.create(
            language_setting=language_setting,
            locale='xh',
        )

        self.login()

        self.page_english = self.mk_article(self.section_index, title='En')

        self.page_xhosa = self.mk_article_translation(
            self.page_english, xhosa, title='Xh')
        self.page_zulu = self.mk_article_translation(
            self.page_english, zulu, title='Zu')

    def test_does_not_delete_on_get_request(self):
        response = self.client.get(
            '/admin/pages/{0}/delete/'.format(self.page_english.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ArticlePage.objects.filter(title='En').count(), 1)
        self.assertEqual(ArticlePage.objects.filter(title='Xh').count(), 1)
        self.assertEqual(ArticlePage.objects.filter(title='Zu').count(), 1)
        self.assertEqual(ArticlePage.objects.get(
                title='En').translated_pages.all().count(), 2)

    def test_deletes_all_on_post_request(self):
        response = self.client.post(
            '/admin/pages/{0}/delete/'.format(self.page_english.id))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(ArticlePage.objects.filter(title='En').count(), 0)
        self.assertEqual(ArticlePage.objects.filter(title='Xh').count(), 0)
        self.assertEqual(ArticlePage.objects.filter(title='Zu').count(), 0)

    def test_delete_translation_does_not_delete_original(self):
        response = self.client.post(
            '/admin/pages/{0}/delete/'.format(self.page_zulu.id))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ArticlePage.objects.filter(title='En').count(), 1)
        self.assertEqual(ArticlePage.objects.filter(title='Zu').count(), 0)
        self.assertEqual(ArticlePage.objects.filter(title='Xh').count(), 1)
        self.assertEqual(ArticlePage.objects.get(
                title='En').translated_pages.all().count(), 1)

    def test_deletes_main_page_and_all_children(self):
        response = self.client.post(
            '/admin/pages/{0}/delete/'.format(self.main.id))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ArticlePage.objects.filter(title='En').count(), 0)
        self.assertEqual(ArticlePage.objects.filter(title='Xh').count(), 0)
        self.assertEqual(ArticlePage.objects.filter(title='Zu').count(), 0)

    def test_deletes_index_page_and_all_children(self):
        response = self.client.post(
            '/admin/pages/{0}/delete/'.format(self.section_index.pk))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ArticlePage.objects.filter(title='En').count(), 0)
        self.assertEqual(ArticlePage.objects.filter(title='Xh').count(), 0)
        self.assertEqual(ArticlePage.objects.filter(title='Zu').count(), 0)
