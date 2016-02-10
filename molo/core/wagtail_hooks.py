from django.conf.urls import url
from django.db.models import Q

from wagtailmodeladmin.options import(
    ModelAdmin, wagtailmodeladmin_register)
from wagtail.wagtailcore import hooks
from wagtail.wagtailcore.models import Page

from molo.core.models import SiteLanguage


class LanguageModelAdmin(ModelAdmin):
    model = SiteLanguage
    menu_label = 'Language'
    menu_icon = 'doc-full-inverse'
    list_display = ('title', 'is_main_language', 'is_active')
    search_fields = ('title',)
    list_per_page = 20
    add_to_settings_menu = True
    ordering = ('is_main_language',)
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


@hooks.register('construct_explorer_page_queryset')
def show_main_language_only(parent_page, pages, request):
    main_language = SiteLanguage.objects.filter(is_main_language=True).first()

    if main_language and not parent_page.depth == 1:
        translatable_pages = Page.objects.filter(
            Q(articlepage__isnull=False) |
            Q(sectionpage__isnull=False) |
            Q(homepage__isnull=False))
        main_pages = [
            p.id
            for p in translatable_pages
            if p.specific.language.id == main_language.id]
        return pages.filter(id__in=main_pages)

    return pages
