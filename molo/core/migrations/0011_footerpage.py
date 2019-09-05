# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_add_banner_to_homepage'),
    ]

    operations = [
        migrations.CreateModel(
            name='FooterPage',
            fields=[
                ('articlepage_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.ArticlePage', on_delete=models.SET_NULL)),
            ],
            options={
                'abstract': False,
            },
            bases=('core.articlepage',),
        ),
    ]
