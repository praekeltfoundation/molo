# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_add_translation_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteLanguage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(help_text="The page title as you'd like it to be seen by the public", max_length=255, verbose_name='language name')),
                ('code', models.CharField(help_text='The language code as specified in iso639-2', max_length=255, verbose_name='language code')),
                ('is_main_language', models.BooleanField(default=False, verbose_name='main Language', editable=False)),
            ],
            options={
                'verbose_name': 'Language',
            },
        ),
        migrations.RemoveField(
            model_name='languagepage',
            name='main_language',
        ),
        migrations.AlterField(
            model_name='articlepage',
            name='language',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='core.SiteLanguage', null=True),
        ),
        migrations.AlterField(
            model_name='homepage',
            name='language',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='core.SiteLanguage', null=True),
        ),
        migrations.AlterField(
            model_name='sectionpage',
            name='language',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='core.SiteLanguage', null=True),
        ),
    ]
