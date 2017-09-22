# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def delete_imageinfo(apps, schema_editor):
    ImageInfo = apps.get_model('core.ImageInfo')
    ImageInfo.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0070_add_service_directory_api'),
    ]

    operations = [
        migrations.RunPython(delete_imageinfo),
    ]
