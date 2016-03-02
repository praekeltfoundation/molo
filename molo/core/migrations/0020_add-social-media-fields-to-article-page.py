# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0010_change_on_delete_behaviour'),
        ('core', '0019_add_tags_to_article'),
    ]

    operations = [
        migrations.AddField(
            model_name='articlepage',
            name='social_media_description',
            field=models.TextField(null=True, verbose_name=b'description', blank=True),
        ),
        migrations.AddField(
            model_name='articlepage',
            name='social_media_image',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, verbose_name=b'Image', blank=True, to='wagtailimages.Image', null=True),
        ),
        migrations.AddField(
            model_name='articlepage',
            name='social_media_title',
            field=models.TextField(null=True, verbose_name=b'title', blank=True),
        ),
    ]
