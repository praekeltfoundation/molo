# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_add_nullable_to_articlepage_sectionpage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='languagepage',
            name='code',
            field=models.CharField(help_text='The language code as specified in iso639-2', max_length=255),
            preserve_default=True,
        ),
    ]
