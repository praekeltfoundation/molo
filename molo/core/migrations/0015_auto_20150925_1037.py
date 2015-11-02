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
            name='commenting_state',
            field=models.CharField(blank=True, max_length=1, null=True, choices=[(b'O', b'Open'), (b'C', b'Closed'), (b'T', b'Timestamped')]),
        ),
        migrations.AddField(
            model_name='languagepage',
            name='commenting_state',
            field=models.CharField(default=b'C', max_length=1, choices=[(b'O', b'Open'), (b'C', b'Closed'), (b'T', b'Timestamped')]),
        ),
        migrations.AddField(
            model_name='sectionpage',
            name='commenting_state',
            field=models.CharField(blank=True, max_length=1, null=True, choices=[(b'O', b'Open'), (b'C', b'Closed'), (b'T', b'Timestamped')]),
        ),
    ]
