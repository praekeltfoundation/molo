import csv
import random
import logging

from io import BytesIO
from datetime import datetime

from celery import task
from time import strptime

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.core import management
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404

from molo.core.utils import (
    create_new_article_relations, copy_translation_pages)
from molo.core.models import (
    Site,
    ArticlePage,
    Main,
    SectionIndexPage,
    SectionPage,
    Languages,
    SiteSettings,
    BannerIndexPage,
    FooterIndexPage,
    TagIndexPage,
)
from molo.core.api.importers import (
    RecordKeeper,
    LanguageImporter,
    ImageImporter,
    ContentImporter,
    Logger,
)
from molo.core.api.constants import ACTION
from django.utils import timezone

from six import iteritems

from wagtail.wagtailcore.models import Page


IMPORT_EMAIL_TEMPLATE = "content_import/import_email.html"
VALIDATE_EMAIL_TEMPLATE = "content_import/validate_email.html"
COPY_EMAIL_TEMPLATE = "core/copy_email.html"
COPY_FAILED_EMAIL_TEMPLATE = "core/copy_failed_email.html"


@task(ignore_result=True)
def rotate_content(day=None):
    """ this method gets the parameters that are needed for rotate_latest
    and rotate_featured_in_homepage methods, and calls them both"""
    # getting the content rotation settings from site settings

    for main in Main.objects.all():
        site = main.sites_rooted_here.all().first()
        main_lang = Languages.for_site(site).languages.filter(
            is_main_language=True).first()
        index = SectionIndexPage.objects.live().child_of(main).first()
        site_settings = SiteSettings.for_site(site)
        if day is None:
            day = datetime.today().weekday()

        # calls the two rotate methods with the necessary params
        if main and index:
            rotate_latest(main_lang, index, main, site_settings, day)
            rotate_featured_in_homepage(main_lang, day, main)


@task(ignore_result=True)
def publish_scheduled_pages():
    management.call_command(
        'publish_scheduled_pages', verbosity=0, interactive=False)


@task(ignore_result=True)
def clearsessions():
    # Expired sessions will only be cleared roughly once an hour - randomly
    if random.randint(0, 59) == 0:
        management.call_command(
            'clearsessions', verbosity=0, interactive=False)


@task(ignore_result=True)
def demote_articles():
    ArticlePage.objects.live().filter(
        featured_in_latest_end_date__lte=datetime.now()).update(
            featured_in_latest=False,
            featured_in_latest_start_date=None,
            featured_in_latest_end_date=None)
    ArticlePage.objects.live().filter(
        featured_in_section_end_date__lte=datetime.now()).update(
            featured_in_section=False,
            featured_in_section_start_date=None,
            featured_in_section_end_date=None)
    ArticlePage.objects.live().filter(
        featured_in_homepage_end_date__lte=datetime.now()).update(
            featured_in_homepage=False,
            featured_in_homepage_start_date=None,
            featured_in_homepage_end_date=None)


@task(ignore_result=True)
def promote_articles():
    ArticlePage.objects.live().filter(
        featured_in_latest_start_date__lte=datetime.now()).update(
        featured_in_latest=True)
    ArticlePage.objects.live().filter(
        featured_in_section_start_date__lte=datetime.now()).update(
        featured_in_section=True)
    ArticlePage.objects.live().filter(
        featured_in_homepage_start_date__lte=datetime.now()).update(
        featured_in_homepage=True)


def get_days_section(section=None):
        return [
            section.monday_rotation, section.tuesday_rotation,
            section.wednesday_rotation, section.thursday_rotation,
            section.friday_rotation, section.saturday_rotation,
            section.sunday_rotation]


def get_days_site_settings(site_settings):
        return [
            site_settings.monday_rotation, site_settings.tuesday_rotation,
            site_settings.wednesday_rotation, site_settings.thursday_rotation,
            site_settings.friday_rotation, site_settings.saturday_rotation,
            site_settings.sunday_rotation]


def rotate_latest(main_lang, index, main, site_settings, day):
    """This rotates all the articles that have been marked as
    featured_in_latest. It checks whether current date falls within the set
    date range for content rotation. It then checks whether the current weekday
    is set to rotate, and then rotates an articles for each hour the admin has
    set."""

    def demote_last_featured_article():
        # set the last featured_in_latest article to false
        if main.latest_articles().live().count() >= 2:
            article = main.latest_articles().live().last()
            article.featured_in_latest = False
            article.featured_in_latest_start_date = None
            article.featured_in_latest_end_date = None
            article.save_revision().publish()

    days = get_days_site_settings(site_settings)
    # checks if the current date is within the content rotation range
    if site_settings.content_rotation_start_date and \
            site_settings.content_rotation_end_date:
        if site_settings.content_rotation_start_date < timezone.now() \
                < site_settings.content_rotation_end_date:

            # checks if the current weekday is set to rotate
            if days[day]:
                for time in site_settings.time:
                    time = strptime(str(time), '%H:%M:%S')
                    if time.tm_hour == datetime.now().hour:
                        # get a random article
                        random_article = ArticlePage.objects.live().filter(
                            featured_in_latest=False,
                            languages__language__id=main_lang.id
                        ).descendant_of(index).order_by('?').exact_type(
                            ArticlePage).first()
                        # set random article to feature in latest
                        if random_article:
                            random_article.featured_in_latest_start_date = \
                                datetime.now()
                            random_article.save_revision().publish()
                            promote_articles()
                            demote_last_featured_article()


def rotate_featured_in_homepage(main_lang, day, main):
    def demote_last_featured_article_in_homepage(section):
            articles = ArticlePage.objects.live().filter(
                featured_in_homepage=True,
                languages__language__id=main_lang.id
            ).descendant_of(section).order_by(
                '-featured_in_homepage_start_date')
            if articles.count() >= 2:
                article = articles.last()
                article.featured_in_homepage = False
                article.featured_in_homepage_start_date = None
                article.featured_in_homepage_end_date = None
                article.save_revision().publish()

    for section in SectionPage.objects.descendant_of(main):
        days = get_days_section(section)
        # checks if current date is within the rotation date range
        if section.content_rotation_start_date and \
                section.content_rotation_end_date:
            if section.content_rotation_start_date < timezone.now() \
                    < section.content_rotation_end_date:

                # checks if the current weekday is set to rotate
                if days[day]:
                    for time in section.time:
                        time = strptime(str(time), '%H:%M:%S')
                        if time.tm_hour == datetime.now().hour:
                            random_article = ArticlePage.objects.live().filter(
                                featured_in_homepage=False,
                                languages__language__id=main_lang.id
                            ).descendant_of(section).order_by('?').exact_type(
                                ArticlePage).first()

                            # promotes an article and bumps last one off list
                            if random_article:
                                random_article. \
                                    featured_in_homepage_start_date = \
                                    datetime.now()
                                random_article.save_revision().publish()
                                promote_articles()
                                demote_last_featured_article_in_homepage(
                                    section)


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


def send_copy_email(to_email, context, csv=None):
    from_email = settings.FROM_EMAIL
    subject = settings.CONTENT_COPY_SUBJECT \
        if hasattr(settings, 'CONTENT_COPY_SUBJECT') else 'Molo Content Copy'
    body = render_to_string(COPY_EMAIL_TEMPLATE, context)
    email_message = EmailMessage(subject, body, from_email, [to_email])
    if csv:
        email_message.attach('file.csv', csv.getvalue(), 'text/csv')
    email_message.send()


def send_copy_failed_email(to_email, context):
    from_email = settings.FROM_EMAIL
    subject = settings.CONTENT_COPY_FAILED_SUBJECT \
        if hasattr(settings, 'CONTENT_COPY_FAILED_SUBJECT') \
        else 'Molo Content Copy Failed'
    body = render_to_string(COPY_FAILED_EMAIL_TEMPLATE, context)
    email_message = EmailMessage(subject, body, from_email, [to_email])
    email_message.send()


@task(ignore_result=True)
def molo_consolidated_minute_task():
    """
    Purpose: To reduce the number of db connections, we run all
    tasks in 1 call
    """

    demote_articles()
    promote_articles()
    publish_scheduled_pages()
    clearsessions()


@task(ignore_result=True)
def copy_to_all_task(page_id, user_id, site_pk):
    # getting data needed
    user = User.objects.get(pk=user_id)
    site = Site.objects.get(pk=site_pk)
    page = get_object_or_404(Page, id=page_id).specific
    parent = page.get_parent()
    excluded_main = Main.objects.ancestor_of(page).first()
    errors = []

    # loop through all the mains except for the main the page exists in
    for main in Main.objects.all().exclude(pk=excluded_main.pk):
        new_page = None
        # search for the parent page in the destination site
        destination_parent = Page.objects.descendant_of(main).filter(
            Q(slug=parent.slug) | Q(title=parent.title))
        if destination_parent.exists():
            destination_parent = destination_parent.first()
            # if it exists, check to make sure the page doesn't already exist
            destination_page = Page.objects.descendant_of(
                destination_parent).filter(
                    Q(slug=page.slug) | Q(title=page.title))
            if not destination_page.exists():
                new_page = page.copy(
                    recursive='true',
                    to=destination_parent,
                    update_attrs={
                        'title': page.title,
                        'slug': page.slug,
                    },
                    keep_live='true',
                    user=user,
                )
                copy_translation_pages(page, new_page)
                create_new_article_relations(page, new_page)
                if page.status_string == 'scheduled' and \
                        new_page.status_string == 'draft' and \
                        new_page.go_live_at is not None:
                    new_page.save_revision().publish()
                elif new_page.status_string == 'draft':
                    new_page.save_revision()
            else:
                errors.append(str(
                    page.title + ' already exists in ' + main.title))
        else:
            errors.append(str(
                parent.title + ' does not exist in ' + main.title))

    send_copy_email(
        user.email,
        {
            'name': ((user.get_full_name() or user.username)
                     if user else None),
            'source': site,
            'logs': errors
        },)


@task(ignore_result=True)
def copy_sections_index(
        section_pk, user_pk, to_pk, copy_revisions, recursive, keep_live):
    section_index = SectionIndexPage.objects.get(pk=section_pk)
    user = User.objects.get(pk=user_pk) if user_pk else None
    to = Page.objects.get(pk=to_pk).specific
    try:
        section_index.copy(
            user=user,
            to=to,
            copy_revisions=copy_revisions,
            recursive=recursive,
            keep_live=keep_live,
            via_celery=True)

        old_main = section_index.get_site().root_page
        new_main = to.get_site().root_page
        create_new_article_relations(old_main, new_main)
        send_copy_email(user.email, {
            'name': (user.get_full_name() or user.username) if user else None,
            'source': section_index.get_parent().title,
            'to': to.title
        })
    except Exception as e:
        logging.error(e, exc_info=True)
        send_copy_failed_email(user.email, {
            'name': (user.get_full_name() or user.username) if user else None,
            'source': section_index.get_parent().title,
            'to': to.title
        })


@task(ignore_result=True)
def import_site(root_url, site_pk, user_pk):
    user = User.objects.get(pk=user_pk) if user_pk else None
    record_keeper = RecordKeeper()
    logger = Logger()
    site = Site.objects.get(pk=site_pk)

    language_importer = LanguageImporter(
        site.pk, root_url,
        record_keeper=record_keeper,
        logger=logger)
    image_importer = ImageImporter(
        site.pk, root_url,
        record_keeper=record_keeper,
        logger=logger)
    content_importer = ContentImporter(
        site.pk, root_url,
        record_keeper=record_keeper,
        logger=logger)

    try:
        # get languages
        language_importer.copy_site_languages()

        image_importer.import_images()

        # copy_content SectionIndexPage
        section_index_page = SectionIndexPage.objects.descendant_of(
            site.root_page).first()
        foreign_section_index_page_id = content_importer.get_foreign_page_id_from_type(  # noqa
            "core.SectionIndexPage")
        content_importer.copy_children(
            foreign_id=foreign_section_index_page_id,
            existing_node=section_index_page)

        # copy_content Banner Pages
        banner_index_page = BannerIndexPage.objects.descendant_of(
            site.root_page).first()
        foreign_banner_index_page_id = content_importer.get_foreign_page_id_from_type(  # noqa
            "core.BannerIndexPage")
        content_importer.copy_children(
            foreign_id=foreign_banner_index_page_id,
            existing_node=banner_index_page)

        # copy_content Footer Pages
        footer_index_page = FooterIndexPage.objects.descendant_of(
            site.root_page).first()
        foreign_footer_index_page_id = content_importer.get_foreign_page_id_from_type(  # noqa
            "core.FooterIndexPage")
        content_importer.copy_children(
            foreign_id=foreign_footer_index_page_id,
            existing_node=footer_index_page)

        # copy_content TagIndexPage
        tag_index_page = TagIndexPage.objects.descendant_of(
            site.root_page).first()
        foreign_tag_index_page_id = content_importer.get_foreign_page_id_from_type(  # noqa
            "core.TagIndexPage")
        content_importer.copy_children(
            foreign_id=foreign_tag_index_page_id,
            existing_node=tag_index_page)

        logger.log(ACTION, "Creating Recommended Articles")
        content_importer.create_recommended_articles()

        logger.log(ACTION, "Creating Related Sections")
        content_importer.create_related_sections()

        logger.log(ACTION, "Creating Nav Tag Relationships")
        content_importer.create_nav_tag_relationships()

        logger.log(ACTION, "Creating Section Tag Relationships")
        content_importer.create_section_tag_relationship()

        logger.log(ACTION, "Creating Banner Page Links")
        content_importer.create_banner_page_links()

        logger.log(ACTION, "Recreating Article Body")
        content_importer.recreate_article_body()

        # create CSV
        foreign_local_map = record_keeper.foreign_local_map["page_map"]

        csvfile = BytesIO()
        writer = csv.writer(csvfile)

        rows = [["foreign_id", "local_id"]]
        for foreign_id, local_id in iteritems(foreign_local_map):
            rows.append([foreign_id, local_id])

        writer.writerows(rows)

        # send email
        send_copy_email(
            user.email,
            {
                'name': ((user.get_full_name() or user.username)
                         if user else None),
                'source': root_url,
                'to': site.root_url,
                'logs': logger.get_email_logs()
            },
            csv=csvfile)
    except Exception as e:
        logging.error(e, exc_info=True)
        send_copy_failed_email(user.email, {
            'name': (user.get_full_name() or user.username) if user else None,
            'source': root_url,
            'to': site.root_url,
            'logs': logger.get_email_logs(),
        })
