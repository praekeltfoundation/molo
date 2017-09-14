from __future__ import absolute_import, unicode_literals

from django.core.management.base import BaseCommand
from molo.core.page_utils import move_page_links_to_recommended_articles


class Command(BaseCommand):
    help = ("Iterates through all articles in the database and moves any "
            "articles at the end of a StreamField to Recommended Articles.")

    def handle(self, **options):
        move_page_links_to_recommended_articles()
