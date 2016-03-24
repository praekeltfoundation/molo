from django import template

from molo.core.models import Page, SiteLanguage

register = template.Library()


@register.inclusion_tag(
    'core/tags/section_listing_homepage.html',
    takes_context=True
)
def section_listing_homepage(context):
    request = context['request']
    locale = context['locale_code']

    if request.site:
        sections = request.site.root_page.specific.sections()
    else:
        sections = []

    return {
        'sections': [a.get_translation_for(locale) or a for a in sections],
        'request': context['request'],
    }


@register.inclusion_tag(
    'core/tags/latest_listing_homepage.html',
    takes_context=True
)
def latest_listing_homepage(context, num_count=5):
    request = context['request']
    locale = context['locale_code']

    if request.site:
        articles = request.site.root_page.specific\
            .latest_articles()[:num_count]
    else:
        articles = []

    return {
        'articles': [a.get_translation_for(locale) or a for a in articles],
        'request': context['request'],
    }


@register.inclusion_tag('core/tags/bannerpages.html', takes_context=True)
def bannerpages(context):
    request = context['request']
    locale = context['locale_code']

    if request.site:
        pages = request.site.root_page.specific.bannerpages()
    else:
        pages = []

    return {
        'bannerpages': [a.get_translation_for(locale) or a for a in pages],
        'request': context['request']
    }


@register.inclusion_tag('core/tags/footerpage.html', takes_context=True)
def footer_page(context):
    request = context['request']
    locale = context['locale_code']

    if request.site:
        pages = request.site.root_page.specific.footers()
    else:
        pages = []

    return {
        'footers': [a.get_translation_for(locale) or a for a in pages],
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


@register.inclusion_tag(
    'core/admin/translations_actions.html', takes_context=True)
def render_translations(context, page):
    if not hasattr(page.specific, 'get_translation_for'):
        return {}

    languages = [
        (l.locale, str(l))
        for l in SiteLanguage.objects.filter(is_main_language=False)]

    return {
        'translations': [{
            'locale': {'title': title, 'code': code},
            'translated': page.specific.get_translation_for(code)
            if hasattr(page.specific, 'get_translation_for') else None}
            for code, title in languages],
        'page': page
    }


@register.filter
def translation(page, locale):
    if not hasattr(page.specific, 'get_translation_for'):
        return page
    return page.get_translation_for(locale) or page
