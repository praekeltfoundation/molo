# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_add_tags_to_article'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticlePageTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('page', modelcluster.fields.ParentalKey(related_name='translations', to='core.ArticlePage')),
                ('translated_page', models.ForeignKey(related_name='+', to='core.ArticlePage')),
            ],
        ),
        migrations.CreateModel(
            name='HomePageTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('page', modelcluster.fields.ParentalKey(related_name='translations', to='core.HomePage')),
                ('translated_page', models.ForeignKey(related_name='+', to='core.HomePage')),
            ],
        ),
        migrations.CreateModel(
            name='SectionPageTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('page', modelcluster.fields.ParentalKey(related_name='translations', to='core.SectionPage')),
                ('translated_page', models.ForeignKey(related_name='+', to='core.SectionPage')),
            ],
        ),
    ]
