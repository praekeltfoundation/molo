# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_add_tags_to_article'),
    ]

    operations = [
        migrations.AddField(
            model_name='languagepage',
            name='main_language',
            field=models.BooleanField(default=False, help_text='The main language of the site'),
        ),
    ]
