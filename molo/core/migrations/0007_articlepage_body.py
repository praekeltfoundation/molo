# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtail.wagtailcore.fields
import molo.core.blocks
import wagtail.wagtailimages.blocks
import wagtail.wagtailcore.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_add_help_text_to_language_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='articlepage',
            name='body',
            field=wagtail.wagtailcore.fields.StreamField([(b'heading', wagtail.wagtailcore.blocks.CharBlock(classname=b'full title')), (b'paragraph', molo.core.blocks.MarkDownBlock()), (b'image', wagtail.wagtailimages.blocks.ImageChooserBlock())], null=True, blank=True),
            preserve_default=True,
        ),
    ]
