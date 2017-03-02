from __future__ import absolute_import, unicode_literals

from django.core.management.base import BaseCommand
from molo.core.models import ArticlePage


class Command(BaseCommand):
    def handle(self, **options):
        ArticlePage.objects.all().update(
            featured_in_latest=False,
            featured_in_latest_start_date=None,
            featured_in_latest_end_date=None,
            featured_in_homepage=False,
            featured_in_homepage_start_date=None,
            featured_in_homepage_end_date=None)
