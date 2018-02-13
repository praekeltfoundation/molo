# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_add_mobile_number_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofilessettings',
            name='email_required',
            field=models.BooleanField(default=False, verbose_name='Email required'),
        ),
        migrations.AddField(
            model_name='userprofilessettings',
            name='show_email_field',
            field=models.BooleanField(default=False, verbose_name='Add email field to registration'),
        ),
    ]
