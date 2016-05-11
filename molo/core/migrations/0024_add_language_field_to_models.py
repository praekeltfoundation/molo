# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0023_alter_page_revision_on_delete_behaviour'),
        ('core', '0023_languagepage_main_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='articlepage',
            name='language',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='homepage',
            name='language',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='sectionpage',
            name='language',
            field=models.CharField(max_length=255, blank=True),
        ),
    ]
