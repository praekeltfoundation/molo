from itertools import chain

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django import template
from django.utils.safestring import mark_safe
from markdown import markdown

from molo.core.models import (Page, SiteLanguage, ArticlePage, SectionPage,
                              SiteSettings)

register = template.Library()


def get_pages(context, qs, locale):
    language = SiteLanguage.objects.filter(locale=locale).first()
    request = context['request']
    site_settings = SiteSettings.for_site(request.site)
    if site_settings.show_only_translated_pages:
        if language and language.is_main_language:
            return [a for a in qs.live()]
        else:
            pages = []
            for a in qs:
                translation = a.get_translation_for(locale)
                if translation:
                    pages.append(translation)
            return pages
    else:
        if language and language.is_main_language:
            return [a for a in qs.live()]
        else:
            pages = []
            for a in qs:
                translation = a.get_translation_for(locale)
                if translation:
                    pages.append(translation)
                elif a.live:
                    pages.append(a)
            return pages


@register.assignment_tag(takes_context=True)
def load_sections(context):
    request = context['request']
    locale = context.get('locale_code')

    if request.site:
        qs = request.site.root_page.specific.sections()
    else:
        qs = []

    return get_pages(context, qs, locale)


@register.assignment_tag(takes_context=True)
def get_translation(context, page):
    locale_code = context.get('locale_code')
    if page.get_translation_for(locale_code):
        return page.get_translation_for(locale_code)
    else:
        return page


@register.inclusion_tag(
    'core/tags/section_listing_homepage.html',
    takes_context=True
)
def section_listing_homepage(context):
    locale_code = context.get('locale_code')

    return {
        'sections': load_sections(context),
        'request': context['request'],
        'locale_code': locale_code,
    }


@register.inclusion_tag(
    'core/tags/latest_listing_homepage.html',
    takes_context=True
)
def latest_listing_homepage(context, num_count=5):
    request = context['request']
    locale = context.get('locale_code')

    if request.site:
        articles = request.site.root_page.specific\
            .latest_articles()
    else:
        articles = []

    return {
        'articles': get_pages(context, articles, locale)[:num_count],
        'request': context['request'],
        'locale_code': locale,
    }


@register.inclusion_tag(
    'core/tags/topic_of_the_day.html',
    takes_context=True
)
def topic_of_the_day(context):
    request = context['request']
    locale = context.get('locale_code')

    if request.site:
        articles = request.site.root_page.specific\
            .topic_of_the_day()
    else:
        articles = ArticlePage.objects.None()

    return {
        'articles': get_pages(context, articles, locale),
        'request': context['request'],
        'locale_code': locale,
    }


@register.inclusion_tag('core/tags/bannerpages.html', takes_context=True)
def bannerpages(context):
    request = context['request']
    locale = context.get('locale_code')

    if request.site:
        pages = request.site.root_page.specific.bannerpages()
    else:
        pages = []

    return {
        'bannerpages': get_pages(context, pages, locale),
        'request': context['request'],
        'locale_code': locale,
    }


@register.inclusion_tag('core/tags/footerpage.html', takes_context=True)
def footer_page(context):
    request = context['request']
    locale = context.get('locale_code')

    if request.site:
        pages = request.site.root_page.specific.footers()
    else:
        pages = []

    return {
        'footers': get_pages(context, pages, locale),
        'request': context['request'],
        'locale_code': locale,
    }


@register.inclusion_tag('core/tags/breadcrumbs.html', takes_context=True)
def breadcrumbs(context):
    self = context.get('self')
    locale_code = context.get('locale_code')

    if self is None or self.depth <= 2:
        # When on the home page, displaying breadcrumbs is irrelevant.
        ancestors = ()
    else:
        ancestors = Page.objects.live().ancestor_of(
            self, inclusive=True).filter(depth__gt=3).specific()

    translated_ancestors = []
    for p in ancestors:
        if hasattr(p, 'get_translation_for'):
            translated_ancestors.append(
                p.get_translation_for(locale_code) or p)
        else:
            translated_ancestors.append(p)

    return {
        'ancestors': translated_ancestors,
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
            'translated':
                page.specific.get_translation_for(code, is_live=None)
            if hasattr(page.specific, 'get_translation_for') else None}
            for code, title in languages],
        'page': page
    }


@register.assignment_tag(takes_context=True)
def load_descendant_articles_for_section(
        context, section, featured_in_homepage=None, featured_in_section=None,
        featured_in_latest=None, count=5):
    '''
    Returns all descendant articles (filtered using the parameters)
    If the `locale_code` in the context is not the main language, it will
    return the translations of the live articles.
    '''
    page = section.get_main_language_page()
    locale = context.get('locale_code')

    qs = ArticlePage.objects.descendant_of(page).filter(
        languages__language__is_main_language=True)

    if featured_in_homepage is not None:
        qs = qs.filter(featured_in_homepage=featured_in_homepage)

    if featured_in_latest is not None:
        qs = qs.filter(featured_in_latest=featured_in_latest)

    if featured_in_section is not None:
        qs = qs.filter(featured_in_section=featured_in_section)

    if not locale:
        return qs[:count]

    return get_pages(context, qs, locale)[:count]


@register.assignment_tag(takes_context=True)
def load_child_articles_for_section(context, section, count=5):
    '''
    Returns all child articles
    If the `locale_code` in the context is not the main language, it will
    return the translations of the live articles.
    '''
    locale = context.get('locale_code')
    main_language_page = section.get_main_language_page()
    child_articles = ArticlePage.objects.child_of(main_language_page).filter(
        languages__language__is_main_language=True)
    related_articles = ArticlePage.objects.filter(
        related_sections__section__slug=main_language_page.slug)
    qs = list(chain(
        get_pages(context, child_articles, locale),
        get_pages(context, related_articles, locale)))

    # Pagination
    if count:
        p = context.get('p', 1)
        paginator = Paginator(qs, count)

        try:
            articles = paginator.page(p)
        except PageNotAnInteger:
            articles = paginator.page(1)
        except EmptyPage:
            articles = paginator.page(paginator.num_pages)
    else:
        articles = qs
    if not locale:
        return articles

    context.update({'articles_paginated': articles})
    return articles


@register.assignment_tag(takes_context=True)
def load_child_sections_for_section(context, section, count=None):
    '''
    Returns all child articles
    If the `locale_code` in the context is not the main language, it will
    return the translations of the live articles.
    '''
    page = section.get_main_language_page()
    locale = context.get('locale_code')

    qs = SectionPage.objects.child_of(page).filter(
        languages__language__is_main_language=True)

    if not locale:
        return qs[:count]

    return get_pages(context, qs, locale)


@register.filter
def handle_markdown(value):
    md = markdown(
        value,
        [
            'markdown.extensions.fenced_code',
            'codehilite',
        ]
    )
    """ For some unknown reason markdown wraps the value in <p> tags.
        Currently there doesn't seem to be an extension to turn this off.
    """
    open_tag = '<p>'
    close_tag = '</p>'
    if md.startswith(open_tag) and md.endswith(close_tag):
        md = md[len(open_tag):-len(close_tag)]
    return mark_safe(md)
