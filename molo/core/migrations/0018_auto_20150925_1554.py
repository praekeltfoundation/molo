# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_auto_20150925_1232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articlepage',
            name='commenting_state',
            field=models.CharField(blank=True, max_length=1, null=True, choices=[(b'O', b'Open'), (b'C', b'Closed'), (b'D', b'Disabled'), (b'T', b'Timestamped')]),
        ),
        migrations.AlterField(
            model_name='homepage',
            name='commenting_state',
            field=models.CharField(blank=True, max_length=1, null=True, choices=[(b'O', b'Open'), (b'C', b'Closed'), (b'D', b'Disabled'), (b'T', b'Timestamped')]),
        ),
        migrations.AlterField(
            model_name='languagepage',
            name='commenting_state',
            field=models.CharField(blank=True, max_length=1, null=True, choices=[(b'O', b'Open'), (b'C', b'Closed'), (b'D', b'Disabled'), (b'T', b'Timestamped')]),
        ),
        migrations.AlterField(
            model_name='main',
            name='commenting_state',
            field=models.CharField(default=b'C', max_length=1, choices=[(b'O', b'Open'), (b'C', b'Closed'), (b'D', b'Disabled'), (b'T', b'Timestamped')]),
        ),
        migrations.AlterField(
            model_name='sectionpage',
            name='commenting_state',
            field=models.CharField(blank=True, max_length=1, null=True, choices=[(b'O', b'Open'), (b'C', b'Closed'), (b'D', b'Disabled'), (b'T', b'Timestamped')]),
        ),
    ]
