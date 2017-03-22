from __future__ import absolute_import, unicode_literals

from django.core.management.base import BaseCommand
from molo.core.models import SectionPage


class Command(BaseCommand):
    def handle(self, **options):
        SectionPage.objects.all().update(
            content_rotation_start_date=None,
            content_rotation_end_date=None,
            monday_rotation=False,
            tuesday_rotation=False,
            wednesday_rotation=False,
            thursday_rotation=False,
            friday_rotation=False,
            saturday_rotation=False,
            sunday_rotation=False,
            time=None)
