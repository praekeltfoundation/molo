import pytest
from datetime import datetime, timedelta
from django.test import TestCase

from molo.core.models import ArticlePage, SectionPage, LanguagePage


@pytest.mark.django_db
class TestModels(TestCase):
    fixtures = ['molo/core/tests/fixtures/test.json']

    def test_article_order(self):
        now = datetime.now()
        article1 = ArticlePage.objects.get(pk=14)
        article1.first_published_at = now
        article1.save()

        article2 = ArticlePage.objects.get(pk=15)
        article2.first_published_at = now + timedelta(hours=1)
        article2.save()

        # most recent first
        section = SectionPage.objects.get(slug='your-mind-subsection')
        self.assertEquals(
            section.articles()[0].title, article2.title)

        # swap published date
        article1.first_published_at = now + timedelta(hours=4)
        article1.save()

        self.assertEquals(
            section.articles()[0].title, article1.title)

    def test_latest(self):
        lang = LanguagePage.objects.get(code='en')
        self.assertEquals(lang.latest_articles().count(), 2)
