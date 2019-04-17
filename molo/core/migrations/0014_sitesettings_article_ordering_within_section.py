# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-16 12:59
from __future__ import unicode_literals

from django.db import migrations
import django_enumfield.db.fields
import molo.core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_add_email_to_forms'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesettings',
            name='article_ordering_within_section',
            field=django_enumfield.db.fields.EnumField(blank=True, default=1, enum=molo.core.models.ArticleOrderingChoices, help_text='Ordering of articles within a section', null=True),
        ),
    ]
