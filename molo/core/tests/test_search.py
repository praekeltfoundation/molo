from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import Client

from wagtail.wagtailsearch.backends import get_search_backend

from molo.core.models import SiteLanguageRelation, \
    Main, Languages, FooterPage
from molo.core.tests.base import MoloTestCaseMixin


class TestSearch(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.client = Client()
        # Creates Main language
        self.mk_main()
        main = Main.objects.all().first()
        self.english = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(main.get_site()),
            locale='en',
            is_active=True)

        self.french = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(main.get_site()),
            locale='fr',
            is_active=True)

        # Creates a section under the index page
        self.english_section = self.mk_section(
            self.section_index, title='English section')

        self.mk_main2()
        self.main2 = Main.objects.all().last()
        self.language_setting2 = Languages.objects.create(
            site_id=self.main2.get_site().pk)
        self.english2 = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting2,
            locale='en',
            is_active=True)

        self.spanish = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting2,
            locale='es',
            is_active=True)

        self.yourmind2 = self.mk_section(
            self.section_index2, title='Your mind2')
        self.yourmind_sub2 = self.mk_section(
            self.yourmind2, title='Your mind subsection2')

    def test_search_only_includes_articles(self):
        self.backend = get_search_backend('default')
        self.backend.reset_index()
        self.mk_articles(self.english_section, count=2)
        footer = FooterPage(title='Test Footer')
        self.footer_index.add_child(instance=footer)
        footer.save_revision().publish()
        self.backend.refresh_index()
        response = self.client.get(reverse('search'), {
            'q': 'Test'
        })
        results = response.context['results']
        for article in results:
            self.assertNotEquals(article.title, 'Test Footer')

    def test_search(self):
        self.backend = get_search_backend('default')
        self.backend.reset_index()

        self.mk_articles(self.english_section, count=20)
        self.backend.refresh_index()

        response = self.client.get(reverse('search'), {
            'q': 'Test'
        })
        self.assertContains(response, 'Page 1 of 2')
        self.assertContains(response, '&rarr;')
        self.assertNotContains(response, '&larr;')

        response = self.client.get(reverse('search'), {
            'q': 'Test',
            'p': '2',
        })
        self.assertContains(response, 'Page 2 of 2')
        self.assertNotContains(response, '&rarr;')
        self.assertContains(response, '&larr;')

        response = self.client.get(reverse('search'), {
            'q': 'Test',
            'p': 'foo',
        })
        self.assertContains(response, 'Page 1 of 2')

        response = self.client.get(reverse('search'), {
            'q': 'Test',
            'p': '4',
        })
        self.assertContains(response, 'Page 2 of 2')

        response = self.client.get(reverse('search'), {
            'q': 'magic'
        })
        self.assertContains(response, 'No search results for magic')

        response = self.client.get(reverse('search'))
        self.assertContains(response, 'No search results for None')

    def test_search_works_with_multisite(self):
        self.backend = get_search_backend('default')
        self.backend.reset_index()

        self.mk_article(
            self.english_section, title="Site 1 article")
        self.mk_article(
            self.yourmind2, title="Site 2 article")
        self.backend.refresh_index()

        response = self.client.get(reverse('search'), {
            'q': 'article'
        })
        self.assertContains(response, 'Site 1 article')
        self.assertNotContains(response, 'Site 2 article')

        client = Client(HTTP_HOST=self.site2.hostname)
        response = client.get(reverse('search'), {
            'q': 'article'
        })
        self.assertNotContains(response, 'Site 1 article')
        self.assertContains(response, 'Site 2 article')

        response = self.client.get(reverse('search'), {
            'q': 'magic'
        })
        self.assertContains(response, 'No search results for magic')

        response = self.client.get(reverse('search'))
        self.assertContains(response, 'No search results for None')

    def test_search_works_with_multilanguages(self):
        self.backend = get_search_backend('default')
        self.backend.reset_index()
        eng_article = self.mk_article(
            self.english_section, title="English article")

        self.mk_article_translation(
            eng_article, self.french, title='French article')

        self.backend.refresh_index()

        self.client.get('/locale/en/')
        response = self.client.get(reverse('search'), {
            'q': 'article'
        })
        self.assertContains(response, 'English article')
        self.assertNotContains(response, 'French article')

        self.client.get('/locale/fr/')
        response = self.client.get(reverse('search'), {
            'q': 'article'
        })
        self.assertContains(response, 'French article')
        self.assertNotContains(response, 'English article')
