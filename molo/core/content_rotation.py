from molo.core.models import ArticlePage, LanguagePage

from wagtail.wagtailcore.models import Site
from wagtail.contrib.settings.context_processors import SettingsProxy

from datetime import datetime


def rotate_content():
    site = Site.objects.get(is_default_site=True)
    settings = SettingsProxy(site)
    site_settings = settings['core']['SiteSettings']
    if site_settings.content_rotation and \
            site_settings.content_rotation_time == datetime.now().hour:
        languages = LanguagePage.objects.live()
        for language_page in languages:
            random_article = ArticlePage.objects.live().filter(
                featured_in_latest=False
            ).descendant_of(language_page).order_by('?').first()
            if random_article:
                random_article.featured_in_latest = True
                random_article.save_revision().publish()

                article = language_page.latest_articles().last()
                article.featured_in_latest = False
                article.save_revision().publish()
