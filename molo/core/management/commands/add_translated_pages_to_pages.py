from __future__ import absolute_import, unicode_literals
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from molo.core.models import (
    PageTranslation, Page, Main, Languages)


class Command(BaseCommand):

    def handle(self, *args, **options):
        # first add all the translations to the main language Page
        # and add the main language page as a translated page
        # to the translated pages
        for main in Main.objects.all():
            try:
                main_language = Languages.for_site(
                    main.get_site()).languages.get(is_main_language=True)
            except ObjectDoesNotExist:
                self.stdout.write(self.style.NOTICE(
                    'Main with pk "%s"'
                    'is missing a main language'
                    % (main.pk)))
                continue
            pages = Page.objects.all().exclude(depth__in=[1, 2, 3])
            for page in pages:
                if page.specific.language and (
                   page.specific.language.pk == main_language.pk):
                    for translation in PageTranslation.objects.filter(
                            page=page):
                        if translation.page and \
                         translation.translated_page and \
                         translation.translated_page.specific.language and \
                         translation.translated_page.pk != translation.page.pk:
                            page.specific.translated_pages.add(
                                translation.translated_page.specific)
                            translation.translated_page.specific.\
                                translated_pages.add(page.specific)
                            page.save()
                            translation.translated_page.save()
                        else:
                            self.stdout.write(self.style.NOTICE(
                                'Translation with pk "%s"'
                                'is missing page/translated_page'
                                % (translation.pk)))

            # loop through all translated_pages on the main language page and
            # add all the translations to the rest of the translated pages
            # except the language that it is in
            for page in Page.objects.all().exclude(depth__in=[1, 2, 3]):
                if page.specific.language and (
                   page.specific.language.pk == main_language.pk):
                    for translated_page in \
                            page.specific.translated_pages.all():
                        translations = page.specific.translated_pages.all().\
                            exclude(language__pk=translated_page.language.pk)
                        for translation in translations:
                            translated_page.translated_pages.add(translation)
                        translated_page.save()
