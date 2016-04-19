# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0023_alter_page_revision_on_delete_behaviour'),
        ('core', '0024_add_language_field_to_models'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('page', modelcluster.fields.ParentalKey(related_name='translations', to='wagtailcore.Page')),
                ('translated_page', models.ForeignKey(related_name='+', to='wagtailcore.Page')),
            ],
        ),
    ]
