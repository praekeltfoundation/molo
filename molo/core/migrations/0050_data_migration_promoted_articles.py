# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def set_promote_start_date(apps, schema_editor):
    ArticlePage = apps.get_model("core", "ArticlePage")

    latest_articles = ArticlePage.objects.filter(featured_in_latest=True)
    homepage_articles = ArticlePage.objects.filter(featured_in_homepage=True)
    section_articles = ArticlePage.objects.filter(featured_in_section=True)

    for article in latest_articles:
      article.featured_in_latest_start_date = article.latest_revision_created_at
      article.save()
    for article in homepage_articles:
      article.featured_in_homepage_start_date = article.latest_revision_created_at
      article.save()
    for article in section_articles:
      article.featured_in_section_start_date = article.latest_revision_created_at
      article.save()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0049_add_social_media_links_to_site_settings'),
    ]

    operations = [
        migrations.RunPython(set_promote_start_date),
    ]
