# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_change_language_models'),
    ]

    operations = [
        migrations.AlterField(
            model_name='languagerelation',
            name='page',
            field=models.ForeignKey(related_name='languages', to='wagtailcore.Page'),
        ),
        migrations.AlterField(
            model_name='pagetranslation',
            name='page',
            field=models.ForeignKey(related_name='translations', to='wagtailcore.Page'),
        ),
    ]
