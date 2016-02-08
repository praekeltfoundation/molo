# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_languagepage_main_language'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticlePageTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='HomePageTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='SectionPageTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.AddField(
            model_name='articlepage',
            name='language',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='homepage',
            name='language',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='sectionpage',
            name='language',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='sectionpagetranslation',
            name='page',
            field=modelcluster.fields.ParentalKey(related_name='translations', to='core.SectionPage'),
        ),
        migrations.AddField(
            model_name='sectionpagetranslation',
            name='translated_page',
            field=models.ForeignKey(related_name='+', to='core.SectionPage'),
        ),
        migrations.AddField(
            model_name='homepagetranslation',
            name='page',
            field=modelcluster.fields.ParentalKey(related_name='translations', to='core.HomePage'),
        ),
        migrations.AddField(
            model_name='homepagetranslation',
            name='translated_page',
            field=models.ForeignKey(related_name='+', to='core.HomePage'),
        ),
        migrations.AddField(
            model_name='articlepagetranslation',
            name='page',
            field=modelcluster.fields.ParentalKey(related_name='translations', to='core.ArticlePage'),
        ),
        migrations.AddField(
            model_name='articlepagetranslation',
            name='translated_page',
            field=models.ForeignKey(related_name='+', to='core.ArticlePage'),
        ),
    ]
