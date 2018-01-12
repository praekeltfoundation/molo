# -*- coding: utf-8 -*-
# flake8: noqa: E122
from __future__ import unicode_literals

from django.db import migrations, models
from django.core.management.sql import emit_post_migrate_signal
from molo.core.models import MoloMedia, ArticlePage
from wagtailmedia.models import Media


def convert_media_to_molo_media(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    try:
        # Django 1.9
        emit_post_migrate_signal(2, False, db_alias)
    except TypeError:
        # Django < 1.9
        try:
            # Django 1.8
            emit_post_migrate_signal(2, False, 'default', db_alias)
        except TypeError:  # Django < 1.8
            emit_post_migrate_signal([], 2, False, 'default', db_alias)

    for media in Media.objects.all():
        if media.type == 'video':
            new_media = MoloMedia.objects.create(
            title=media.title, file=media.file, duration=media.duration,
            type=media.type, width=media.width, height=media.height,
            thumbnail=media.thumbnail)
        else:
            new_media = MoloMedia.objects.create(
            title=media.title, file=media.file, duration=media.duration,
            type=media.type)
        media.file = None
        media.save()
        for article in ArticlePage.objects.all():
            for block in article.body:
                if block.block_type is 'media' and block.value is media.id:
                    block.value = new_media.id
                    article.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0067_promote_homepage_media'),
        ('wagtailmedia', '0003_copy_media_permissions_to_collections'),
    ]

    operations = [
        migrations.RunPython(convert_media_to_molo_media),
    ]
