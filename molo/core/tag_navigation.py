from django.core.cache import cache

from molo.core.models import ArticlePage, SectionPage, Tag
from molo.core.templatetags.core_tags import (
    get_pages, get_articles_for_tags_with_translations)


class TagNavigation(object):
    def __init__(
            self, context, section_count, tag_count, sec_articles_count,
            latest_article_count):
        self.context = context
        self.section_count = section_count
        self.tag_count = tag_count
        self.sec_articles_count = sec_articles_count
        self.latest_article_count = latest_article_count

        self.request = context['request']
        self.locale = context.get('locale_code')

        self.exclude_pks = []
        self.all_translated_latest_articles = []

    def get_cache_prefix(self):
        return "tag_navigation_{}_{}_{}_{}_{}".format(
            self.section_count, self.tag_count, self.sec_articles_count,
            self.latest_article_count, self.locale)

    def get_featured_latest_articles_cache_key(self):
        return "{}_featured_latest_articles".format(
            self.get_cache_prefix())

    def get_sections_list_cache_key(self):
        return "{}_sections_list".format(
            self.get_cache_prefix())

    def get_featured_latest_articles(self):
        latest_articles = []
        # get x amount of articles featured in latest
        # ordered by featured in latest promote date

        self.all_latest_articles = ArticlePage.objects\
            .descendant_of(self.request.site.root_page)\
            .filter(
                languages__language__is_main_language=True,
                featured_in_latest=True)\
            .exact_type(ArticlePage)\
            .order_by('-featured_in_latest_start_date')

        if self.all_latest_articles.exists():
            self.all_translated_latest_articles = get_pages(
                self.context, self.all_latest_articles, self.locale)

            if self.all_translated_latest_articles:
                if len(self.all_translated_latest_articles) >= \
                        self.latest_article_count:
                    latest_articles = self.all_translated_latest_articles[
                        :self.latest_article_count]
                    self.exclude_pks += [p.pk for p in latest_articles]
                else:
                    latest_articles = self.all_translated_latest_articles
                    self.exclude_pks += [p.pk for p in latest_articles]
            elif len(self.all_latest_articles) >= self.latest_article_count:
                latest_articles = self.all_latest_articles[
                    :self.latest_article_count]
                self.exclude_pks += [p.pk for p in latest_articles]
            else:
                latest_articles = self.all_latest_articles
                self.exclude_pks += [p.pk for p in latest_articles]
        return latest_articles

    def get_sections_articles_list(self):
        sections_list = []
        sections = self.request.site.root_page.specific.sections()
        for section in sections[:self.section_count]:
            sec_articles = ArticlePage.objects.descendant_of(section).filter(
                languages__language__is_main_language=True,
                featured_in_homepage=True).order_by(
                    '-featured_in_homepage_start_date').exclude(
                    pk__in=self.exclude_pks)
            self.exclude_pks += [
                p.pk for p in sec_articles[:self.sec_articles_count]]
            section = SectionPage.objects.filter(pk=section.pk)
            section_for_locale = get_pages(self.context, section, self.locale)
            if section_for_locale:
                section = section_for_locale[0]
            sec_articles_for_locale = get_pages(
                self.context, sec_articles, self.locale)

            if sec_articles_for_locale and len(
                    sec_articles_for_locale) > self.sec_articles_count:
                sec_articles_for_locale = sec_articles_for_locale[
                    :self.sec_articles_count]

            if section_for_locale:
                sections_list.append((
                    section,
                    sec_articles_for_locale))

        return sections_list

    def get_tags_article_list(self):
        tags_list = []
        tag_qs = Tag.objects.descendant_of(self.request.site.root_page).filter(
            feature_in_homepage=True).live()
        for tag in tag_qs:
            tag_articles = get_articles_for_tags_with_translations(
                self.request, tag, self.locale,
                self.context, self.exclude_pks)
            if tag_articles and len(tag_articles) > self.tag_count:
                tag_articles = tag_articles[:self.tag_count]
            self.exclude_pks += [p.pk for p in tag_articles]
            tag_for_locale = get_pages(
                self.context, tag_qs.filter(pk=tag.pk), self.locale)
            if tag_for_locale:
                tags_list.append((tag_for_locale[0], tag_articles))
            else:
                tags_list.append((tag, tag_articles))
        return tags_list

    def get_cached_featured_latest_articles(self):
        cache_key = self.get_featured_latest_articles_cache_key()
        featured_latest_articles_pk = cache.get(cache_key)
        if featured_latest_articles_pk:
            featured_latest_articles = ArticlePage.objects\
                .descendant_of(self.request.site.root_page)\
                .filter(pk__in=featured_latest_articles_pk)\
                .order_by('-featured_in_latest_start_date')\
                .exact_type(ArticlePage)\
                .live()
            return get_pages(
                self.context, featured_latest_articles, self.locale)

    def get_cached_sections_list(self):
        cache_key = self.get_sections_list_cache_key()
        sections_list_cache = cache.get(cache_key)
        if sections_list_cache:
            return [
                (SectionPage.objects.get(pk=section_pk),
                 ArticlePage.objects.filter(pk__in=articles_pk).order_by(
                    '-featured_in_homepage_start_date').live())
                for section_pk, articles_pk in sections_list_cache]

    def get_data(self):
        data = {}

        latest_articles = self.get_cached_featured_latest_articles()
        if not latest_articles:
            latest_articles = self.get_featured_latest_articles()
            cache.set(
                self.get_featured_latest_articles_cache_key(),
                [article.pk for article in latest_articles], 300)

        # Featured Section/s
        sections_list = self.get_cached_sections_list()
        if not sections_list:
            sections_list = self.get_sections_articles_list()
            cache.set(
                self.get_sections_list_cache_key(),
                [(section.pk, [article.pk for article in articles])
                 for section, articles in sections_list],
                300)

        data.update({'sections': sections_list})

        # Featured Tag/s
        tags_list = self.get_tags_article_list()
        data.update({'tags_list': tags_list})

        # Latest Articles
        remainder_articles_qs = ArticlePage.objects\
            .descendant_of(self.request.site.root_page)\
            .filter(languages__language__is_main_language=True)\
            .exact_type(ArticlePage)\
            .exclude(pk__in=self.exclude_pks)\
            .exclude(translations__translated_page__pk__in=self.exclude_pks)\
            .order_by('-featured_in_latest')

        remainder_articles_translated = get_pages(
            self.context, remainder_articles_qs, self.locale)

        data.update({
            'latest_articles':
                latest_articles + remainder_articles_translated})
        return data
