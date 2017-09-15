# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import csv
from django.core.management.base import BaseCommand
from molo.core.models import Languages, ArticlePage, Main


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('csv_name', type=str)

    def handle(self, **options):
        csv_name = options.get('csv_name', None)
        mains = Main.objects.all()
        dates = {}
        with open(csv_name) as dates_csv:
            reader = csv.DictReader(dates_csv)
            if mains:
                for row in reader:
                    dates[row['slug']] = row['date']
        for main in mains:
            main_lang = Languages.for_site(main.get_site()).languages.filter(
                is_active=True, is_main_language=True).first()
            if main_lang:
                add_dates(self, main_lang, main, dates)
            else:
                self.stdout.write(self.style.NOTICE(
                    'Main language does not exist in "%s"' % main))


def add_dates(self, main_lang, main, dates):
    for slug in dates.keys():
        article = ArticlePage.objects.descendant_of(main).filter(slug=slug)
        if article.exists():
            article.update(featured_in_latest_start_date=dates[slug])
