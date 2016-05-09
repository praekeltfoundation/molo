from molo.core.models import ArticlePage, SiteSettings, LanguagePage

from {{cookiecutter.app_name}} import celery_app

from datetime import datetime


@celery_app.task(ignore_result=True)
def rotate_content():
    d = datetime.now()
    hour = d.hour + d.minute / 60. + d.second / 3600.
    if SiteSettings.content_rotation_time == hour:
        language_page = LanguagePage.objects.live().first()
        if language_page:
            random_article = ArticlePage.objects.live().filter(
                featured_in_latest=False).order_by('?').first()
            if random_article:
                random_article.featured_in_latest = True
                random_article.save_revision().publish()

                article = language_page.latest_articles().last()
                article.featured_in_latest = False
                article.save_revision().publish()
