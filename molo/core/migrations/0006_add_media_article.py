# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-02-10 17:57
from __future__ import unicode_literals

from django.db import migrations, models
import molo.core.models
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20180906_0915'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='articlepage',
            options={'ordering': ('-latest_revision_created_at',), 'verbose_name': 'Article'},
        ),
        migrations.AddField(
            model_name='articlepage',
            name='homepage_media',
            field=wagtail.core.fields.StreamField([('media', molo.core.models.MoloMediaBlock(icon='media'))], blank=True, help_text='If media is added here, it will override the article image as the hero', null=True),
        ),
        migrations.AddField(
            model_name='articlepage',
            name='is_media_page',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='default_service_directory_radius',
            field=models.PositiveSmallIntegerField(blank=True, help_text='When set this will enable service directory radius filter as the set value for the default radius value', null=True, verbose_name='Default Service Directory Radius'),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='enable_multi_category_service_directory_search',
            field=models.BooleanField(default=False, verbose_name='Enable multi service directory search'),
        ),
    ]
