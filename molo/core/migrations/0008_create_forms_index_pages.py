# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def create_form_index(apps, schema_editor):
    from molo.core.models import FormIndexPage, Main
    main = Main.objects.first()

    if main:
        form_index = FormIndexPage(title='Forms', slug='forms')
        main.add_child(instance=form_index)
        form_index.save_revision().publish()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_add_contact_form'),
    ]

    operations = [
        migrations.RunPython(create_form_index),
    ]
