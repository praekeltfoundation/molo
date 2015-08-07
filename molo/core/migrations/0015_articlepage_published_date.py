# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_sectionpage_extra_style_hints'),
    ]

    operations = [
        migrations.AddField(
            model_name='articlepage',
            name='published_date',
            field=models.DateTimeField(null=True, verbose_name='Published date', blank=True),
        ),
    ]
