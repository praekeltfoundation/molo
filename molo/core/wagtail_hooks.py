from django.conf.urls import re_path

from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.templatetags.static import static
from django.utils.html import format_html

from wagtail.core import hooks
from wagtail.admin.menu import MenuItem
from wagtail.admin.site_summary import SummaryItem
from wagtail.admin.widgets import Button
from wagtail.contrib.modeladmin.options import modeladmin_register

from molo.core import views
from molo.core.admin import AdminViewGroup
from django.db.models.query import QuerySet
from molo.core.api import urls as molo_api_urls
from molo.core.utils import copy_translation_pages
from molo.core.models import Languages, ArticlePage
from molo.core.utils import create_new_article_relations


@hooks.register('register_admin_urls')
def urlconf_translations():
    return [
        re_path(
            r'^translations/add/(?P<page_id>\d+)/(?P<locale>[\w\-\_]+)/$',
            views.add_translation,
            name='add_translation'),
    ]


modeladmin_register(AdminViewGroup)


@hooks.register('construct_explorer_page_queryset')
def show_main_language_only(parent_page, pages, request):
    main_language = Languages.for_site(
        request._wagtail_site).languages.filter(
            is_main_language=True).first()
    if pages and main_language and parent_page.depth > 2:

        if isinstance(pages, QuerySet):
            for page in pages:
                has_lang = hasattr(page.specific, 'language')
                if 'indexpage' in page.slug or not has_lang:
                    continue
                elif not page.specific:
                    pages = pages.exclude(pk=page.pk)
                elif not page.specific.language:
                    pages = pages.exclude(pk=page.pk)
                elif page.specific.language.pk != main_language.pk:
                    pages = pages.exclude(pk=page.pk)
            return pages
        else:
            specific_pages = [page.specific for page in pages]
            new_pages = [page for page in specific_pages
                         if page.language and
                         page.language.pk == main_language.pk]
            return new_pages
    return pages


@hooks.register('after_copy_page')
def add_new_tag_article_relations(request, page, new_page):
    create_new_article_relations(page, new_page)


@hooks.register('after_copy_page')
def copy_translation_pages_hook(request, page, new_page):
    copy_translation_pages(page, new_page)


@hooks.register('before_delete_page')
def delete_page_translations(request, page):
    # If this is the main language page then we want to delete all translations
    # but Main and Index pages don't have a language or translations
    if request.method == 'POST' and hasattr(page.specific, 'language') and \
            page.specific.language.is_main_language:
        for translation in page.specific.translated_pages.all():
            translation.delete()


# API admin
@hooks.register("register_admin_urls")
def add_import_view():
    return molo_api_urls.urlpatterns


@hooks.register('register_admin_menu_item')
def register_api_menu_item():
    return MenuItem(
        _('API'),
        reverse('site-import'),
        classnames='icon icon-download',
    )


class LanguageSummaryItem(SummaryItem):
    order = 500
    template = 'wagtail/site_languages_summary.html'

    def get_context(self):
        languages = Languages.for_site(
            self.request._wagtail_site).languages.all()
        return {
            'summaries': [{
                'language': l.get_locale_display(),
                'total': ArticlePage.objects.all().filter(
                    language=l).count()
            }for l in languages],
        }


@hooks.register('construct_homepage_summary_items')
def add_languages_summary_item(request, items):
    items.append(LanguageSummaryItem(request))


class LanguageErrorMessage(SummaryItem):
    order = 100
    template = 'wagtail/language_error_message.html'


@hooks.register('construct_homepage_panels')
def add_language_error_message_panel(request, panels):
    if not Languages.for_site(
            request._wagtail_site).languages.all().exists():
        panels[:] = [LanguageErrorMessage(request)]


@hooks.register('construct_main_menu')
def hide_menu_items_if_no_language(request, menu_items):
    if not Languages.for_site(
            request._wagtail_site).languages.all().exists():
        menu_items[:] = [
            item for item in menu_items if (
                item.name == 'settings' or
                item.name == 'api')]


@hooks.register('construct_main_menu')
def hide_site_import_if_not_in_importer_group(request, menu_items):
    if not User.objects.filter(
            pk=request.user.pk,
            groups__name='Site Importers').exists():
        menu_items[:] = [
            item for item in menu_items if item.name != 'api']


@hooks.register('construct_main_menu')
def show_explorer_only_to_users_have_access(request, menu_items):
    if (request.user.is_superuser or
        User.objects.filter(pk=request.user.pk, groups__name__in=[
            'Moderator', 'Editor']).exists()):
        return menu_items
    if User.objects.filter(pk=request.user.pk, groups__name__in=[
            'Comment Moderator', 'Expert', 'Wagtail Login Only']).exists():
        menu_items[:] = [
            item for item in menu_items if item.name != 'explorer']


@hooks.register('register_page_listing_more_buttons')
def page_listing_some_more_buttons(page, page_perms, is_parent=False):
    yield Button(
        _('Copy to All Countries'),
        reverse('copy-to-all-confirm', args=(page.id,)),
        attrs={'copy_to_all_confirm': _("Copy page '{title}'").format(
            title=page.get_admin_display_title()
        )},
        priority=40
    )


@hooks.register('insert_global_admin_css')
def global_admin_css():
    return format_html(
        '<link rel="stylesheet" href="{}">', static('css/wagtail-admin.css'))
