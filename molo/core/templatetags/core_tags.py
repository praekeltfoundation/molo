from itertools import chain
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache
from django import template
from django.utils.safestring import mark_safe
from django.db.models import Case, When
from markdown import markdown

from molo.core.models import (
    Page, ArticlePage, SectionPage, SiteSettings, Languages, Tag,
    ArticlePageTags, SectionIndexPage, ReactionQuestion,
    ReactionQuestionChoice, BannerPage)

register = template.Library()


def get_language(site, locale):
    language_cache_key = 'get_pages_language_{}_{}'.format(site.pk, locale)
    language = cache.get(language_cache_key)
    if not language:
        language = Languages.for_site(site).languages.filter(
            locale=locale).first()
        cache.set(language_cache_key, language, None)
    return language


def get_pages(context, queryset, locale):
    request = context['request']
    if not hasattr(request, 'site'):
        return list[queryset]

    language = get_language(request.site, locale)
    if language and language.is_main_language:
        return list(queryset.live())

    show_only_translated_pages = SiteSettings.for_site(
        request.site).show_only_translated_pages
    pages = []
    for page in queryset:
        translation = page.get_translation_for(locale, request.site)
        if translation and translation.live:
            pages.append(translation)
        elif page.live and not show_only_translated_pages:
            pages.append(page)
    return pages


@register.assignment_tag(takes_context=True)
def load_tags(context):
    request = context['request']
    locale = context.get('locale_code')

    if request.site:
        qs = Tag.objects.descendant_of(request.site.root_page).filter(
            languages__language__is_main_language=True).live()
    else:
        qs = []

    return get_pages(context, qs, locale)


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
    translation = page.get_translation_for(
        locale_code, context['request'].site)

    return translation or page


@register.assignment_tag(takes_context=True)
def get_parent(context, page):
    parent = page.get_parent()
    if not parent.specific_class == SectionIndexPage:
        return get_translation(context, parent.specific)
    return None


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
    'core/tags/tag_menu_homepage.html',
    takes_context=True
)
def tag_menu_homepage(context):
    locale_code = context.get('locale_code')

    return {
        'tags': load_tags(context),
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
        articles = request.site.root_page.specific \
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
        articles = request.site.root_page.specific \
            .topic_of_the_day()
    else:
        articles = ArticlePage.objects.none()

    return {
        'articles': get_pages(context, articles, locale),
        'request': context['request'],
        'locale_code': locale,
    }


@register.inclusion_tag('core/tags/bannerpages.html', takes_context=True)
def bannerpages(context, position=-1):
    request = context['request']
    locale = context.get('locale_code')

    if request.site:
        pages = request.site.root_page.specific.bannerpages().exact_type(
            BannerPage)
    else:
        pages = []
    if position >= 0:
        banners = get_pages(context, pages, locale)
        if position > (len(banners) - 1):
            return None
        banners = get_pages(context, pages, locale)
        if banners and len(banners) > position:
            return {
                'bannerpages': [banners[position]],
                'request': context['request'],
                'locale_code': locale,
            }
        return None
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
                p.get_translation_for(
                    locale_code, context['request'].site) or p)
        else:
            translated_ancestors.append(p)

    return {
        'ancestors': translated_ancestors,
        'request': context['request'],
    }


@register.inclusion_tag(
    'wagtail/translations_actions.html', takes_context=True)
def render_translations(context, page):
    if not hasattr(page.specific, 'get_translation_for'):
        return {}

    languages = [
        (l.locale, str(l))
        for l in Languages.for_site(context['request'].site).languages.filter(
            is_main_language=False)]
    return {
        'translations': [{
            'locale': {'title': title, 'code': code},
            'translated':
                page.specific.get_translation_for(
                    code, context['request'].site, is_live=None)
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
        qs = qs.filter(featured_in_homepage=featured_in_homepage).order_by(
            '-featured_in_homepage_start_date')

    if featured_in_latest is not None:
        qs = qs.filter(featured_in_latest=featured_in_latest)

    if featured_in_section is not None:
        qs = qs.filter(featured_in_section=featured_in_section).order_by(
            '-featured_in_section_start_date')

    if not locale:
        return qs.live()[:count]

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

    # TODO: Consider caching the pks of these articles using a timestamp on
    # section as the key so tha twe don't always do these joins
    child_articles = ArticlePage.objects.child_of(
        main_language_page).filter(languages__language__is_main_language=True)
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


def get_articles_for_tags_with_translations(
        request, tag, exclude_list, locale, context, exclude_pks):

    pks = [article_tag.page.pk for article_tag in
           ArticlePageTags.objects.filter(tag=tag)]
    return get_pages(
        context, ArticlePage.objects.descendant_of(
            request.site.root_page).filter(pk__in=pks).exclude(
                pk__in=exclude_pks), locale)


@register.assignment_tag(takes_context=True)
def get_articles_for_tag(context, tag):
    request = context['request']
    locale = context.get('locale_code')
    if tag:
        main_tag = tag.specific.get_main_language_page()
        pks = [article_tag.page.pk for article_tag in
               ArticlePageTags.objects.filter(tag=main_tag)]
        return get_pages(
            context, ArticlePage.objects.descendant_of(
                request.site.root_page).filter(pk__in=pks), locale)
    return None


@register.assignment_tag(takes_context=True)
def get_next_tag(context, tag):
    request = context['request']
    locale_code = context.get('locale_code')
    current_tag = tag.get_main_language_page()
    qs = Tag.objects.descendant_of(request.site.root_page).filter(
        languages__language__is_main_language=True).live()
    if qs.exists():
        tags = list(qs)
        if not (len(tags) == tags.index(current_tag) + 1):
            next_tag = tags[tags.index(current_tag) + 1]
        else:
            next_tag = tags[0]

        if next_tag.get_translation_for(
                locale_code, context['request'].site):
            return next_tag.get_translation_for(
                locale_code, context['request'].site)
        else:
            return next_tag


@register.assignment_tag(takes_context=True)
def get_tags_for_section(context, section, tag_count=2, tag_article_count=4):
    request = context['request']
    locale = context.get('locale_code')
    # Featured Tags
    exclude_pks = []
    tags_list = []
    main_language_page = section.get_main_language_page()
    child_articles = ArticlePage.objects.descendant_of(
        main_language_page).filter(languages__language__is_main_language=True)
    for article in child_articles:
        exclude_pks.append(article.pk)
    related_articles = ArticlePage.objects.filter(
        related_sections__section__slug=main_language_page.slug)
    for article in related_articles:
        exclude_pks.append(article.pk)

    tags = [
        section_tag.tag.pk for section_tag in
        section.get_main_language_page().specific.section_tags.all()
        if section_tag.tag]
    if tags and request.site:
        qs = Tag.objects.descendant_of(
            request.site.root_page).live().filter(pk__in=tags)
        for tag in qs:
            tag_articles = get_articles_for_tags_with_translations(
                request, tag, exclude_pks, locale, context,
                exclude_pks)
            if len(tag_articles) > tag_article_count:
                tag_articles = tag_articles[:tag_article_count]
            exclude_pks += [p.pk for p in tag_articles]
            tags = get_pages(context, qs.filter(pk=tag.pk), locale)
            if tags:
                tags_list.append((
                    tags[0],
                    tag_articles))
    else:
        return []

    return tags_list


@register.simple_tag(takes_context=True)
def get_tag_articles(
        context, section_count=1, tag_count=4, sec_articles_count=4,
        latest_article_count=3):
    # TODO: consider caching this tag - these queries are too expensive

    request = context['request']
    locale = context.get('locale_code')

    exclude_pks = []
    data = {}
    tags_list = []
    sections_list = []
    latest_articles = []
    # get x amount of articles featured in latest
    # ordered by featured in latest promote date
    all_latest_articles = ArticlePage.objects.descendant_of(
        request.site.root_page).filter(
        languages__language__is_main_language=True,
        featured_in_latest=True).exact_type(ArticlePage).exclude(
            pk__in=exclude_pks).order_by('-featured_in_latest_start_date')
    if all_latest_articles:
        all_translated_latest_articles = get_pages(
            context, all_latest_articles, locale)
        if all_translated_latest_articles:
            if len(all_translated_latest_articles) >= latest_article_count:
                latest_articles = all_translated_latest_articles[
                    :latest_article_count]
                exclude_pks += [p.pk for p in latest_articles]
            else:
                latest_articles = all_translated_latest_articles
                exclude_pks += [p.pk for p in latest_articles]
        elif len(all_latest_articles) >= latest_article_count:
            latest_articles = all_latest_articles[:latest_article_count]
            exclude_pks += [p.pk for p in latest_articles]
        else:
            latest_articles = all_latest_articles
            exclude_pks += [p.pk for p in latest_articles]

    # Featured Section/s
    sections = request.site.root_page.specific.sections()
    for section in sections[:section_count]:
        sec_articles = ArticlePage.objects.descendant_of(section).filter(
            languages__language__is_main_language=True,
            featured_in_homepage=True).order_by(
                '-featured_in_homepage_start_date').exclude(
                pk__in=exclude_pks)
        exclude_pks += [p.pk for p in sec_articles[:sec_articles_count]]
        section = SectionPage.objects.filter(pk=section.pk)
        section_for_locale = get_pages(context, section, locale)
        if section_for_locale:
            section = section_for_locale[0]
        sec_articles_for_locale = get_pages(context, sec_articles, locale)
        if sec_articles_for_locale and len(
                sec_articles_for_locale) > sec_articles_count:
            sec_articles_for_locale = sec_articles_for_locale[
                :sec_articles_count]
        if section_for_locale:
            sections_list.append((
                section,
                sec_articles_for_locale))
    data.update({'sections': sections_list})

    # Featured Tag/s
    tag_qs = Tag.objects.descendant_of(request.site.root_page).filter(
        feature_in_homepage=True).live()
    for tag in tag_qs:
        tag_articles = get_articles_for_tags_with_translations(
            request, tag, exclude_pks, locale,
            context, exclude_pks)
        if tag_articles and len(tag_articles) > tag_count:
            tag_articles = tag_articles[:tag_count]
        exclude_pks += [p.pk for p in tag_articles]
        tag_for_locale = get_pages(context, tag_qs.filter(pk=tag.pk), locale)
        if tag_for_locale:
            tags_list.append((
                tag_for_locale[0],
                tag_articles))
        else:
            tags_list.append((
                tag,
                tag_articles))
    data.update({'tags_list': tags_list})

    # Latest Articles
    data.update({
        'latest_articles': latest_articles + get_pages(
            context, ArticlePage.objects.descendant_of(
                request.site.root_page).filter(
                languages__language__is_main_language=True).exact_type(
                    ArticlePage).exclude(pk__in=exclude_pks).order_by(
                        '-featured_in_latest'), locale)})

    return data


@register.assignment_tag(takes_context=True)
def load_tags_for_article(context, article):
    if not article.specific.__class__ == ArticlePage:
        return None

    locale = context.get('locale_code')
    request = context['request']

    cache_key = "load_tags_for_article_{}_{}_{}_{}".format(
        locale, request.site.pk, article.pk,
        article.latest_revision_created_at.isoformat())
    tags_pks = cache.get(cache_key)

    if not tags_pks:
        tags = [
            article_tag.tag.pk for article_tag in
            article.specific.get_main_language_page().nav_tags.all()
            if article_tag.tag]
        if tags and request.site:
            qs = Tag.objects.descendant_of(
                request.site.root_page).live().filter(pk__in=tags)
            tags_pks = qs.values_list("pk", flat=True)
            cache.set(cache_key, tags_pks, 300)
        else:
            return []

    qs = Tag.objects.descendant_of(
        request.site.root_page).live().filter(pk__in=tags_pks)
    return get_pages(context, qs, locale)


@register.assignment_tag(takes_context=True)
def load_choices_for_reaction_question(context, question):
    locale = context.get('locale_code')
    if question:
        question_pk = question.get_main_language_page().pk
        question = ReactionQuestion.objects.filter(pk=question_pk)
    if question and question.first().get_children():
        pks = [c.pk for c in question.first().get_children().filter(
            languages__language__is_main_language=True)]
        choices = ReactionQuestionChoice.objects.filter(pk__in=pks)
        return get_pages(context, choices, locale)
    return []


@register.assignment_tag(takes_context=True)
def load_user_can_vote_on_reaction_question(context, question, article_pk):
    request = context['request']
    if question:
        question = question.get_main_language_page().specific
        article = ArticlePage.objects.get(pk=article_pk)
        if hasattr(article, 'get_main_language_page'):
            article = article.get_main_language_page()
        return not question.has_user_submitted_reaction_response(
            request, question.pk, article.pk)


@register.assignment_tag(takes_context=True)
def load_reaction_question(context, article):
    locale = context.get('locale_code')
    request = context['request']
    question = None
    if article:
        article_question = article.get_main_language_page() \
            .reaction_questions.all().first()
        if hasattr(article_question, 'reaction_question'):
            question = article_question.reaction_question

        if question and request.site:
            qs = ReactionQuestion.objects.descendant_of(
                request.site.root_page).live().filter(
                    pk=question.pk, languages__language__is_main_language=True)
        else:
            return []
        translated_question = get_pages(context, qs, locale)
        if translated_question:
            return get_pages(context, qs, locale)[0]
        return question


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


@register.inclusion_tag(
    'core/tags/social_media_footer.html',
    takes_context=True
)
def social_media_footer(context, page=None):
    request = context['request']
    locale = context.get('locale_code')
    social_media = SiteSettings.for_site(request.site).\
        social_media_links_on_footer_page

    data = {
        'social_media': social_media,
        'request': context['request'],
        'locale_code': locale,
        'page': page,
    }
    return data


@register.inclusion_tag(
    'core/tags/social_media_article.html',
    takes_context=True
)
def social_media_article(context, page=None):
    request = context['request']
    locale = context.get('locale_code')
    site_settings = SiteSettings.for_site(request.site)

    if site_settings.facebook_sharing:
        facebook = site_settings.facebook_image
    else:
        facebook = False

    if site_settings.twitter_sharing:
        twitter = site_settings.twitter_image
    else:
        twitter = False

    data = {
        'facebook': facebook,
        'twitter': twitter,
        'request': context['request'],
        'locale_code': locale,
        'page': page,
    }
    return data


@register.assignment_tag(takes_context=True)
def get_next_article(context, article):
    locale_code = context.get('locale_code')
    section = article.get_parent_section()
    articles = load_child_articles_for_section(context, section, count=None)
    if len(articles) > 1:
        next_article = articles[articles.index(article) - 1]
    else:
        return None

    if next_article.get_translation_for(locale_code, context['request'].site):
        return next_article.get_translation_for(
            locale_code, context['request'].site)
    else:
        return next_article


@register.assignment_tag(takes_context=True)
def get_recommended_articles(context, article):
    locale_code = context.get('locale_code')

    if article.recommended_articles.all():
        recommended_articles = article.recommended_articles.all()
    else:
        a = article.get_main_language_page()
        recommended_articles = a.specific.recommended_articles.all()

    # http://stackoverflow.com/questions/4916851/django-get-a-queryset-from-array-of-ids-in-specific-order/37648265#37648265 # noqa
    # the following allows us to order the results of the querystring
    pk_list = recommended_articles.values_list(
        'recommended_article__pk', flat=True)

    if not pk_list:
        return []

    preserved = Case(
        *[When(pk=pk, then=pos) for pos, pk in enumerate(pk_list)])
    articles = ArticlePage.objects.filter(pk__in=pk_list).order_by(preserved)

    return get_pages(context, articles, locale_code)


@register.simple_tag(takes_context=True)
def should_hide_delete_button(context, page):
    return hasattr(page.specific, 'hide_delete_button')
