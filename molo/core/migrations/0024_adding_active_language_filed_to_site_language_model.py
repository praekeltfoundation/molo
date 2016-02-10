# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_adding_new_language_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitelanguage',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='active Language'),
        ),
    ]
