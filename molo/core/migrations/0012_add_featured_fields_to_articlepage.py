# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_footerpage'),
    ]

    operations = [
        migrations.AddField(
            model_name='articlepage',
            name='featured_in_latest',
            field=models.BooleanField(default=False, help_text='Article to be featured in the Latest module'),
        ),
        migrations.AddField(
            model_name='articlepage',
            name='featured_in_section',
            field=models.BooleanField(default=False, help_text='Article to be featured in the Section module'),
        ),
    ]
