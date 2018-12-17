# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtail.core.fields
import molo.core.blocks
import wagtail.images.blocks
import wagtail.core.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_articlepage_body'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articlepage',
            name='body',
            field=wagtail.core.fields.StreamField([(b'heading', wagtail.core.blocks.CharBlock(classname=b'full title')), (b'paragraph', molo.core.blocks.MarkDownBlock()), (b'image', wagtail.images.blocks.ImageChooserBlock()), (b'list', wagtail.core.blocks.ListBlock(wagtail.core.blocks.CharBlock(label=b'Item'))), (b'numbered_list', wagtail.core.blocks.ListBlock(wagtail.core.blocks.CharBlock(label=b'Item'))), (b'page', wagtail.core.blocks.PageChooserBlock())], null=True, blank=True),
            preserve_default=True,
        ),
    ]
