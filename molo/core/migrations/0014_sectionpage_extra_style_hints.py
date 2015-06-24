# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_articlepage_featured_in_homepage'),
    ]

    operations = [
        migrations.AddField(
            model_name='sectionpage',
            name='extra_style_hints',
            field=models.TextField(default=b'', help_text='Styling options that can be applied to this section and all its descendants', null=True, blank=True),
        ),
    ]
