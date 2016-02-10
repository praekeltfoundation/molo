from django import template

from molo.core.models import SectionPage, Page, HomePage, SiteLanguage

register = template.Library()


@register.inclusion_tag(
    'core/tags/section_listing_homepage.html',
    takes_context=True
)
def section_listing_homepage(context):
    language_page = context.get('language_page')
    if language_page:
        sections = language_page.sections()
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
    language_page = context.get('language_page')
    if language_page:
        articles = language_page.latest_articles()[:num_count]
    else:
        articles = Page.objects.none()
    return {
        'articles': articles,
        'request': context['request'],
    }


@register.inclusion_tag('core/tags/homepages.html', takes_context=True)
def homepages(context):
    language_page = context.get('language_page')
    if language_page:
        homepages = language_page.homepages()
    else:
        homepages = HomePage.objects.none()
    return {
        'homepages': homepages,
        'request': context['request']
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


@register.inclusion_tag(
    'core/admin/translations_actions.html', takes_context=True)
def render_translations(context, page):
    def get_translated_page(qs, locale):
        translated = None
        for t in qs:
            if (hasattr(t.translated_page.specific, 'language') and
                    t.translated_page.specific.language and
                    t.translated_page.specific.language.code == locale):
                translated = t.translated_page.specific
                break
        return translated

    if not hasattr(page.specific, 'translations'):
        return {}
    languages = [
        (l.code, l.title)
        for l in SiteLanguage.objects.filter(is_main_language=False)]
    translations_qs = page.specific.translations.all()

    return {
        'translations': [{
            'locale': {'title': lt, 'code': l},
            'translated': get_translated_page(translations_qs, l)}
            for l, lt in languages],
        'page': page
    }
