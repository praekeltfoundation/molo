# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def create_banner_index(apps, schema_editor):
    from molo.core.models import BannerPage, LanguagePage, BannerIndexPage, Main
    main = Main.objects.all().first()
    main_language = LanguagePage.objects.all().first()

    if main and main_language:
        banner_index = BannerIndexPage(title='Banners', slug='banners')
        main.add_child(instance=banner_index)
        banner_index.save_revision().publish()

        # Move existing banners
        for page in BannerPage.objects.all().child_of(main_language):
            page.move(banner_index, pos='last-child')


def create_section_index(apps, schema_editor):
    from molo.core.models import SectionPage, LanguagePage, SectionIndexPage, Main
    main = Main.objects.all().first()
    main_language = LanguagePage.objects.all().first()

    if main and main_language:
        section_index = SectionIndexPage(title='Sections', slug='sections')
        main.add_child(instance=section_index)
        section_index.save_revision().publish()

        # Move existing banners
        for page in SectionPage.objects.all().child_of(main_language):
            page.move(section_index, pos='last-child')


def create_footer_index(apps, schema_editor):
    from molo.core.models import FooterPage, LanguagePage, FooterIndexPage, Main
    main = Main.objects.all().first()
    main_language = LanguagePage.objects.all().first()

    if main and main_language:
        footer_index = FooterIndexPage(title='Footer pages', slug='footer-pages')
        main.add_child(instance=footer_index)
        footer_index.save_revision().publish()

        # Move existing banners
        for page in FooterPage.objects.all().child_of(main_language):
            page.move(footer_index, pos='last-child')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_bannerindexpage_footerindexpage_sectionindexpage'),
    ]

    operations = [
        migrations.RunPython(create_banner_index),
        migrations.RunPython(create_section_index),
        migrations.RunPython(create_footer_index),
    ]
