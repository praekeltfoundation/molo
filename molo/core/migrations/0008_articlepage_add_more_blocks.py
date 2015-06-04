# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtail.wagtailcore.fields
import molo.core.blocks
import wagtail.wagtailimages.blocks
import wagtail.wagtailcore.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_articlepage_body'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articlepage',
            name='body',
            field=wagtail.wagtailcore.fields.StreamField([(b'heading', wagtail.wagtailcore.blocks.CharBlock(classname=b'full title')), (b'paragraph', molo.core.blocks.MarkDownBlock()), (b'image', wagtail.wagtailimages.blocks.ImageChooserBlock()), (b'list', wagtail.wagtailcore.blocks.ListBlock(wagtail.wagtailcore.blocks.CharBlock(label=b'Item'))), (b'numbered_list', wagtail.wagtailcore.blocks.ListBlock(wagtail.wagtailcore.blocks.CharBlock(label=b'Item'))), (b'page', wagtail.wagtailcore.blocks.PageChooserBlock())], null=True, blank=True),
            preserve_default=True,
        ),
    ]
