from __future__ import absolute_import, unicode_literals

from django.core.management.base import BaseCommand
from molo.core.models import (
    Languages, Main, SiteLanguage, SiteLanguageRelation, LanguageRelation)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('new_language_locale', type=str)

    def handle(self, *args, **options):
        new_language_locale = options.get('new_language_locale', None)
        mains = Main.objects.all()
        if mains.count() != 1:
            self.stdout.write(self.style.ERROR(
                'This command only works for apps with one wagtail site'))
            exit(1)
        main = mains.first()
        old_main_langauge = SiteLanguageRelation.objects.get(
            is_main_language=True)
        if not main:
            self.stdout.write(self.style.ERROR(
                'Main page does not exist'))
        # add the new language if necessary
        desired_main_language = SiteLanguage.objects.filter(
            locale=new_language_locale)
        if not desired_main_language.exists():
            new_language = SiteLanguageRelation.objects.create(
                language_setting=Languages.for_site(main.get_site()),
                locale=new_language_locale,
                is_active=True)
            self.stdout.write(self.style.NOTICE(
                'New Language %s created' %
                new_language.locale))

        else:
            self.stdout.write(self.style.NOTICE(
                'Language %s already exists' %
                desired_main_language.first().locale))
            new_language = new_language = SiteLanguageRelation.objects.get(
                locale=new_language_locale)

        # switch the language relation to the new language
        for relation in LanguageRelation.objects.filter(
                language__is_main_language=True):
            relation.language = new_language
            relation.page.specific.language = new_language
            relation.save()

        new_language.is_main_language = True
        new_language.save()
        old_main_langauge.is_main_language = False
        old_main_langauge.is_active = False
        old_main_langauge.save()
        self.stdout.write(self.style.SUCCESS(
            'Main language swopped from %s to %s' %
            (old_main_langauge.locale, new_language.locale)))
