from django import template
from django.utils.translation import get_language_from_request

from molo.core.models import SectionPage, LanguagePage

register = template.Library()


@register.inclusion_tag(
    'core/tags/section_listing_homepage.html',
    takes_context=True
)
def section_listing_homepage(context):
    language = get_language_from_request(context['request'])
    language_page = LanguagePage.objects.live().filter(code=language).first()
    if language_page:
        sections = SectionPage.objects.live().descendant_of(language_page)
    else:
        sections = SectionPage.objects.none()
    return {
        'sections': sections,
        'request': context['request'],
    }
