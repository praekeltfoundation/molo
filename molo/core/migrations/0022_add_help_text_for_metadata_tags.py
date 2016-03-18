# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import modelcluster.contrib.taggit


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_add-meta-tags-field-to-article-page'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articlepage',
            name='metadata_tags',
            field=modelcluster.contrib.taggit.ClusterTaggableManager(to='taggit.Tag', through='core.ArticlePageMetaDataTag', blank=True, help_text='A comma-separated list of tags. This is not visible to the user.', verbose_name='Tags'),
        ),
    ]
