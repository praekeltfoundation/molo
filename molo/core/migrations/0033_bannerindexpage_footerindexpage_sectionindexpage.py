# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import molo.core.models


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0028_merge'),
        ('core', '0032_sitesettings_ga_tag_manager'),
    ]

    operations = [
        migrations.CreateModel(
            name='BannerIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(
                    parent_link=True, auto_created=True, primary_key=True,
                    serialize=False, to='wagtailcore.Page', on_delete=models.SET_NULL)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='FooterIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='wagtailcore.Page', on_delete=models.SET_NULL)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='SectionIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='wagtailcore.Page', on_delete=models.SET_NULL)),
                ('commenting_state', models.CharField(default=b'O', max_length=1, null=True, blank=True, choices=[(b'O', b'Open'), (b'C', b'Closed'), (b'D', b'Disabled'), (b'T', b'Timestamped')])),
                ('commenting_open_time', models.DateTimeField(null=True, blank=True)),
                ('commenting_close_time', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(molo.core.models.CommentedPageMixin, 'wagtailcore.page'),
        ),
        migrations.RemoveField(
            model_name='main',
            name='commenting_close_time',
        ),
        migrations.RemoveField(
            model_name='main',
            name='commenting_open_time',
        ),
        migrations.RemoveField(
            model_name='main',
            name='commenting_state',
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='ga_tag_manager',
            field=models.CharField(help_text='GA Tag Manager tracking code (e.g GTM-XXX)', max_length=255, null=True, verbose_name='GA Tag Manager', blank=True),
        ),
    ]
