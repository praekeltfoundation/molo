from datetime import datetime

from celery import task
from time import strptime

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from molo.core.content_import import api
from molo.core.models import (
    ArticlePage, Main, SectionIndexPage, SiteLanguage, SectionPage)

from wagtail.contrib.settings.context_processors import SettingsProxy
from wagtail.wagtailcore.models import Site
from django.utils import timezone

IMPORT_EMAIL_TEMPLATE = "core/content_import/import_email.html"
VALIDATE_EMAIL_TEMPLATE = "core/content_import/validate_email.html"


@task(ignore_result=True)
def rotate_content():
    """ this method gets the parameters that are needed for rotate_latest
    and rotate_featured_in_homepage methods, and calls them both"""
    # getting the content rotation settings from site settings
    main_lang = SiteLanguage.objects.filter(is_main_language=True).first()
    main = Main.objects.all().first()
    index = SectionIndexPage.objects.live().first()
    site = Site.objects.get(is_default_site=True)
    settings = SettingsProxy(site)
    site_settings = settings['core']['SiteSettings']
    day = datetime.today().weekday()
    # creates a days of the week list
    days = [
        site_settings.monday, site_settings.tuesday, site_settings.wednesday,
        site_settings.thursday, site_settings.friday, site_settings.saturday,
        site_settings.sunday]
    # calls the two rotate methods with the necessary params
    if main and index:
        rotate_latest(main_lang, index, main, site_settings, days, day)
        rotate_featured_in_homepage(main_lang)


def rotate_latest(main_lang, index, main, site_settings, days, day):
    """This rotates all the articles that have been marked as
    featured_in_latest. It checks whether current date falls within the set
    date range for content rotation. It then checks whether the current weekday
    is set to rotate, and then rotates an articles for each hour the admin has
    set."""
    if site_settings.content_rotation_start_date and \
            site_settings.content_rotation_end_date:
        if site_settings.content_rotation_start_date < timezone.now() \
                < site_settings.content_rotation_end_date:
            # checks if the current weekday is set to rotate
            if days[day - 1]:
                for time in site_settings.time:
                    time = strptime(str(time), '%H:%M:%S.%f')
                    if time.tm_hour == datetime.now().hour:
                        # get a random article, set it to feature in latest
                        random_article = ArticlePage.objects.live().filter(
                            featured_in_latest=False,
                            languages__language__id=main_lang.id
                        ).descendant_of(index).order_by('?').first()
                        if random_article:
                            random_article.featured_in_latest = True
                            random_article.save_revision().publish()

                            # set the last featured_in_latest article to false
                            article = main.latest_articles().last()
                            article.featured_in_latest = False
                            article.save_revision().publish()


def rotate_featured_in_homepage(main_lang):
    for section in SectionPage.objects.all():
        if section.featured_in_homepage_rotation:
            random_article = ArticlePage.objects.live().filter(
                featured_in_homepage=False,
                languages__language__id=main_lang.id
            ).child_of(section).order_by('?').first()
            if random_article:
                random_article.featured_in_homepage = True
                random_article.save_revision().publish()
                article = section.featured_in_homepage_articles().last()
                article.featured_in_homepage = False
                article.save_revision().publish()


def send_import_email(to_email, context):
    from_email = settings.FROM_EMAIL
    subject = settings.CONTENT_IMPORT_SUBJECT
    body = render_to_string(IMPORT_EMAIL_TEMPLATE, context)
    email_message = EmailMessage(subject, body, from_email, [to_email])
    email_message.send()


def send_validate_email(to_email, context):
    from_email = settings.FROM_EMAIL
    subject = settings.CONTENT_IMPORT_SUBJECT
    body = render_to_string(VALIDATE_EMAIL_TEMPLATE, context)
    email_message = EmailMessage(subject, body, from_email, [to_email])
    email_message.send()


@task(ignore_result=True)
def import_content(data, locales, username, email, host):
    repos = api.get_repos(data)
    result = api.validate_content(repos, locales)

    if not result['errors']:
        api.import_content(repos, locales)

    send_import_email(email, {
        'name': username,
        'host': host,
        'errors': result['errors'],
        'warnings': result['warnings']
    })


@task(ignore_result=True)
def validate_content(data, locales, username, email, host):
    repos = api.get_repos(data)
    result = api.validate_content(repos, locales)

    send_import_email(email, {
        'name': username,
        'host': host,
        'type': 'import_failure',
        'errors': result['errors'],
        'warnings': result['warnings']
    })
