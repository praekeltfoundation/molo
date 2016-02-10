from django.conf.urls import url

from wagtailmodeladmin.options import(
    ModelAdmin, wagtailmodeladmin_register)
from wagtail.wagtailcore import hooks

from molo.core.models import SiteLanguage


class LanguageModelAdmin(ModelAdmin):
    model = SiteLanguage
    menu_label = 'Language'
    menu_icon = 'doc-full-inverse'
    list_display = ('title', 'is_main_language',)
    search_fields = ('title',)
    list_per_page = 100
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
