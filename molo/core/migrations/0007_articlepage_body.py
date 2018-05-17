# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtail.core.fields
import molo.core.blocks
import wagtail.images.blocks
import wagtail.core.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_add_help_text_to_language_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='articlepage',
            name='body',
            field=wagtail.core.fields.StreamField([(b'heading', wagtail.core.blocks.CharBlock(classname=b'full title')), (b'paragraph', molo.core.blocks.MarkDownBlock()), (b'image', wagtail.images.blocks.ImageChooserBlock())], null=True, blank=True),
            preserve_default=True,
        ),
    ]
