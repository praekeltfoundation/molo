# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def convert_media_to_molo_media(apps, schema_editor):
    from molo.core.models import MoloMedia, ArticlePage
    from wagtailmedia.models import Media

    for media in Media.objects.all():
        new_media = MoloMedia.objects.create(
            title=media.title, file=media.file, duration=media.duration,
            type=media.type, width=media.width,
            height=media.height, thumbnail=media.thumbnail)

        for article in ArticlePage.objects.all():
            for block in article.body:
                if block.block_type is 'media' and block.value is media.id:
                    block.value = new_media.id
                    article.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0066_add_custom_media_model'),
    ]

    operations = [
        migrations.RunPython(convert_media_to_molo_media),
    ]
