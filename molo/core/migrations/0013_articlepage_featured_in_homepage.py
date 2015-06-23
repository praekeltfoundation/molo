# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_add_featured_fields_to_articlepage'),
    ]

    operations = [
        migrations.AddField(
            model_name='articlepage',
            name='featured_in_homepage',
            field=models.BooleanField(default=False, help_text='Article to be featured in the Homepage within the Section module'),
        ),
    ]
