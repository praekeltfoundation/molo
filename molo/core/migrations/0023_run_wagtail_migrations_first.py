# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.core.management.sql import emit_pre_migrate_signal


def run_wagtail_migration_before_core(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    emit_pre_migrate_signal(verbosity=2, interactive=False, db=db_alias)


class Migration(migrations.Migration):
    dependencies = [
        ('wagtailcore', '0052_pagelogentry'),
        ('core', '0022_auto_20201215_0734'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(run_wagtail_migration_before_core),
    ]
