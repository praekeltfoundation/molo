import pytest
from datetime import datetime, timedelta
from django.test import TestCase

from molo.core.models import ArticlePage


@pytest.mark.django_db
class TestModels(TestCase):
    fixtures = ['molo/core/tests/fixtures/test.json']

    def test_article_order(self):
        now = datetime.now()
        article1 = ArticlePage.objects.get(pk=7)
        article1.first_published_at = now
        article1.save()

        article2 = ArticlePage.objects.get(pk=8)
        article2.first_published_at = now + timedelta(hours=1)
        article2.save()

        # most recent first
        self.assertEquals(
            ArticlePage.objects.live()[0].title, article2.title)

        # swap published date
        article1.first_published_at = now + timedelta(hours=4)
        article1.save()

        self.assertEquals(
            ArticlePage.objects.live()[0].title, article1.title)
