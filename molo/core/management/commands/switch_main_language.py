from __future__ import absolute_import, unicode_literals

from django.core.management.base import BaseCommand
from molo.core.models import (
    Languages, Main, SiteLanguage, SiteLanguageRelation, LanguageRelation)

# This is currently made to work for single sites only


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('new_language_locale', type=str)

    def handle(self, *args, **options):
        new_language_locale = options.get('new_language_locale', None)
        main = Main.objects.first()

        # add the new language if necessary
        if not SiteLanguage.objects.filter(
                locale=new_language_locale).exists():
            new_language = SiteLanguageRelation.objects.create(
                language_setting=Languages.for_site(main.get_site()),
                locale=new_language_locale,
                is_active=True)

        # switch the language in the language relation to the new language
        for relation in LanguageRelation.objects.filter(
                language__is_main_language=True):
            relation.language = new_language
            relation.save()

        new_language.is_main_language = True
        new_language.save()
