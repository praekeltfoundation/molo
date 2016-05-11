# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_remove_commenting_fields_from_homepage'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='HomePage',
            new_name='BannerPage',
        ),
    ]
