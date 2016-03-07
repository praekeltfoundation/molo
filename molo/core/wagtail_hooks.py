from django.conf.urls import url

from wagtailmodeladmin.options import(
    ModelAdmin, wagtailmodeladmin_register)
from wagtail.wagtailcore import hooks

from molo.core.models import SiteLanguage

from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _


from wagtail.wagtailadmin.menu import MenuItem

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

wagtailmodeladmin_register(LanguageModelAdmin)


@hooks.register('register_admin_urls')
def urlconf_translations():
    return [
        url(
            r'^translations/add/(?P<page_id>\d+)/(?P<locale>\w+)/$',
            'molo.core.views.add_translation',
            name='add_translation'),
    ]


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        url(r'^import-ucd/$',
            views.import_from_ucd,
            name='import-from-ucd'),
    ]


@hooks.register('construct_explorer_page_queryset')
def show_main_language_only(parent_page, pages, request):
    main_language = SiteLanguage.objects.filter(is_main_language=True).first()

    if main_language and not parent_page.depth == 1:
        return pages.filter(languages__language__id=main_language.id)

    return pages


@hooks.register('register_admin_menu_item')
def register_import_menu_item():
    return MenuItem(
        _('Import content'),
        urlresolvers.reverse('import-from-ucd'),
        classnames='icon icon-download',
    )
