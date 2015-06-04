from django import template
from django.utils.translation import get_language_from_request, to_locale

from molo.core.models import SectionPage, LanguagePage, Page

register = template.Library()


@register.inclusion_tag(
    'core/tags/section_listing_homepage.html',
    takes_context=True
)
def section_listing_homepage(context):
    locale = get_language_from_request(context['request'])
    lang_code, _, country_code = to_locale(locale).partition('_')
    language_page = LanguagePage.objects.live().filter(code=lang_code).first()
    if language_page:
        sections = SectionPage.objects.live().descendant_of(language_page)
    else:
        sections = SectionPage.objects.none()
    return {
        'sections': sections,
        'request': context['request'],
    }


@register.inclusion_tag('core/tags/breadcrumbs.html', takes_context=True)
def breadcrumbs(context):
    self = context.get('self')
    if self is None or self.depth <= 3:
        # When on the home page, displaying breadcrumbs is irrelevant.
        ancestors = ()
    else:
        ancestors = Page.objects.ancestor_of(
            self, inclusive=True).filter(depth__gt=3)
    return {
        'ancestors': ancestors,
        'request': context['request'],
    }
