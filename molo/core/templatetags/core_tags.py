from django import template

from molo.core.models import SectionPage, LanguagePage, Page
from molo.core.utils import get_locale_code

register = template.Library()


@register.inclusion_tag(
    'core/tags/section_listing_homepage.html',
    takes_context=True
)
def section_listing_homepage(context):
    language_code = context.get('locale_code') or get_locale_code()
    language_page = LanguagePage.objects.live().filter(
        code=language_code).first()
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
