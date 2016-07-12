# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_create_index_pages'),
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
            field=models.IntegerField(blank=True, help_text='This is the time that content will be rotated every day. If the content should rotate at 14h, then fill in 14', null=True, validators=[django.core.validators.MaxValueValidator(23), django.core.validators.MinValueValidator(0)]),
        ),
    ]
