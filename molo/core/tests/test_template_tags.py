# coding=utf-8
import pytest
from mock import patch
from django.utils import timezone
from django.test import TestCase, RequestFactory
from molo.core.models import (
    Main, SiteLanguageRelation, Languages, BannerPage, ArticlePageTags,
    SiteSettings
)
from molo.core.tests.base import MoloTestCaseMixin
from molo.core.templatetags.core_tags import (
    get_parent, bannerpages, load_tags_for_article, get_recommended_articles,
    hero_article, render_translations, load_descendant_articles_for_section,
    load_child_articles_for_section,
    get_tag_articles, load_sections
)


@pytest.mark.django_db
class TestModels(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.main = Main.objects.all().first()
        self.factory = RequestFactory()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)

        self.french = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='fr',
            is_active=True)

        self.yourmind = self.mk_section(
            self.section_index, title='Your mind')
        self.yourmind_sub = self.mk_section(
            self.yourmind, title='Your mind subsection')
        # create a requset object
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        self.request._wagtail_site = self.main.get_site()

    def test_render_translations(self):
        # this should return an empty dictionary for non main lang pages
        article = self.mk_articles(self.yourmind, 1)[0]
        fr_article = self.mk_article_translation(article, self.french)
        self.assertEqual(render_translations({}, fr_article), {})

    def test_bannerpages_without_position(self):
        banner = BannerPage(title='test banner')
        self.banner_index.add_child(instance=banner)
        banner.save_revision().publish()
        banner2 = BannerPage(title='test banner 2')
        self.banner_index.add_child(instance=banner2)
        banner2.save_revision().publish()
        banner3 = BannerPage(title='test banner 3')
        self.banner_index.add_child(instance=banner3)
        banner3.save_revision().publish()
        self.assertEqual(self.main.bannerpages().count(), 3)

        request = self.factory.get('/')
        request._wagtail_site = self.site

        self.assertEqual(len(bannerpages({
            'locale_code': 'en', 'request': request})['bannerpages']), 3)

    def test_bannerpages_with_position(self):
        banner = BannerPage(title='test banner')
        self.banner_index.add_child(instance=banner)
        banner.save_revision().publish()
        banner2 = BannerPage(title='test banner 2')
        self.banner_index.add_child(instance=banner2)
        banner2.save_revision().publish()
        banner3 = BannerPage(title='test banner 3')
        self.banner_index.add_child(instance=banner3)
        banner3.save_revision().publish()
        self.assertEqual(self.main.bannerpages().count(), 3)

        request = self.factory.get('/')
        request._wagtail_site = self.site

        self.assertEqual(len(bannerpages({
            'locale_code': 'en',
            'request': request}, position=0)['bannerpages']), 1)
        self.assertEqual(bannerpages({
            'locale_code': 'en',
            'request': request}, position=0)['bannerpages'][0].title,
            'test banner')
        self.assertEqual(bannerpages({
            'locale_code': 'en',
            'request': request}, position=1)['bannerpages'][0].title,
            'test banner 2')

    def test_bannerpages_with_position_out_of_range(self):
        banner = BannerPage(title='test banner')
        self.banner_index.add_child(instance=banner)
        banner.save_revision().publish()
        banner2 = BannerPage(title='test banner 2')
        self.banner_index.add_child(instance=banner2)
        banner2.save_revision().publish()
        banner3 = BannerPage(title='test banner 3')
        self.banner_index.add_child(instance=banner3)
        banner3.save_revision().publish()
        self.assertEqual(self.main.bannerpages().count(), 3)

        request = self.factory.get('/')
        request._wagtail_site = self.site

        self.assertEqual(bannerpages({
            'locale_code': 'en',
            'request': request}, position=4), None)

    def test_get_parent_template_tag(self):
        request = self.factory.get('/')
        request._wagtail_site = self.site

        article = self.mk_articles(self.yourmind, 1)[0]
        fr_article = self.mk_article_translation(article, self.french)

        self.assertEqual(
            get_parent({'locale_code': 'fr', 'request': request}, article),
            self.yourmind)
        self.assertEqual(
            get_parent({'locale_code': 'fr', 'request': request}, fr_article),
            self.yourmind)
        self.assertEqual(get_parent(
            {'locale_code': 'fr', 'request': request}, self.yourmind_sub),
            self.yourmind)

        fr_yourmind = self.mk_section_translation(self.yourmind, self.french)
        self.assertEqual(
            get_parent({'locale_code': 'en', 'request': request}, article),
            self.yourmind)
        self.assertEqual(
            get_parent({'locale_code': 'en', 'request': request}, fr_article),
            self.yourmind)
        self.assertEqual(get_parent(
            {'locale_code': 'en', 'request': request}, self.yourmind_sub),
            self.yourmind)

        self.assertEqual(
            get_parent({'locale_code': 'fr', 'request': request}, article),
            fr_yourmind)
        self.assertEqual(
            get_parent({'locale_code': 'fr', 'request': request}, fr_article),
            fr_yourmind)
        self.assertEqual(get_parent(
            {'locale_code': 'fr', 'request': request}, self.yourmind_sub),
            fr_yourmind)

        self.assertEqual(get_parent(
            {'locale_code': 'fr', 'request': request}, self.yourmind),
            None)

    def test_load_tags_for_article(self):
        request = self.factory.get('/')
        request._wagtail_site = self.site
        article1 = self.mk_article(self.yourmind, title='article 1')

        tag = self.mk_tag(parent=self.tag_index)
        ArticlePageTags.objects.create(page=article1, tag=tag)
        self.assertEqual(load_tags_for_article(
            {
                'locale_code': 'en',
                'request': request
            }, article1)[0],
            tag)
        self.assertEqual(load_tags_for_article(
            {
                'locale_code': 'en',
                'request': request
            }, self.yourmind),
            None)

    def test_article_ordering_descendant_articles(self):
        today = timezone.now()
        request = self.factory.get('/')
        request._wagtail_site = self.site
        settings = SiteSettings.objects.create(
            site=self.site,
            article_ordering_within_section='pk'
        )
        article1 = self.mk_article(
            self.yourmind, title='article 1',
            first_published_at=today - timezone.timedelta(hours=1),
            featured_in_section_start_date=today - timezone.timedelta(hours=1)
        )
        article2 = self.mk_article(
            self.yourmind, title='article 2',
            first_published_at=today,
            featured_in_section_start_date=today
        )

        self.assertEqual(load_descendant_articles_for_section({
            'locale_code': 'en', 'request': request
        }, self.yourmind)[0], article1)
        self.assertEqual(load_descendant_articles_for_section({
            'locale_code': 'en', 'request': request
        }, self.yourmind)[1], article2)

        settings.article_ordering_within_section = 'pk_desc'
        settings.save()

        self.assertEqual(load_descendant_articles_for_section({
            'locale_code': 'en', 'request': request
        }, self.yourmind)[0], article2)
        self.assertEqual(load_descendant_articles_for_section({
            'locale_code': 'en', 'request': request
        }, self.yourmind)[1], article1)

    def test_article_ordering_child_articles(self):
        today = timezone.now()
        request = self.factory.get('/')
        request._wagtail_site = self.site
        settings = SiteSettings.objects.create(
            site=self.site,
            article_ordering_within_section='pk'
        )
        article1 = self.mk_article(self.yourmind, title='article 1')
        article1.first_published_at = today + timezone.timedelta(hours=1)
        article1.save()

        article2 = self.mk_article(self.yourmind, title='article 2')
        article2.first_published_at = today - timezone.timedelta(hours=1)
        article2.save()

        self.assertEqual(load_child_articles_for_section({
            'locale_code': 'en', 'request': request
        }, self.yourmind)[0], article1)
        self.assertEqual(load_child_articles_for_section({
            'locale_code': 'en', 'request': request
        }, self.yourmind)[1], article2)

        settings.article_ordering_within_section = 'pk_desc'
        settings.save()

        self.assertEqual(load_child_articles_for_section({
            'locale_code': 'en', 'request': request
        }, self.yourmind)[0], article2)
        self.assertEqual(load_child_articles_for_section({
            'locale_code': 'en', 'request': request
        }, self.yourmind)[1], article1)

    def test_get_recommended_articles(self):
        request = self.factory.get('/')
        request._wagtail_site = self.site
        article1 = self.mk_article(self.yourmind, title='article 1')

        self.assertEqual(get_recommended_articles(
            {'locale_code': 'en', 'request': request}, article1),
            [])

    @patch('molo.core.templatetags.core_tags.get_pages')
    def test_hero_article_empty_queryset_if_no_site(self, get_pages_mock):
        request = self.factory.get('/')
        request._wagtail_site = self.site
        context = {'request': request, 'locale_code': 'en'}
        get_pages_mock.return_value = []

        self.assertEqual(
            hero_article(context),
            {
                'articles': [],
                'request': request,
                'locale_code': 'en',
            }
        )

    def test_get_tag_articles(self):
        request = self.factory.get('/')
        request._wagtail_site = self.site
        your_body = self.mk_section(
            self.section_index, title='Your body')

        article01 = self.mk_article(your_body, title='Your body 1')
        article02 = self.mk_article(your_body, title='Your body 2')

        article1 = self.mk_article(self.yourmind, title='article 1')
        article2 = self.mk_article(self.yourmind, title='article 2')

        self.mk_article(self.yourmind, title='article 3')
        self.mk_article(self.yourmind, title='article 4')
        self.mk_article(self.yourmind, title='article 5')
        self.mk_article(self.yourmind, title='article 6')
        self.mk_article(self.yourmind, title='article 7')
        self.mk_article(self.yourmind, title='article 8')
        self.mk_article(self.yourmind, title='article 9')

        tag1 = self.mk_tag(parent=self.main, feature_in_homepage=True)
        tag2 = self.mk_tag(parent=self.main, feature_in_homepage=True)

        ArticlePageTags.objects.create(page=article1, tag=tag1)
        ArticlePageTags.objects.create(page=article01, tag=tag1)

        ArticlePageTags.objects.create(page=article2, tag=tag2)
        ArticlePageTags.objects.create(page=article02, tag=tag2)

        articles = get_tag_articles({'locale_code': 'en', 'request': request})
        tag_articles = articles['tags_list'][0][1]

        for i in tag_articles:
            self.assertNotIn(i, articles['sections'])
            self.assertNotIn(i, articles['latest_articles'])

    def test_load_sections(self):
        request = self.factory.get('/')
        request._wagtail_site = self.site
        context = {'locale_code': 'en', 'request': request}

        your_body = self.mk_section(
            self.section_index, title='Your body')

        service = self.mk_section(
            self.section_index,
            title='Service dir', is_service_aggregator=True)

        self.assertTrue(service not in load_sections(context))
        self.assertTrue(service in load_sections(
            context, service_aggregator=True))

        self.assertTrue(your_body in load_sections(context))
        self.assertTrue(your_body not in load_sections(
            context, service_aggregator=True))
