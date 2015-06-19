# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0015_add_more_verbose_names'),
        ('wagtailimages', '0006_add_verbose_names'),
        ('core', '0009_sectionpage_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepage',
            name='banner',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='wagtailimages.Image', null=True),
        ),
        migrations.AddField(
            model_name='homepage',
            name='banner_link_page',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='wagtailcore.Page', help_text='Optional page to which the banner will link to', null=True),
        ),
    ]
