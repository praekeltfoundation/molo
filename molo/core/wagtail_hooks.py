from django.conf.urls import url
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from wagtailmodeladmin.options import(
    ModelAdmin, wagtailmodeladmin_register)
from wagtail.wagtailcore import hooks
from wagtail.wagtailadmin.widgets import PageListingButton
from wagtail.wagtailadmin.widgets import ButtonWithDropdownFromHook

from molo.core.models import SiteLanguage


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


@hooks.register('construct_explorer_page_queryset')
def show_main_language_only(parent_page, pages, request):
    main_language = SiteLanguage.objects.filter(is_main_language=True).first()

    if main_language and not parent_page.depth == 1:
        return pages.filter(languages__language__id=main_language.id)

    return pages


@hooks.register('register_page_listing_buttons')
def page_listing_buttons(page, page_perms, is_parent=False):
    if not hasattr(page.specific, 'get_translation_for'):
        return

    translations_group = ButtonWithDropdownFromHook(
        _('Translations'),
        hook_name='register_page_listing_translation_buttons',
        page=page,
        page_perms=page_perms,
        is_parent=is_parent,
        attrs={'target': '_blank'}, priority=60)
    translations_group.template_name = 'core/translation_buttons.html'
    yield translations_group


@hooks.register('register_page_listing_translation_buttons')
def page_listing_translation_buttons(page, page_perms, is_parent=False):
    if not hasattr(page.specific, 'get_translation_for'):
        return

    for language in SiteLanguage.objects.filter(is_main_language=False):
        translation = page.specific.get_translation_for(language.locale)
        if translation:
            url = reverse('wagtailadmin_pages:edit', args=[translation.id])
            classes = (
                "button button-small button-secondary translation-translated")
            if not translation.live or translation.has_unpublished_changes:
                classes += " translation-translated-draft"
        else:
            url = reverse(
                'add_translation', args=[page.id, language.locale])
            classes = "button button-small button-secondary"
        yield PageListingButton(
            str(language), url,
            attrs={'title': str(language), 'class': classes})
