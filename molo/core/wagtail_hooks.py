from wagtailmodeladmin.options import(
    ModelAdmin, wagtailmodeladmin_register)

from molo.core.models import LanguagePage


class LanguageModelAdmin(ModelAdmin):
    model = LanguagePage
    menu_label = 'Language'
    menu_icon = 'doc-full-inverse'
    list_display = ('title', 'type', 'live',)
    list_filter = ('live',)
    search_fields = ('title',)
    list_per_page = 100
    add_to_settings_menu = True
    menu_order = 100

wagtailmodeladmin_register(LanguageModelAdmin)
