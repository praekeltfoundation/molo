from django.conf.urls import url

from molo.core.models import SiteLanguage

from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register)
from wagtail.wagtailcore import hooks
from wagtail.wagtailcore.models import Page
from wagtail.wagtailadmin.menu import MenuItem
from wagtail.wagtailadmin.site_summary import SummaryItem
from wagtail.wagtailadmin.widgets import ButtonWithDropdownFromHook

from wagtail.wagtailadmin.wagtail_hooks import page_listing_more_buttons

from . import views


class LanguageModelAdmin(ModelAdmin):
    model = SiteLanguage
    menu_label = 'Language'
    menu_icon = 'doc-full-inverse'
    list_display = ('locale', 'is_main_language', 'is_active')
    search_fields = ('title',)
    list_per_page = 20
    add_to_settings_menu = True
    ordering = ('-is_main_language', 'locale')
    menu_order = 100

modeladmin_register(LanguageModelAdmin)


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
    main_language = SiteLanguage.objects.filter(is_main_language=True).first()

    if main_language and not parent_page.depth == 2:
        return pages.filter(languages__language__id=main_language.id)

    return pages


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
        languages = SiteLanguage.objects.all()
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
    if not SiteLanguage.objects.all().exists():
        panels[:] = [LanguageErrorMessage(request)]


@hooks.register('construct_main_menu')
def hide_menu_items_if_no_language(request, menu_items):
    if not SiteLanguage.objects.all().exists():
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
    if (request.user.is_superuser or
        User.objects.filter(pk=request.user.pk, groups__name__in=[
            'Moderator', 'Editor']).exists()):
        return menu_items
    if User.objects.filter(pk=request.user.pk, groups__name__in=[
            'Comment Moderator', 'Expert', 'Wagtail Login Only']).exists():
        menu_items[:] = [
            item for item in menu_items if item.name != 'explorer']


@hooks.register('register_page_listing_buttons')
def page_custom_listing_buttons(page, page_perms, is_parent=False):
    yield ButtonWithDropdownFromHook(
        'More',
        hook_name='my_button_dropdown_hook',
        page=page,
        page_perms=page_perms,
        is_parent=is_parent,
        priority=50
    )


@hooks.register('register_page_listing_more_buttons')
def page_listing_buttons(page, page_perms, is_parent=False):
    """
    This removes the standard wagtail dropdown menu.

    This supresses the original 'More' dropdown menu because it breaks
    the expected behaviour of the yeild functionality used to add
    additional buttons in wagtail_hooks.
    """
    if page_perms.can_move():
        return None


@hooks.register('my_button_dropdown_hook')
def new_page_listing_buttons(page, page_perms, is_parent=False):
    """
    This inherits the buttons from wagtail's page_listing_more_buttons
    https://github.com/wagtail/wagtail/blob/stable/1.8.x/wagtail/wagtailadmin/wagtail_hooks.py#L94
    (i.e. the buttons that are put in the original drop down menu)
    This is done to avoid breakages should their hooks change in the future


    It iterates through the buttons and prevents the delete button
    from being added if the Page should not be deleteable from the admin UI
    """
    original_buttons = list(page_listing_more_buttons(page,
                                                      page_perms,
                                                      is_parent))
    if not hasattr(page.specific, 'hide_delete_button'):
        for b in original_buttons:
            yield b
    else:
        for b in original_buttons:
            if (hasattr(b, 'attrs') and
                    b.attrs.get('title').lower() != 'delete this page'):
                    yield b
