from __future__ import absolute_import, unicode_literals

from django.core.management.base import BaseCommand
from molo.core.models import ArticlePage


class Command(BaseCommand):
    def handle(self, **options):
        article_pages = ArticlePage.objects.all()
        for article in article_pages:
            if article.featured_in_latest or \
                article.featured_in_latest_start_date or \
                    article.featured_in_latest_end_date:
                article.featured_in_latest = False
                article.featured_in_latest_start_date = None
                article.featured_in_latest_end_date = None
                article.save_revision().publish()
                print "Promoted Article in latest--->", article.title, "<---"
            if article.featured_in_homepage or \
                article.featured_in_homepage_start_date or \
                    article.featured_in_homepage_end_date:
                article.featured_in_homepage = False
                article.featured_in_homepage_start_date = None
                article.featured_in_homepage_end_date = None
                article.save_revision().publish()
                print "Promoted Article in Home Page--->", article.title, "<---"
