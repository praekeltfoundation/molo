# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0073_run_wagtail_migration_before_core_34'),
    ]

    operations = [
        migrations.AddField(
            model_name='bannerpage',
            name='subtitle',
            field=models.TextField(blank=True, null=True),
        ),
    ]
