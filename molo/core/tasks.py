from molo.core.models import ArticlePage, Main, SiteLanguage, SectionIndexPage

from wagtail.wagtailcore.models import Site
from wagtail.contrib.settings.context_processors import SettingsProxy

from datetime import datetime
from celery import task


@task(ignore_result=True)
def rotate_content():
    main_lang = SiteLanguage.objects.filter(is_main_language=True).first()
    main = Main.objects.all().first()
    index = SectionIndexPage.objects.live().first()
    site = Site.objects.get(is_default_site=True)
    settings = SettingsProxy(site)
    site_settings = settings['core']['SiteSettings']
    if site_settings.content_rotation and \
            site_settings.content_rotation_time == datetime.now().hour:
        if main and index:
            random_article = ArticlePage.objects.live().filter(
                featured_in_latest=False, languages__language__id=main_lang.id
            ).descendant_of(index).order_by('?').first()
            if random_article:
                random_article.featured_in_latest = True
                random_article.save_revision().publish()

                article = main.latest_articles().last()
                article.featured_in_latest = False
                article.save_revision().publish()
