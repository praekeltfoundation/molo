from __future__ import absolute_import, unicode_literals

from django.core.management.base import BaseCommand
from molo.core.models import PageTranslation


class Command(BaseCommand):

    def handle(self, *args, **options):
        for translation in PageTranslation.objects.all():
            if translation.page and translation.translated_page:
                translation.page.translated_pages.add(
                    translation.translated_page)
                translation.page.save()
                translation.translated_page.translated_pages.add(
                    translation.page)
                translation.translated_page.save()
            else:
                self.stdout.write(self.style.NOTICE(
                    'Translation with pk "%s" is missing page/translated_page'
                    % (translation.pk)))
