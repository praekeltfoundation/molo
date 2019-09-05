# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('user', models.OneToOneField(related_name='profile', primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL, on_delete=models.SET_NULL)),
                ('date_of_birth', models.DateField(null=True)),
                ('alias', models.CharField(max_length=128, null=True, blank=True)),
                ('avatar', models.ImageField(upload_to=b'users/profile', null=True, verbose_name=b'avatar', blank=True)),
            ],
        ),
    ]
