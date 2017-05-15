from datetime import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse

from molo.core.tests.base import MoloTestCaseMixin
from molo.core.models import (SiteSettings, Main, Languages,
                              SiteLanguageRelation, ArticlePageTags,
                              SectionPageTags, FooterPage, ArticlePage)
from molo.core.tasks import promote_articles
from itertools import chain


class TestTags(MoloTestCaseMixin, TestCase):
    def setUp(self):
        self.mk_main()
        main = Main.objects.all().first()
        self.english = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(main.get_site()),
            locale='en',
            is_active=True)

        self.french = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(main.get_site()),
            locale='fr',
            is_active=True)
        self.spanish = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(main.get_site()),
            locale='es',
            is_active=True)
        self.arabic = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(main.get_site()),
            locale='ar',
            is_active=True)

        self.yourmind = self.mk_section(
            self.section_index, title='Your mind')
        self.yourbody = self.mk_section(
            self.section_index, title='Your body')
        self.yourmind_sub = self.mk_section(
            self.yourmind, title='Your mind subsection')

        self.yourmind_fr = self.mk_section_translation(
            self.yourmind, self.french, title='Your mind in french')
        self.yourmind_sub_fr = self.mk_section_translation(
            self.yourmind_sub, self.french,
            title='Your mind subsection in french')

        self.mk_main2()
        self.main2 = Main.objects.all().last()
        self.language_setting2 = Languages.objects.create(
            site_id=self.main2.get_site().pk)
        self.english2 = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting2,
            locale='en',
            is_active=True)

        self.spanish = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting2,
            locale='es',
            is_active=True)

        self.yourmind2 = self.mk_section(
            self.section_index2, title='Your mind2')
        self.yourmind_sub2 = self.mk_section(
            self.yourmind2, title='Your mind subsection2')

        self.site_settings = SiteSettings.for_site(main.get_site())
        self.site_settings2 = SiteSettings.for_site(self.main2.get_site())
        self.site_settings.enable_clickable_tags = True
        self.site_settings.enable_tag_navigation = True
        self.site_settings.save()

    def unique(self, g):
        s = set()
        for x in g:
            if x.pk in s:
                return False
            s.add(x.pk)
        return True

    def test_tag_nav_data_does_not_pull_in_footer_pages(self):
        self.mk_articles(parent=self.yourmind, count=2)
        footer = FooterPage(title='Test Footer Page')
        self.footer_index.add_child(instance=footer)
        footer.save_revision().publish()
        footer2 = FooterPage(title='Test Footer Page 2')
        self.footer_index.add_child(instance=footer2)
        footer2.save_revision().publish()
        footer3 = FooterPage(title='Test Footer Page 3')
        self.footer_index.add_child(instance=footer3)
        footer3.save_revision().publish()
        footer_pks = [footer.pk, footer2.pk, footer3.pk]

        response = self.client.get('/')
        data = response.context['tag_nav_data']
        hoempage_articles = []
        for section, section_list in data['sections']:
            homepage_articles = list(chain(hoempage_articles, section_list))
        for tag, tag_list in data['tags_list']:
            homepage_articles = list(chain(homepage_articles, tag_list))
        homepage_articles = list(chain(
            homepage_articles, data['latest_articles']))
        for article in homepage_articles:
            self.assertFalse(article.pk in footer_pks)

    def test_article_not_repeated_in_section_for_tag_navigation_enabled(self):
        tag = self.mk_tag(parent=self.tag_index)
        tag.feature_in_section = True
        tag.save_revision().publish()
        articles = self.mk_articles(parent=self.yourmind, count=30)
        other_articles = self.mk_articles(parent=self.yourbody, count=10)
        for article in articles:
            ArticlePageTags.objects.create(page=article, tag=tag)
        for article in other_articles:
            ArticlePageTags.objects.create(page=article, tag=tag)
        SectionPageTags.objects.create(page=self.yourmind, tag=tag)
        SectionPageTags.objects.create(page=self.yourbody, tag=tag)

        response = self.client.get(self.yourmind.url)
        tag_articles = response.context['tags'][0][1]
        section_articles = response.context['articles']
        all_section_articles = list(chain(section_articles, tag_articles))
        self.assertTrue(self.unique(all_section_articles))
        self.assertContains(response, tag.title)
        self.assertEquals(len(tag_articles), 4)

    def test_article_only_site_specific_artcles_show_under_tag(self):
        tag = self.mk_tag(parent=self.tag_index)
        tag.feature_in_homepage = True
        tag.save_revision().publish()
        articles = self.mk_articles(
            parent=self.yourmind,
            featured_in_latest_start_date=datetime.now(),
            featured_in_homepage_start_date=datetime.now(), count=5)
        for article in articles:
            ArticlePageTags.objects.create(page=article, tag=tag)

        promote_articles()
        self.user = self.login()
        response = self.client.post(reverse(
            'wagtailadmin_pages:copy',
            args=(self.main.id,)),
            data={
                'new_title': 'blank',
                'new_slug': 'blank',
                'new_parent_page': self.root.id,
                'copy_subpages': 'true',
                'publish_copies': 'true'})
        self.assertEquals(response.status_code, 302)
        response = self.client.get('/tags/' + tag.slug + '/')
        self.assertEquals(len(response.context['object_list']), 5)
        for article in response.context['object_list']:
            self.assertEquals(article.get_site().pk, self.main.get_site().pk)

    def test_new_tag_article_relations_made_when_copying_site(self):
        tag = self.mk_tag(parent=self.tag_index)
        tag.feature_in_homepage = True
        tag.save_revision().publish()
        articles = self.mk_articles(
            parent=self.yourmind,
            featured_in_latest_start_date=datetime.now(),
            featured_in_homepage_start_date=datetime.now(), count=30)
        for article in articles:
            ArticlePageTags.objects.create(page=article, tag=tag)

        promote_articles()

        self.user = self.login()
        response = self.client.post(reverse(
            'wagtailadmin_pages:copy',
            args=(self.main.id,)),
            data={
                'new_title': 'blank',
                'new_slug': 'blank',
                'new_parent_page': self.root.id,
                'copy_subpages': 'true',
                'publish_copies': 'true'})
        self.assertEquals(response.status_code, 302)
        main3 = Main.objects.get(slug='blank')
        new_articles = ArticlePage.objects.descendant_of(main3)
        new_article_tags = ArticlePageTags.objects.filter(
            page__in=new_articles)
        for article_tag_relation in new_article_tags:
            self.assertEquals(
                article_tag_relation.tag.get_site().pk, main3.get_site().pk)

    def test_article_not_repeated_when_tag_navigation_enabled_homepage(self):
        tag = self.mk_tag(parent=self.tag_index)
        tag.feature_in_homepage = True
        tag.save_revision().publish()
        articles = self.mk_articles(
            parent=self.yourmind,
            featured_in_latest_start_date=datetime.now(),
            featured_in_homepage_start_date=datetime.now(), count=30)
        for article in articles:
            ArticlePageTags.objects.create(page=article, tag=tag)

        promote_articles()

        response = self.client.get('/')
        data = response.context['tag_nav_data']
        hoempage_articles = []
        for section, section_list in data['sections']:
            homepage_articles = list(chain(hoempage_articles, section_list))
        for tag, tag_list in data['tags_list']:
            homepage_articles = list(chain(homepage_articles, tag_list))
        homepage_articles = list(chain(
            homepage_articles, data['latest_articles']))

        self.assertTrue(self.unique(homepage_articles))

    def test_tag_cloud_homepage(self):
        tag = self.mk_tag(parent=self.tag_index)
        response = self.client.get('/')
        self.assertContains(response, tag.title)

    def test_tag_cloud_homepage_translation(self):
        tag = self.mk_tag(parent=self.tag_index)
        self.mk_tag_translation(
            tag,
            self.french,
            title=tag.title + ' in french',)

        self.client.get('/locale/fr/')
        response = self.client.get('/')
        self.assertContains(response, tag.title + ' in french')

    def test_tag_navigation_setting_overrides_other_tags(self):
        article = self.mk_article(self.yourmind, title='article')
        article.tags.add("old tag")
        article.save_revision().publish()

        tag = self.mk_tag(parent=self.tag_index)
        ArticlePageTags.objects.create(page=article, tag=tag)

        response = self.client.get(article.url)
        self.assertNotContains(response, 'old tag')
        self.assertContains(response, tag.title)

    def test_articles_within_tag(self):
        article1 = self.mk_article(self.yourmind, title='article 1')
        article2 = self.mk_article(self.yourmind, title='article 2')
        article3 = self.mk_article(self.yourmind, title='article 3')

        tag = self.mk_tag(parent=self.tag_index)
        ArticlePageTags.objects.create(page=article1, tag=tag)
        ArticlePageTags.objects.create(page=article2, tag=tag)
        ArticlePageTags.objects.create(page=article3, tag=tag)

        response = self.client.get('/tags/' + tag.slug + '/')
        self.assertContains(
            response,
            '<a href="/sections-main-1/your-mind/article-1/"')
        self.assertContains(
            response,
            '<a href="/sections-main-1/your-mind/article-2/"')
        self.assertContains(
            response,
            '<a href="/sections-main-1/your-mind/article-3/"')

    def test_promoted_tags(self):
        articles = self.mk_articles(self.yourmind, count=5)
        tag = self.mk_tag(parent=self.tag_index)
        for article in articles:
            ArticlePageTags.objects.create(page=article, tag=tag)

        tag.feature_in_homepage = True
        tag.save_revision().publish()

        response = self.client.get('/')
        self.assertEquals(
            str(response.context['tag_nav_data']['tags_list']),
            '[(<Tag: Test Tag>, [<ArticlePage: Test page 0>, <ArticlePage'
            ': Test page 1>, <ArticlePage: Test page 2>, <ArticleP'
            'age: Test page 3>])]')
        self.assertNotContains(response, 'Test Page 5')

        tag = self.mk_tag(parent=self.tag_index, title='Not Promoted Tag 1')
        tag = self.mk_tag(parent=self.tag_index, title='Not Promoted Tag 2')

        articles = self.mk_articles(self.yourmind, count=5)
        tag = self.mk_tag(parent=self.tag_index, title='Test Tag 2')
        for article in articles:
            ArticlePageTags.objects.create(page=article, tag=tag)

        tag.feature_in_homepage = True
        tag.save_revision().publish()

        response = self.client.get('/')
        self.assertEquals(
            str(response.context['tag_nav_data']['tags_list']),
            '[(<Tag: Test Tag>, [<ArticlePage: Test page 0>, <ArticlePage: '
            'Test page 1>, <ArticlePage: Test page 2>, <ArticlePage: Test p'
            'age 3>]), (<Tag: Test Tag 2>, [<ArticlePage: Test page 0>, <Ar'
            'ticlePage: Test page 1>, <ArticlePage: Test page 2>, <Articl'
            'ePage: Test page 3>])]')
        self.assertNotContains(response, 'Test Page 5')

    def test_tag_navigation_shows_correct_tag_for_locale(self):
        article = self.mk_article(self.yourmind, title='article')

        tag = self.mk_tag(parent=self.tag_index)
        ArticlePageTags.objects.create(page=article, tag=tag)

        # make the translation for the article and the tag
        self.mk_article_translation(
            article,
            self.french,
            title=article.title + ' in french',)
        self.mk_tag_translation(
            tag,
            self.french,
            title=tag.title + ' in french',)

        self.client.get('/locale/fr/')
        response = self.client.get(
            '/sections-main-1/your-mind/article-in-french/')
        self.assertContains(response, 'Test Tag in french')

    def test_articles_with_the_same_tag(self):
        self.site_settings.enable_tag_navigation = False
        self.site_settings.save()
        # create two articles with the same tag and check that they can
        # be retrieved
        new_section = self.mk_section(
            self.section_index, title="New Section", slug="new-section")
        first_article = self.mk_article(new_section, title="First article", )
        second_article = self.mk_article(new_section, title="Second article", )

        # add common tag to both articles
        first_article.tags.add("common")
        first_article.save_revision().publish()
        second_article.tags.add("common")
        second_article.save_revision().publish()

        # create another article that doesn't have the tag, and check that
        # it will be excluded from the return list
        self.mk_article(new_section, title="Third article", )

        response = self.client.get(
            reverse("tags_list", kwargs={"tag_name": "common"})
        )
        self.assertEqual(
            list(response.context["object_list"]),
            [first_article, second_article]
        )
