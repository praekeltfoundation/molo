# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0024_alter_page_content_type_on_delete_behaviour'),
        ('core', '0024_adding_active_language_filed_to_site_language_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='LanguageRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.ForeignKey(related_name='+', to='core.SiteLanguage')),
                ('page', modelcluster.fields.ParentalKey(related_name='languages', to='wagtailcore.Page')),
            ],
        ),
        migrations.RemoveField(
            model_name='articlepage',
            name='language',
        ),
        migrations.RemoveField(
            model_name='homepage',
            name='language',
        ),
        migrations.RemoveField(
            model_name='sectionpage',
            name='language',
        ),
    ]
