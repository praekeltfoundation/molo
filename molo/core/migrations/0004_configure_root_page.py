# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def configure_root_page(apps, schema_editor):
    # Get models
    ContentType = apps.get_model('contenttypes.ContentType')
    Site = apps.get_model('wagtailcore.Site')
    Main = apps.get_model('core.Main')
    HomePage = apps.get_model('core.HomePage')

    # Delete the default homepage
    HomePage.objects.all().delete()

    # Create content type for main model
    main_content_type, created = ContentType.objects.get_or_create(
        model='main', app_label='core')

    # Create a new homepage
    main = Main.objects.create(
        title="Main",
        slug='main',
        content_type=main_content_type,
        path='00010001',
        depth=2,
        numchild=0,
        url_path='/home/',
    )

    # Create a site with the new homepage set as the root
    Site.objects.all().delete()
    Site.objects.create(
        hostname='localhost', root_page=main, is_default_site=True)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_articlepage_languagepage_main_sectionpage'),
    ]

    operations = [
        migrations.RunPython(configure_root_page),
    ]
