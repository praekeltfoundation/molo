from django import template

from molo.core.models import (
    SectionPage, Page, HomePage, FooterPage)

register = template.Library()


@register.inclusion_tag(
    'core/tags/section_listing_homepage.html',
    takes_context=True
)
def section_listing_homepage(context):
    selected_language = context.get('selected_language')
    request = context['request']
    if selected_language:
        sections = request.site.root_page.specific.sections(selected_language)
    else:
        sections = SectionPage.objects.none()
    return {
        'sections': sections,
        'request': context['request'],
    }


@register.inclusion_tag(
    'core/tags/latest_listing_homepage.html',
    takes_context=True
)
def latest_listing_homepage(context, num_count=5):
    selected_language = context.get('selected_language')
    request = context['request']
    if selected_language:
        articles = request.site.root_page.specific.latest_articles(
            selected_language)[:num_count]
    else:
        articles = Page.objects.none()
    return {
        'articles': articles,
        'request': context['request'],
    }


@register.inclusion_tag('core/tags/homepages.html', takes_context=True)
def homepages(context):
    selected_language = context.get('selected_language')
    request = context['request']
    if selected_language:
        homepages = request.site.root_page.specific.homepages(
            selected_language)
    else:
        homepages = HomePage.objects.none()
    return {
        'homepages': homepages,
        'request': context['request']
    }


@register.inclusion_tag(
    'core/tags/footerpage.html',
    takes_context=True
)
def footer_page(context):
    selected_language = context.get('selected_language')
    request = context['request']
    if selected_language:
        footers = request.site.root_page.specific.footers(
            selected_language)
    else:
        footers = FooterPage.objects.none()
    return {
        'footers': footers,
        'request': context['request'],
    }


@register.inclusion_tag('core/tags/breadcrumbs.html', takes_context=True)
def breadcrumbs(context):
    self = context.get('self')
    if self is None or self.depth <= 2:
        # When on the home page, displaying breadcrumbs is irrelevant.
        ancestors = ()
    else:
        ancestors = Page.objects.ancestor_of(
            self, inclusive=True).filter(depth__gt=2)
    return {
        'ancestors': ancestors,
        'request': context['request'],
    }
