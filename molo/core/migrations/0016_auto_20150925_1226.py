# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20150925_1037'),
    ]

    operations = [
        migrations.AddField(
            model_name='articlepage',
            name='commenting_close_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='articlepage',
            name='commenting_open_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='homepage',
            name='commenting_close_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='homepage',
            name='commenting_open_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='homepage',
            name='commenting_state',
            field=models.CharField(blank=True, max_length=1, null=True, choices=[(b'O', b'Open'), (b'C', b'Closed'), (b'T', b'Timestamped')]),
        ),
        migrations.AddField(
            model_name='languagepage',
            name='commenting_close_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='languagepage',
            name='commenting_open_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='main',
            name='commenting_close_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='main',
            name='commenting_open_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='main',
            name='commenting_state',
            field=models.CharField(default=b'C', max_length=1, choices=[(b'O', b'Open'), (b'C', b'Closed'), (b'T', b'Timestamped')]),
        ),
        migrations.AddField(
            model_name='sectionpage',
            name='commenting_close_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='sectionpage',
            name='commenting_open_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='languagepage',
            name='commenting_state',
            field=models.CharField(blank=True, max_length=1, null=True, choices=[(b'O', b'Open'), (b'C', b'Closed'), (b'T', b'Timestamped')]),
        ),
    ]
