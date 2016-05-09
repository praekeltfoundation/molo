# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_sitesettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesettings',
            name='content_rotation',
            field=models.BooleanField(default=False, help_text='This option allows content to be rotated randomly and automatically'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='content_rotation_time',
            field=models.TimeField(help_text='This is the time that content willbe rotated every day.', null=True, blank=True),
        ),
    ]
