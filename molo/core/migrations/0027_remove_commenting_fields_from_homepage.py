# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_add_site_language_model'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='homepage',
            name='commenting_close_time',
        ),
        migrations.RemoveField(
            model_name='homepage',
            name='commenting_open_time',
        ),
        migrations.RemoveField(
            model_name='homepage',
            name='commenting_state',
        ),
    ]
