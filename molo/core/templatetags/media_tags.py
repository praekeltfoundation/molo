from django import template

from molo.core.models import MoloMedia


register = template.Library()


@register.inclusion_tag(
    'core/tags/media_listing_homepage.html',
    takes_context=True
)
def media_listing_homepage(context):
    return {
        'media': MoloMedia.objects.filter(feature_in_homepage=True),
        'request': context['request'],
    }
