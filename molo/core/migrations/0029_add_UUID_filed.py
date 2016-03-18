# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_rename_homepage_to_bannerpage'),
    ]

    operations = [
        migrations.AddField(
            model_name='articlepage',
            name='uuid',
            field=models.CharField(max_length=32, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='sectionpage',
            name='uuid',
            field=models.CharField(max_length=32, null=True, blank=True),
        ),
    ]
