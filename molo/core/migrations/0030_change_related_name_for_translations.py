# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_add_UUID_filed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pagetranslation',
            name='translated_page',
            field=models.OneToOneField(related_name='source_page', to='wagtailcore.Page', on_delete=models.SET_NULL),
        ),
    ]
