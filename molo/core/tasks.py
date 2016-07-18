from datetime import datetime

from celery import task

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from molo.core.content_import import api
from molo.core.models import (
    ArticlePage, Main, SectionIndexPage, SiteLanguage, SectionPage)

from wagtail.contrib.settings.context_processors import SettingsProxy
from wagtail.wagtailcore.models import Site


IMPORT_EMAIL_TEMPLATE = "core/content_import/import_email.html"
VALIDATE_EMAIL_TEMPLATE = "core/content_import/validate_email.html"


@task(ignore_result=True)
def rotate_content():
    main_lang = SiteLanguage.objects.filter(is_main_language=True).first()
    main = Main.objects.all().first()
    index = SectionIndexPage.objects.live().first()
    site = Site.objects.get(is_default_site=True)
    settings = SettingsProxy(site)
    site_settings = settings['core']['SiteSettings']
    if main and index:
        if site_settings.content_rotation_time == datetime.now().hour:
            if site_settings.content_rotation:
                rotate_latest(main_lang, index, main)
            rotate_featured_in_homepage(main_lang)


def rotate_latest(main_lang, index, main):
    random_article = ArticlePage.objects.live().filter(
        featured_in_latest=False, languages__language__id=main_lang.id
    ).descendant_of(index).order_by('?').first()
    if random_article:
        random_article.featured_in_latest = True
        random_article.save_revision().publish()

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
