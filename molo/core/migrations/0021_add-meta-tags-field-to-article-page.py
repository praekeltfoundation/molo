# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import modelcluster.fields
import modelcluster.contrib.taggit


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('core', '0020_add-social-media-fields-to-article-page'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticlePageMetaDataTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_object', modelcluster.fields.ParentalKey(related_name='metadata_tagged_items', to='core.ArticlePage')),
                ('tag', models.ForeignKey(related_name='core_articlepagemetadatatag_items', to='taggit.Tag')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='articlepage',
            name='metadata_tags',
            field=modelcluster.contrib.taggit.ClusterTaggableManager(to='taggit.Tag', through='core.ArticlePageMetaDataTag', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags'),
        ),
    ]
