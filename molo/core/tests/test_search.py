from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import Client

from wagtail.wagtailsearch.backends import get_search_backend

from molo.core.models import ArticlePage


class TestSearch(TestCase):

    def test_search(self):
        self.backend = get_search_backend('default')
        self.backend.reset_index()

        for a in range(0, 20):
            ArticlePage.objects.create(
                title='article %s' % (a,), depth=a,
                subtitle='article %s subtitle' % (a,),
                slug='article-%s' % (a,), path=[a])

        self.backend.refresh_index()

        client = Client()
        response = client.get(reverse('search'), {
            'q': 'article'
        })
        self.assertContains(response, 'Page 1 of 2')
        self.assertContains(response, '&rarr;')
        self.assertNotContains(response, '&larr;')

        response = client.get(reverse('search'), {
            'q': 'article',
            'p': '2',
        })
        self.assertContains(response, 'Page 2 of 2')
        self.assertNotContains(response, '&rarr;')
        self.assertContains(response, '&larr;')

        response = client.get(reverse('search'), {
            'q': 'article',
            'p': 'foo',
        })
        self.assertContains(response, 'Page 1 of 2')

        response = client.get(reverse('search'), {
            'q': 'article',
            'p': '4',
        })
        self.assertContains(response, 'Page 2 of 2')

        response = client.get(reverse('search'), {
            'q': 'magic'
        })
        self.assertContains(response, 'No search results for magic')

        response = client.get(reverse('search'))
        self.assertContains(response, 'No search results for None')
