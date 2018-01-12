# -*- coding: utf-8 -*-
# flake8: noqa: E251, E302
from __future__ import unicode_literals

from django.db import migrations, models


def convert_languages_to_site_language_relation(apps, schema_editor):
    from molo.core.models import SiteLanguage, SiteLanguageRelation, Main, Languages
    main = Main.objects.all().first()
    if main:
        site = main.get_site()
        if site:
            language_setting, _ = Languages.objects.get_or_create(
                site_id=site.pk)
            for language in SiteLanguage.objects.all():
                site_language_rel = SiteLanguageRelation(
                    sitelanguage_ptr=language,
                    language_setting = language_setting,
                    locale=language.locale,
                    is_active=language.is_active,
                    is_main_language=language.is_main_language)
                site_language_rel.save()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0054_languages_sitelanguagerelation'),
    ]

    operations = [
        migrations.RunPython(convert_languages_to_site_language_relation),
    ]
