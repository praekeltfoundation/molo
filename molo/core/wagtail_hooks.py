from django.conf.urls import url

from molo.core.models import LanguageRelation, PageTranslation, Languages

from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from wagtail.wagtailcore import hooks
from wagtail.wagtailcore.models import Page
from wagtail.wagtailadmin.menu import MenuItem
from wagtail.wagtailadmin.site_summary import SummaryItem

from . import views


@hooks.register('register_admin_urls')
def urlconf_translations():
    return [
        url(
            r'^translations/add/(?P<page_id>\d+)/(?P<locale>[\w\-\_]+)/$',
            'molo.core.views.add_translation',
            name='add_translation'),
    ]


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        url(r'^import-git/$',
            views.import_from_git,
            name='import-from-git'),
    ]


@hooks.register('construct_explorer_page_queryset')
def show_main_language_only(parent_page, pages, request):
    main_language = Languages.for_site(request.site).languages.filter(
        is_main_language=True).first()
    if main_language and parent_page.depth > 2:
        return pages.filter(languages__language__locale=main_language.locale)
    return pages


@hooks.register('after_copy_page')
def copy_translation_pages(request, page, new_page):
    current_site = page.get_site()
    destination_site = new_page.get_site()
    if not (current_site is destination_site):
        page.specific.copy_languages(current_site, destination_site)
    languages = Languages.for_site(destination_site).languages
    if (languages.filter(
            is_main_language=True).exists() and
            not new_page.languages.exists()):
        LanguageRelation.objects.create(
            page=new_page,
            language=languages.filter(
                is_main_language=True).first())

    for translation in page.translations.all():
        translation.translated_page.specific.copy_languages(current_site, destination_site)
        new_translation = translation.translated_page.copy(
            to=new_page.get_parent())
        new_l_rel = LanguageRelation.objects.get(page=new_translation)
        new_l_rel.language = languages.filter(
            locale=translation.translated_page.languages.all().first(
            ).language.locale).first()
        new_l_rel.save()
        PageTranslation.objects.create(
            page=new_page,
            translated_page=new_translation)


@hooks.register('register_admin_menu_item')
def register_import_menu_item():
    return MenuItem(
        _('Import content'),
        urlresolvers.reverse('import-from-git'),
        classnames='icon icon-download',
    )


class LanguageSummaryItem(SummaryItem):
    order = 500
    template = 'admin/site_languages_summary.html'

    def get_context(self):
        languages = Languages.for_site(self.request.site).languages.all()
        return {
            'summaries': [{
                'language': l.get_locale_display(),
                'total': Page.objects.filter(
                    languages__language__id=l.id).count()
            }for l in languages],
        }


@hooks.register('construct_homepage_summary_items')
def add_languages_summary_item(request, items):
    items.append(LanguageSummaryItem(request))


class LanguageErrorMessage(SummaryItem):
    order = 100
    template = 'admin/language_error_message.html'


@hooks.register('construct_homepage_panels')
def add_language_error_message_panel(request, panels):
    if not Languages.for_site(request.site).languages.all().exists():
        panels[:] = [LanguageErrorMessage(request)]


@hooks.register('construct_main_menu')
def hide_menu_items_if_no_language(request, menu_items):
    if not Languages.for_site(request.site).languages.all().exists():
        menu_items[:] = [
            item for item in menu_items if (
                item.name == 'settings' or item.name == 'import-content')]


@hooks.register('construct_main_menu')
def hide_import_content_if_not_uc_user(request, menu_items):
    if not User.objects.filter(
            pk=request.user.pk,
            groups__name='Universal Core Importers').exists():
        menu_items[:] = [
            item for item in menu_items if item.name != 'import-content']


@hooks.register('construct_main_menu')
def show_explorer_only_to_users_have_access(request, menu_items):
    if User.objects.filter(pk=request.user.pk, groups__name__in=[
            'Comment Moderator', 'Expert', 'Wagtail Login Only']).exists():
        menu_items[:] = [
            item for item in menu_items if item.name != 'explorer']
