from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import Client

from wagtail.wagtailsearch.backends import get_search_backend

from molo.core.models import ArticlePage, SiteLanguage
from molo.core.tests.base import MoloTestCaseMixin


class TestSearch(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.client = Client()
        # Creates Main language
        self.english = SiteLanguage.objects.create(
            locale='en',
        )
        # Creates translation Language
        self.french = SiteLanguage.objects.create(
            locale='fr',
        )
        self.mk_main()

        # Creates a section under the index page
        self.english_section = self.mk_section(
            self.section_index, title='English section')

    def test_search(self):
        self.backend = get_search_backend('default')
        self.backend.reset_index()

        for a in range(0, 20):
            ArticlePage.objects.create(
                title='article %s' % (a,), depth=a,
                subtitle='article %s subtitle' % (a,),
                slug='article-%s' % (a,), path=[a])

        self.backend.refresh_index()

        response = self.client.get(reverse('search'), {
            'q': 'article'
        })
        self.assertContains(response, 'Page 1 of 2')
        self.assertContains(response, '&rarr;')
        self.assertNotContains(response, '&larr;')

        response = self.client.get(reverse('search'), {
            'q': 'article',
            'p': '2',
        })
        self.assertContains(response, 'Page 2 of 2')
        self.assertNotContains(response, '&rarr;')
        self.assertContains(response, '&larr;')

        response = self.client.get(reverse('search'), {
            'q': 'article',
            'p': 'foo',
        })
        self.assertContains(response, 'Page 1 of 2')

        response = self.client.get(reverse('search'), {
            'q': 'article',
            'p': '4',
        })
        self.assertContains(response, 'Page 2 of 2')

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
