# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def create_tag_index(apps, schema_editor):
    from molo.core.models import TagIndexPage, Main
    main = Main.objects.all().first()

    if main:
        tag_index = TagIndexPage(title='Tags', slug='tags')
        main.add_child(instance=tag_index)
        tag_index.save_revision().publish()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0056_tag_navigation'),
    ]

    operations = [
        migrations.RunPython(create_tag_index),
    ]
