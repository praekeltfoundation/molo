from itertools import chain
from markdown import markdown

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache
from django import template
from django.utils.safestring import mark_safe
from django.db.models import Case, When

from prometheus_client import Summary

from molo.core.decorators import prometheus_query_count
from molo.core.models import (
    Page, ArticlePage, SectionPage, SiteSettings, Languages, Tag,
    ArticlePageTags, SectionIndexPage, ReactionQuestion,
    ReactionQuestionChoice, BannerPage, get_translation_for,
    ArticleOrderingChoices, ReactionQuestionResponse
)


register = template.Library()


REQUEST_TIME = Summary(
        'request_processing_seconds', 'Time spent processing request')


def get_language(site, locale):
    language_cache_key = 'get_pages_language_{}_{}'.format(site.pk, locale)
    language = cache.get(language_cache_key)
    if not language:
        language = Languages.for_site(site).languages.filter(
            locale=locale).first()
        cache.set(language_cache_key, language, None)
    return language


def get_pages(context, queryset, locale):
    from molo.core.models import get_translation_for

    if queryset.count() == 0:
        return []

    request = context['request']
    if not hasattr(request, 'site'):
        return list[queryset]

    language = get_language(request.site, locale)
    if language and language.is_main_language:
        return list(queryset.live())
    pages = get_translation_for(queryset, locale, request.site)
    return pages or []


@register.simple_tag(takes_context=True)
def load_tags(context):
    request = context['request']
    locale = context.get('locale_code')

    if request.site:
        qs = Tag.objects.descendant_of(request.site.root_page).filter(
            language__is_main_language=True).live()
    else:
        return[]

    return get_pages(context, qs, locale)


@register.simple_tag(takes_context=True)
def load_sections(context):
    request = context['request']
    locale = context.get('locale_code')
    if request.site:
        qs = request.site.root_page.specific.sections()
    else:
        return []
    return get_pages(context, qs, locale)


@register.simple_tag(takes_context=True)
def get_translation(context, page):
    locale_code = context.get('locale_code')
    try:
        translation = page.translated_pages.get(language__locale=locale_code)
    except:
        return page

    return translation


@register.simple_tag(takes_context=True)
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
        articles = request.site.root_page.specific.latest_articles()
    else:
        articles = []
    return {
        'articles': get_pages(context, articles, locale)[:num_count],
        'request': context['request'],
        'locale_code': locale,
    }


@register.inclusion_tag(
    'core/tags/hero_article.html',
    takes_context=True
)
def hero_article(context):
    request = context['request']
    locale = context.get('locale_code')

    if request.site:
        articles = request.site.root_page.specific \
            .hero_article()
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
                'is_via_freebasics':
                    'Internet.org' in request.META.get('HTTP_VIA', '') or
                    'InternetOrgApp' in request.META.get(
                        'HTTP_USER_AGENT', '') or
                    'true' in request.META.get('HTTP_X_IORG_FBS', '')
            }
        return None
    return {
        'bannerpages': get_pages(context, pages, locale),
        'request': context['request'],
        'locale_code': locale,
        'is_via_freebasics':
            'Internet.org' in request.META.get('HTTP_VIA', '') or
            'InternetOrgApp' in request.META.get('HTTP_USER_AGENT', '') or
            'true' in request.META.get('HTTP_X_IORG_FBS', '')
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
    ancestors = []
    translated_ancestors = []
    if self is not None and not self.depth <= 2:
        ancestors = Page.objects.live().ancestor_of(
            self, inclusive=True).filter(depth__gt=3)
        if ancestors:
            translated_ancestors = get_pages(context, ancestors, locale_code)

    return {
        'ancestors': translated_ancestors,
        'request': context['request'],
    }


@register.inclusion_tag(
    'wagtail/translations_actions.html', takes_context=True)
def render_translations(context, page):
    from molo.core.models import TranslatablePageMixinNotRoutable
    if not issubclass(type(page.specific), TranslatablePageMixinNotRoutable):
        return {}
    if not page.specific.language.is_main_language:
        return {}

    languages = [
        (l.locale, str(l))
        for l in Languages.for_site(
            context['request'].site.root_page.get_site()).languages.filter(
                is_main_language=False)]

    translated = []
    for code, title in languages:
        if page.specific.translated_pages.filter(
                language__locale=code).exists():
            translated.append({
                'locale': {'title': title, 'code': code},
                'translated':
                    page.specific.translated_pages.filter(
                        language__locale=code).first()})
        else:
            translated.append({
                'locale': {'title': title, 'code': code},
                'translated': []})
    return {
        'translations': translated,
        'page': page
    }


@register.simple_tag(takes_context=True)
def load_descendant_articles_for_section(
        context, section, featured_in_homepage=None, featured_in_section=None,
        featured_in_latest=None, count=5):
    """
    Returns all descendant articles (filtered using the parameters)
    If the `locale_code` in the context is not the main language, it will
    return the translations of the live articles.
    """
    request = context.get('request')
    locale = context.get('locale_code')
    page = section.get_main_language_page()
    settings = SiteSettings.for_site(request.site) \
        if request else None

    qs = ArticlePage.objects.descendant_of(page).filter(
        language__is_main_language=True)

    article_ordering = settings \
        and settings.article_ordering_within_section

    if article_ordering:
        order_by = ArticleOrderingChoices.\
            get(settings.article_ordering_within_section).name.lower()

        order_by = order_by if order_by.find('_desc') == -1 \
            else '-{}'.format(order_by.replace('_desc', ''))

        # if the sort order is equal to CMS_DEFAULT_SORTING
        #  do not order QS, CMS handles it
        if article_ordering and settings.article_ordering_within_section\
                != ArticleOrderingChoices.CMS_DEFAULT_SORTING:
            qs = qs.order_by(order_by)

    if featured_in_homepage is not None:
        qs = qs.filter(featured_in_homepage=featured_in_homepage)\
            .order_by('-featured_in_homepage_start_date')

    if featured_in_latest is not None:
        qs = qs.filter(featured_in_latest=featured_in_latest)

    if featured_in_section is not None:
        qs = qs.filter(featured_in_section=featured_in_section)\
            .order_by('-featured_in_section_start_date')

    if not locale:
        return qs.live()[:count]

    return get_pages(context, qs, locale)[:count]


@register.simple_tag(takes_context=True)
def load_child_articles_for_section(
        context, section, featured_in_section=None, count=5):
    """
    Returns all child articles
    If the `locale_code` in the context is not the main language, it will
    return the translations of the live articles.
    """
    if not section:
        return None
    request = context.get('request')
    locale = context.get('locale_code')
    main_language_page = section.specific.get_main_language_page()
    settings = SiteSettings.for_site(request.site) \
        if request else None

    # TODO: Consider caching the pks of these articles using a timestamp on
    # section as the key so tha twe don't always do these joins
    article_ordering = settings and settings.article_ordering_within_section
    order_by = ArticleOrderingChoices.\
        get(settings.article_ordering_within_section).name.lower() \
        if article_ordering else '-first_published_at'

    order_by = order_by if order_by.find('_desc') == -1 \
        else '-{}'.format(order_by.replace('_desc', ''))

    child_articles = ArticlePage.objects.child_of(
        main_language_page).filter(
        language__is_main_language=True)

    # if the sort order is equal to CMS_DEFAULT_SORTING
    #  do not order QS, CMS handles it
    if getattr(settings, 'article_ordering_within_section')\
            != ArticleOrderingChoices.CMS_DEFAULT_SORTING:
        child_articles = child_articles.order_by(order_by)

    if featured_in_section is not None:
        child_articles = child_articles.filter(
            featured_in_section=featured_in_section)\
            .order_by('-featured_in_section_start_date')

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
    pages = get_pages(
        context, ArticlePage.objects.descendant_of(
            request.site.root_page).filter(pk__in=pks), locale)
    return [x for x in pages if x.pk not in exclude_pks]


@register.simple_tag(takes_context=True)
@prometheus_query_count
def get_articles_for_tag(context, tag):
    request = context['request']
    locale = context.get('locale_code')
    if tag:
        main_tag = tag.specific.get_main_language_page()
        pks = [article_tag.page.pk for article_tag in
               ArticlePageTags.objects.filter(tag=main_tag)]
        return get_pages(
            context, ArticlePage.objects.descendant_of(
                request.site.root_page).filter(
                pk__in=pks).order_by(
                '-first_published_at'), locale)
    return None


@register.simple_tag(takes_context=True)
@prometheus_query_count
def get_next_tag(context, tag):
    request = context['request']
    locale_code = context.get('locale_code')
    current_tag = tag.get_main_language_page()
    qs = Tag.objects.descendant_of(request.site.root_page).filter(
        language__is_main_language=True).live()
    if qs.exists():
        tags = list(qs)
        if not (len(tags) == tags.index(current_tag) + 1):
            next_tag = tags[tags.index(current_tag) + 1]
        else:
            next_tag = tags[0]

        next_tag_translated = get_translation_for(
                [next_tag], locale_code, context['request'].site)
        if next_tag_translated:
            return next_tag_translated[0]
        else:
            return next_tag


@register.simple_tag(takes_context=True)
@prometheus_query_count
def get_tags_for_section(context, section, tag_count=2, tag_article_count=4):
    request = context['request']
    locale = context.get('locale_code')
    # Featured Tags
    exclude_pks = []
    tags_list = []
    main_language_page = section.get_main_language_page()
    child_articles = ArticlePage.objects.descendant_of(
        main_language_page).filter(language__is_main_language=True)
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
@REQUEST_TIME.time()
@prometheus_query_count
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
        language__is_main_language=True,
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

    # Featured Section/s
    sections = request.site.root_page.specific.sections()
    for section in sections[:section_count]:
        article_pages = ArticlePage.objects.descendant_of(section).filter(
            language__is_main_language=True,
            featured_in_homepage=True).order_by(
            '-featured_in_homepage_start_date')

        sec_articles = get_pages(context, article_pages, locale)

        sec_translated_articles = [
            x for x in sec_articles if x.pk not in exclude_pks]

        exclude_pks += [
            p.pk for p in sec_translated_articles[:sec_articles_count]]

        section = SectionPage.objects.filter(pk=section.pk)
        section_for_locale = get_pages(context, section, locale)

        if section_for_locale:
            section = section_for_locale[0]

        if sec_translated_articles and len(
                sec_translated_articles) > sec_articles_count:
            sec_translated_articles = sec_translated_articles[
                                      :sec_articles_count]

        if section_for_locale:
            sections_list.append((section, sec_translated_articles))

    # Featured Tag/s
    tag_qs = Tag.objects.descendant_of(request.site.root_page).filter(
        feature_in_homepage=True).live()
    if tag_qs:
        tag = tag_qs.first()
        tag_articles = get_articles_for_tags_with_translations(
            request, tag, None, locale, context, exclude_pks)

        if tag_articles and len(tag_articles) > tag_count:
            tag_articles = tag_articles[:tag_count]

        exclude_pks += [p.pk for p in tag_articles]
        tag_for_locale = get_pages(context, tag_qs.filter(pk=tag.pk), locale)

        if tag_for_locale:
            tags_list.append((tag_for_locale[0], tag_articles))
        else:
            tags_list.append((tag, tag_articles))

    # Latest Articles
    pages = get_pages(
            context, ArticlePage.objects.descendant_of(
                request.site.root_page).filter(
                language__is_main_language=True).exact_type(
                    ArticlePage).order_by('-featured_in_latest'), locale)
    articles = [x for x in pages if x.pk not in exclude_pks]

    data.update({
        'tags_list': tags_list,
        'sections': sections_list,
        'latest_articles': latest_articles + articles})
    return data


@register.simple_tag(takes_context=True)
@prometheus_query_count
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


@register.simple_tag(takes_context=True)
@prometheus_query_count
def load_choices_for_reaction_question(context, question):
    locale = context.get('locale_code')
    if question:
        question = question.specific.get_main_language_page().specific
    if question and question.get_children():
        choices = ReactionQuestionChoice.objects.child_of(
            question).filter(language__is_main_language=True)
        return get_pages(context, choices, locale)
    return []


@register.simple_tag()
def load_reaction_choice_submission_count(choice, article, question):
    if choice and article:
        choice = choice.specific.get_main_language_page().specific
        return ReactionQuestionResponse.objects.filter(
            article=article, choice=choice, question=question).count()


@register.simple_tag(takes_context=True)
@prometheus_query_count
def load_user_can_vote_on_reaction_question(context, question, article_pk):
    request = context['request']
    if question:
        question = question.specific.get_main_language_page()
        article = ArticlePage.objects.get(pk=article_pk)
        if hasattr(article, 'get_main_language_page'):
            article = article.get_main_language_page()
        return not question.has_user_submitted_reaction_response(
            request, question.pk, article.pk)


@register.simple_tag(takes_context=True)
@prometheus_query_count
def load_user_choice_reaction_question(context, question, article, choice):
    request = context['request']
    if question and request.user.is_authenticated:
        question = question.specific.get_main_language_page()
        article = ArticlePage.objects.get(pk=article)
        if hasattr(article, 'get_main_language_page'):
            article = article.get_main_language_page()
        return ReactionQuestionResponse.objects.filter(
            article=article, choice=choice,
            question=question, user=request.user).exists()


@register.simple_tag(takes_context=True)
@prometheus_query_count
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
                    pk=question.pk, language__is_main_language=True)
        else:
            return []
        translated_question = get_pages(context, qs, locale)
        if translated_question:
            return get_pages(context, qs, locale)[0]
        return question


@register.simple_tag(takes_context=True)
@prometheus_query_count
def load_child_sections_for_section(context, section, count=None):
    """
    Returns all child sections
    If the `locale_code` in the context is not the main language, it will
    return the translations of the live articles.
    """
    if not section:
        return None

    locale = context.get('locale_code')
    page = section.get_main_language_page() \
        if hasattr(section, 'get_main_language_page') else section

    qs = SectionPage.objects.child_of(page).filter(
        language__is_main_language=True)

    if not locale:
        return qs[:count]
    return get_pages(context, qs, locale)


@register.simple_tag(takes_context=True)
@prometheus_query_count
def load_sibling_sections(context, section, count=None):
    """
    Returns all sibling sections
    If the `locale_code` in the context is not the main language, it will
    return the translations of the live articles.
    """
    page = section.get_main_language_page()
    locale = context.get('locale_code')

    qs = SectionPage.objects.sibling_of(page).filter(
        language__is_main_language=True)

    if not locale:
        return qs[:count]
    return get_pages(context, qs, locale)


@register.filter
def handle_markdown(value):
    md = markdown(
        value,
        extensions=[
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
@prometheus_query_count
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
@prometheus_query_count
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

    if site_settings.whatsapp_sharing:
        whatsapp = site_settings.whatsapp_image
    else:
        whatsapp = False

    if site_settings.viber_sharing:
        viber = site_settings.viber_image
    else:
        viber = False

    if site_settings.telegram_sharing:
        telegram = site_settings.telegram_image
    else:
        telegram = False

    data = {
        'facebook': facebook,
        'twitter': twitter,
        'whatsapp': whatsapp,
        'viber': viber,
        'telegram': telegram,
        'request': context['request'],
        'locale_code': locale,
        'page': page,
    }
    return data


@register.simple_tag(takes_context=True)
@prometheus_query_count
def get_next_article(context, article):
    locale_code = context.get('locale_code')
    section = article.get_parent_section()
    articles = load_child_articles_for_section(context, section, count=None)
    if len(articles) > 1:
        if len(articles) > articles.index(article) + 1:
            next_article = articles[articles.index(article) + 1]
        else:
            next_article = articles[0]
    else:
        return None
    try:
        return next_article.translated_pages.get(language__locale=locale_code)
    except:
        if next_article.language.locale == locale_code or not \
                SiteSettings.for_site(
                    context['request'].site).show_only_translated_pages:
            return next_article
        return None


@register.simple_tag(takes_context=True)
@prometheus_query_count
def get_recommended_articles(context, article):
    locale_code = context.get('locale_code')

    if article.recommended_articles.all():
        recommended_articles = article.recommended_articles.all()
    else:
        a = article.get_main_language_page()
        recommended_articles = a.specific.recommended_articles.all()
    # http://stackoverflow.com/questions/4916851/django-get-a-queryset-from-array-of-ids-in-specific-order/37648265#37648265 # noqa
    # the following allows us to order the results of the querystring
    recommended_articles_queryset = recommended_articles.values_list(
        'recommended_article', flat=True)

    if not recommended_articles_queryset:
        return []
    preserved = Case(
        *[When(pk=pk, then=pos) for pos, pk in enumerate(
                recommended_articles_queryset)])
    articles = ArticlePage.objects.filter(
                  pk__in=recommended_articles_queryset).order_by(preserved)

    return get_pages(context, articles, locale_code)


@register.simple_tag(takes_context=True)
def should_hide_delete_button(context, page):
    return hasattr(page.specific, 'hide_delete_button')
