from os import environ
import json
import pytest
import responses
import urllib

from datetime import timedelta, datetime
from urlparse import parse_qs

from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings, Client
from django.utils import timezone
from django.http import HttpRequest

from molo.core.tests.base import MoloTestCaseMixin
from molo.core.models import (
    FooterPage, SectionPage, SiteSettings, ArticlePage,
    ArticlePageRecommendedSections, ArticlePageRelatedSections, Main,
    BannerIndexPage, SectionIndexPage, FooterIndexPage, Languages,
    SiteLanguageRelation, Tag, ArticlePageTags, ReactionQuestion,
    ArticlePageReactionQuestions)
from molo.core.known_plugins import known_plugins
from molo.core.tasks import promote_articles
from molo.core.templatetags.core_tags import \
    load_descendant_articles_for_section
from molo.core.wagtail_hooks import copy_translation_pages

from mock import patch, Mock
from six import b
from bs4 import BeautifulSoup

from wagtail.wagtailcore.models import Site, Page
from wagtail.wagtailimages.tests.utils import Image, get_test_image_file
from wagtailmedia.models import Media


@pytest.mark.django_db
@override_settings(GOOGLE_ANALYTICS={})
class TestPages(TestCase, MoloTestCaseMixin):

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
        self.yourmind_sub = self.mk_section(
            self.yourmind, title='Your mind subsection')

        self.yourmind_fr = self.mk_section_translation(
            self.yourmind, self.french, title='Your mind in french')
        self.yourmind_sub_fr = self.mk_section_translation(
            self.yourmind_sub, self.french,
            title='Your mind subsection in french')

        # Create an image for running tests on
        self.image = Image.objects.create(
            title="Test image",
            file=get_test_image_file(),
        )

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

        # Create an image for running tests on
        self.image2 = Image.objects.create(
            title="Test image",
            file=get_test_image_file(),
        )

        self.yourmind2 = self.mk_section(
            self.section_index2, title='Your mind2')
        self.yourmind_sub2 = self.mk_section(
            self.yourmind2, title='Your mind subsection2')

    def test_site_redirect_if_no_languages(self):
        user = User.objects.create_superuser(
            username='testuser', password='password', email='test@email.com')
        self.mk_main2(title='main3', slug='main3', path=00010003)
        main3_pk = Page.objects.get(title='main3').pk
        main3 = Main.objects.all().last()
        client = Client(HTTP_HOST=main3.get_site().hostname)
        client.login(user=user)
        response = client.get('/admin/pages/%s/' % main3_pk)
        admin_url = '/admin/pages/%s/' % main3_pk
        self.assertEqual(
            response['Location'],
            '/admin/login/?next=' + urllib.quote(admin_url, safe=''))

    def test_copy_langauges_for_translatable_pages_only(self):
        request = HttpRequest()
        response = copy_translation_pages(
            request, self.section_index, self.section_index2)
        self.assertEquals(response, 'Not translatable page')

    def test_able_to_copy_main(self):
        # testing that copying a main page does not give an error
        self.user = self.login()
        article = self.mk_article(self.yourmind)
        article2 = self.mk_article(self.yourmind)
        question = self.mk_reaction_question(self.reaction_index, article)
        tag = self.mk_tag(parent=self.tag_index)
        ArticlePageTags.objects.create(page=article, tag=tag)
        ArticlePageRecommendedSections.objects.create(
            page=article, recommended_article=article2)
        ArticlePageRelatedSections.objects.create(
            page=article, section=self.yourmind)

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
        self.assertEquals(
            main3.get_children().count(), self.main.get_children().count())

        self.assertEqual(len(mail.outbox), 1)
        [email] = mail.outbox
        self.assertEqual(email.subject, 'Molo Content Copy')
        self.assertEqual(email.from_email, 'support@moloproject.org')
        self.assertEqual(email.to, ['superuser@email.com'])
        self.assertTrue('superuser' in email.body)
        self.assertTrue(
            'The content copy from Main to blank is complete.'
            in email.body)
        new_article = ArticlePage.objects.descendant_of(main3).get(
            slug=article.slug)
        new_article2 = ArticlePage.objects.descendant_of(main3).get(
            slug=article2.slug)
        new_tag = Tag.objects.descendant_of(main3).get(slug=tag.slug)
        new_question = ReactionQuestion.objects.descendant_of(main3).get(
            slug=question.slug)
        new_section = SectionPage.objects.descendant_of(main3).get(
            slug=self.yourmind.slug)
        self.assertEqual(ArticlePageTags.objects.get(
            page=new_article).tag.pk, new_tag.pk)
        self.assertEqual(ArticlePageReactionQuestions.objects.get(
            page=new_article).reaction_question.pk, new_question.pk)
        self.assertEqual(ArticlePageRelatedSections.objects.get(
            page=new_article).section.pk, new_section.pk)
        self.assertEqual(ArticlePageRecommendedSections.objects.get(
            page=new_article).recommended_article.pk, new_article2.pk)

    def test_copy_method_of_section_page_copies_translations_subpages(self):
        self.assertFalse(
            Languages.for_site(
                self.main2.get_site()).languages.filter(locale='fr').exists())
        article = self.mk_articles(self.yourmind, 1)[0]
        self.mk_article_translation(article, self.french)
        self.mk_section_translation(self.yourmind, self.french)
        self.user = self.login()
        self.client.post(reverse(
            'wagtailadmin_pages:copy',
            args=(self.yourmind.id,)),
            data={
                'new_title': 'blank',
                'new_slug': 'blank',
                'new_parent_page': self.section_index2.id,
                'copy_subpages': 'true',
                'publish_copies': 'true'})
        self.assertTrue(
            Languages.for_site(
                self.main2.get_site()).languages.filter(locale='fr').exists())
        self.assertFalse(
            Languages.for_site(
                self.main2.get_site()).languages.filter(
                    locale='fr').first().is_active)
        new_section = Page.objects.get(slug='blank')
        self.assertEquals(new_section.get_site(), self.main2.get_site())
        self.assertEquals(
            new_section.get_children().count(),
            self.yourmind.get_children().count())
        self.assertEquals(
            new_section.translations.all().count(),
            self.yourmind.translations.all().count())

    @override_settings(CELERY_ALWAYS_EAGER=True)
    def test_copy_main_with_celery_disabled(self):
        '''
        Ensure copy task completes by setting celery to execute immediately
        '''
        self.assertFalse(
            Languages.for_site(
                self.main2.get_site()).languages.filter(locale='fr').exists())
        article = self.mk_articles(self.yourmind, 1)[0]
        self.mk_article_translation(article, self.french)
        self.mk_section_translation(self.yourmind, self.french)
        self.user = self.login()

        self.assertEquals(Page.objects.descendant_of(self.main).count(), 13)

        response = self.client.post(reverse(
            'wagtailadmin_pages:copy',
            args=(self.main.id,)),
            data={
                'new_title': 'new-main',
                'new_slug': 'new-main',
                'new_parent_page': self.root.id,
                'copy_subpages': 'true',
                'publish_copies': 'true'})
        self.assertEquals(response.status_code, 302)
        new_main = Page.objects.get(slug='new-main')
        self.assertEquals(Page.objects.descendant_of(new_main).count(), 13)

        self.assertEqual(len(mail.outbox), 1)
        [email] = mail.outbox
        self.assertEqual(email.subject, 'Molo Content Copy')

    @override_settings(CELERY_ALWAYS_EAGER=False)
    def test_copy_main_with_celery_enabled(self):
        '''
        Prevent copy on index page from getting executed immediately
        by forcing celery to queue the task, but not execute them
        '''
        self.assertFalse(
            Languages.for_site(
                self.main2.get_site()).languages.filter(locale='fr').exists())
        article = self.mk_articles(self.yourmind, 1)[0]
        self.mk_article_translation(article, self.french)
        self.mk_section_translation(self.yourmind, self.french)
        self.user = self.login()

        self.assertEquals(Page.objects.descendant_of(self.main).count(), 13)

        response = self.client.post(reverse(
            'wagtailadmin_pages:copy',
            args=(self.main.id,)),
            data={
                'new_title': 'new-main-celery',
                'new_slug': 'new-main-celery',
                'new_parent_page': self.root.id,
                'copy_subpages': 'true',
                'publish_copies': 'true'})
        self.assertEquals(response.status_code, 302)

        new_main_celery = Page.objects.get(slug='new-main-celery')
        # few pages created since we're not letting celery run
        self.assertEquals(
            Page.objects.descendant_of(new_main_celery).count(), 6)

        # no email sent since copy is not complete
        self.assertEqual(len(mail.outbox), 0)

    def test_breadcrumbs(self):
        self.mk_articles(self.yourmind_sub, count=10)

        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)
        self.assertNotContains(
            response,
            '<a href="/"  class="breadcrumbs-list-with-bg__anchor">Home</a>')

        response = self.client.get('/sections-main-1/your-mind/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(
            response,
            '<span class="breadcrumbs-list-with-bg__anchor is-active">'
            'Your mind</span>')

        response = self.client.get(
            '/sections-main-1/your-mind/your-mind-subsection/test-page-1/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(
            response,
            '<span class="breadcrumbs-list-with-bg__anchor is-active">'
            'Test page 1</span>')

    def test_footer_pages(self):
        self.footer = FooterPage(
            title='Footer Page',
            slug='footer-page')
        self.footer_index.add_child(instance=self.footer)
        footer_french = self.mk_article_translation(
            self.footer, self.french,
            title='Footer Page in french')

        response = self.client.get('/')
        self.assertContains(response, 'Footer Page')
        self.assertContains(
            response,
            '<a href="/footers-main-1/footer-page/">Footer Page</a>',
            html=True)
        self.assertNotContains(
            response,
            '<a href="/%s/">Footer Page in french</a>' % footer_french.slug,
            html=True)

        response = self.client.get(
            '/sections-main-1/your-mind/your-mind-subsection/')
        self.assertContains(response, 'Footer Page')
        self.assertNotContains(response, 'Footer Page in french')

    def test_section_listing(self):
        self.mk_articles(
            self.yourmind_sub, count=10,
            featured_in_homepage_start_date=datetime.now())
        promote_articles()
        self.yourmind.extra_style_hints = '-yellow'
        self.yourmind.save_revision().publish()
        response = self.client.get('/')
        self.assertContains(response, 'Your mind')
        self.assertContains(
            response,
            '<a href="/sections-main-1/your-mind/"'
            ' class="nav-list__anchor">Your mind</a>', html=True)
        self.assertContains(response, 'listing__theme-bg-yellow')

    def test_correct_languages_on_homepage(self):
        response = self.client.get('/')
        self.assertContains(
            response,
            '<a href="/locale/en/?next=/?" class="language-list__anchor '
            'language-list__anchor-with-label is-active">English</a>',
            html=True)
        self.assertContains(
            response, '<a href="/locale/fr/')
        self.assertContains(
            response, '<a href="/locale/es/')
        self.assertContains(
            response, '<a href="/locale/ar/')

        client = Client(HTTP_HOST=self.site2.hostname)
        response = client.get(self.site2.root_url)
        self.assertContains(
            response,
            '<a href="/locale/en/?next=/?" class="language-list__anchor '
            'language-list__anchor-with-label is-active">English</a>',
            html=True)
        self.assertContains(
            response, '<a href="/locale/es/')
        self.assertNotContains(
            response, '<a href="/locale/ar/')

    def test_section_listing_multiple_sites(self):
        self.mk_articles(
            self.yourmind_sub, count=10,
            featured_in_homepage_start_date=datetime.now())
        promote_articles()
        self.yourmind.extra_style_hints = '-yellow'
        self.yourmind.save_revision().publish()

        self.mk_articles(
            self.yourmind_sub2, count=10,
            featured_in_homepage_start_date=datetime.now())
        promote_articles()

        self.yourmind2.extra_style_hints = '-purple'
        self.yourmind2.save_revision().publish()
        response = self.client.get('/')
        self.assertContains(response, 'Your mind')
        self.assertContains(
            response,
            '<a href="/sections-main-1/your-mind/"'
            ' class="section-listing__theme-bg-link">Your mind</a>')
        self.assertContains(response, 'listing__theme-bg-yellow">')

        # test second site section listing
        client = Client(HTTP_HOST=self.site2.hostname)
        response = client.get(self.site2.root_url)
        self.assertContains(response, 'Your mind2')
        self.assertContains(
            response,
            '<a href="/sections-main2-1/your-mind2/"'
            ' class="section-listing__theme-bg-link">Your mind2</a>')
        self.assertContains(response, 'listing__theme-bg-purple">')

    def test_section_listing_in_french(self):
        self.yourmind.save_revision().publish()
        article = self.mk_article(
            self.yourmind, title='article', slug='article')
        article.featured_in_homepage_start_date = datetime.now()
        article.save()
        promote_articles()

        response = self.client.get('/')
        self.assertContains(
            response,
            '<a href="/sections-main-1/your-mind/"'
            ' class="section-listing__theme-bg-link">Your mind</a>')
        self.assertNotContains(
            response,
            '<a href="/sections-main-1/your-mind-in-french/"'
            ' class="section-listing__theme-bg-link">Your mind in french</a>')

        response = self.client.get('/locale/fr/')
        response = self.client.get('/')

        self.assertNotContains(
            response,
            '<a href="/sections-main-1/your-mind/"'
            ' class="section-listing__theme-bg-link">Your mind</a>')
        self.assertContains(
            response,
            '<a href="/sections-main-1/your-mind-in-french/"'
            ' class="section-listing__theme-bg-link">Your mind in french</a>')

        # unpublished section should fallback to main language
        self.yourmind_fr.unpublish()

        response = self.client.get('/')

        self.assertContains(
            response,
            '<a href="/sections-main-1/your-mind/"'
            ' class="section-listing__theme-bg-link">Your mind</a>')
        self.assertNotContains(
            response,
            '<a href="/sections-main-1/your-mind-in-french/"'
            ' class="section-listing__theme-bg-link">Your mind in french</a>')

    def test_switching_between_child_languages(self):
        self.yourmind_es = self.mk_section_translation(
            self.yourmind, self.spanish, title='Your mind in spanish')
        self.yourmind_ar = self.mk_section_translation(
            self.yourmind, self.arabic, title='Your mind in arabic')
        en_page = self.mk_article(self.yourmind)
        article = self.mk_article(
            self.yourmind, title='article', slug='article')
        article.featured_in_homepage_start_date = datetime.now()
        article.save()
        promote_articles()

        response = self.client.get('/')
        self.assertContains(
            response,
            '<a href="/sections-main-1/your-mind/"'
            ' class="section-listing__theme-bg-link">Your mind</a>')

        response = self.client.get('/sections-main-1/your-min'
                                   'd/%s/' % (en_page.slug))
        self.assertContains(
            response,
            ' <p>Sample page content for 0</p>')

        fr_page = self.mk_article_translation(
            en_page, self.french,
            title=en_page.title + ' in french',
            subtitle=en_page.subtitle + ' in french',
            body=json.dumps([{
                            'type': 'paragraph',
                            'value': 'Sample page content for %s' % (
                                en_page.title + ' in french')}]),
        )

        response = self.client.get('/locale/fr/')

        response = self.client.get('/sections-main-1/your-m'
                                   'ind/%s/' % (fr_page.slug))
        self.assertContains(response, 'Sample page content for %s' % (
            en_page.title + ' in french'))

        self.mk_article_translation(
            en_page, self.spanish,
            title=en_page.title + ' in spanish',
            subtitle=en_page.subtitle + ' in spanish',
            body=json.dumps([{
                            'type': 'paragraph',
                            'value': 'Sample page content for %s' % (
                                en_page.title + ' in spanish')}]),
        )

        response = self.client.get(
            '/locale/es/?next=/sections-main-1/your-mind/%s/' % (fr_page.slug),
            follow=True)
        self.assertContains(response, 'Sample page content for %s' % (
            en_page.title + ' in spanish'))

    def test_latest_listing(self):
        en_latest = self.mk_articles(
            self.yourmind_sub, count=10,
            featured_in_latest_start_date=datetime.now())
        promote_articles()
        for p in en_latest:
            self.mk_article_translation(
                p, self.french, title=p.title + ' in french')

        response = self.client.get('/')
        self.assertContains(response, 'Latest')
        self.assertContains(
            response,
            '<h5 class="heading'
            ' promoted-article__title--theme-headings">'
            'Test page 8</h5>', html=True)
        self.assertContains(
            response,
            '<h5 class="heading'
            ' promoted-article__title--theme-headings">'
            'Test page 9</h5>', html=True)
        self.assertNotContains(
            response, 'Test page 9 in french')
        self.assertNotContains(
            response, 'in french')

    def test_latest(self):
        en_latest = self.mk_articles(
            self.yourmind_sub, count=4,
            featured_in_latest_start_date=datetime.now())
        promote_articles()
        for p in en_latest:
            self.mk_article_translation(
                p, self.french, title=p.title + ' in french')

        fr_articles = self.mk_articles(self.yourmind_sub, count=10)
        for p in fr_articles:
            self.mk_article_translation(
                p, self.french, title=p.title + ' in french')

        self.assertEquals(self.main.latest_articles().count(), 4)

    def test_latest_listing_in_french(self):
        en_latest = self.mk_articles(
            self.yourmind_sub, count=10,
            featured_in_latest_start_date=datetime.now())
        promote_articles()

        for p in en_latest:
            self.mk_article_translation(
                p, self.french, title=p.title + ' in french')

        response = self.client.get('/locale/fr/')
        response = self.client.get('/')

        self.assertContains(response, 'Latest')
        self.assertContains(
            response,
            '<a href="/sections-main-1/your-mind/your-mind-subsection/'
            'test-page-8-in-french/" class="promoted-article-list__anchor'
            ' promoted-article-list__anchor--theme-headings"><h5'
            ' class="heading'
            ' promoted-article__title--theme-headings">'
            'Test page 8 in french</h5></a>', html=True)
        self.assertContains(
            response,
            '<a href="/sections-main-1/your-mind/your-mind-subsection/'
            'test-page-9-in-french/" class="promoted-article-list__anchor'
            ' promoted-article-list__anchor--theme-headings"><h5'
            ' class="heading'
            ' promoted-article__title--theme-headings">'
            'Test page 9 in french</h5></a>', html=True)
        self.assertNotContains(
            response,
            '<a href="/sections/your-mind/your-mind-subsection/test-page-9/"'
            ' class="promoted-article-list__anchor'
            ' promoted-article-list__anchor--theme-headings">'
            '<h5 class="heading'
            ' promoted-article__title--theme-headings">'
            'Test page 9</h5></a>', html=True)

        # unpublished article should fallback to main language
        en_latest[9].specific.translations.first().translated_page.unpublish()

        response = self.client.get('/')
        self.assertNotContains(
            response,
            '<a href="/sections-main-1/your-mind/your-mind-subsection/'
            'test-page-9-in-french/" class="promoted-article-list__anchor'
            ' promoted-article-list__anchor--theme-headings"><h5'
            ' class="heading'
            ' promoted-article__title--theme-headings">'
            'Test page 9 in french</h5></a>', html=True)
        self.assertContains(
            response,
            '<a href="/sections-main-1/your-mind/your-mind-subsection/'
            'test-page-9/" class="promoted-article-list__anchor'
            ' promoted-article-list__anchor--theme-headings">'
            '<h5 class="heading'
            ' promoted-article__title--theme-headings">'
            'Test page 9</h5></a>', html=True)

    def test_article_page(self):
        self.mk_articles(self.yourmind_sub, count=10)

        response = self.client.get(
            '/sections-main-1/your-mind/your-mind-subsection/test-page-1/')
        self.assertContains(
            response,
            '<h1 class="heading heading--article">'
            'Test page 1</h1>')
        self.assertContains(
            response,
            '<p class="article__desc">Sample page description for 1</p>')

    def test_markdown_in_article_page(self):
        self.mk_articles(
            self.yourmind_sub, count=10,
            body=json.dumps([{
                'type': 'paragraph',
                'value': '<strong>Lorem ipsum</strong> '
                         'dolor <em>sit amet</em>'}]))

        response = self.client.get(
            '/sections-main-1/your-mind/your-mind-subsection/test-page-1/')
        self.assertContains(
            response,
            '<strong>Lorem ipsum</strong> dolor <em>sit amet</em>')

    def test_markdown_in_article_page_list(self):
        self.mk_articles(
            self.yourmind_sub, count=10,
            body=json.dumps([
                {'type': 'list',
                 'value': ['<strong>Lorem ipsum</strong>',
                           'dolor <em>sit amet</em>']},
                {'type': 'numbered_list',
                 'value': ['_ad nec_',
                           'aeque *saepe albucius*']}
            ]))

        response = self.client.get(
            '/sections-main-1/your-mind/your-mind-subsection/test-page-1/')
        self.assertContains(
            response,
            '<li class="unordered-list__item">'
            '<strong>Lorem ipsum</strong></li>')
        self.assertContains(
            response,
            '<li class="unordered-list__item">'
            'dolor <em>sit amet</em></li>')
        self.assertContains(
            response,
            '<li class="ordered-list__item"><em>ad nec</em></li>')
        self.assertContains(
            response,
            '<li class="ordered-list__item">'
            'aeque <em>saepe albucius</em></li>')

    def test_featured_homepage_listing(self):
        self.mk_article(
            self.yourmind_sub, featured_in_homepage_start_date=datetime.now())
        promote_articles()
        response = self.client.get('/')
        self.assertContains(
            response,
            'promoted-article-list__desc'
            ' promoted-article-list__desc--theme-bg">'
            'Sample page description for 0</p>')

    def test_featured_homepage_listing_draft_articles(self):
        article = self.mk_article(
            self.yourmind_sub, featured_in_homepage_start_date=datetime.now())
        article2 = self.mk_article(
            self.yourmind_sub, featured_in_homepage_start_date=datetime.now())
        promote_articles()
        article2.unpublish()
        self.assertEquals(ArticlePage.objects.live().count(), 1)
        featured_in_homepage_articles = load_descendant_articles_for_section(
            {}, self.yourmind_sub, featured_in_homepage=True)
        self.assertEquals(featured_in_homepage_articles.count(), 1)
        self.assertEquals(
            featured_in_homepage_articles.first().title, article.title)

    def test_featured_topic_of_the_day(self):
        promote_date = timezone.now() + timedelta(days=-1)
        demote_date = timezone.now() + timedelta(days=1)
        self.mk_article(
            self.yourmind_sub,
            feature_as_topic_of_the_day=True,
            promote_date=promote_date,
            demote_date=demote_date
        )
        response = self.client.get('/')
        self.assertContains(
            response,
            'Topic of the Day')

    def test_social_media_footer(self):
        default_site = Site.objects.get(is_default_site=True)
        setting = SiteSettings.objects.create(site=default_site)
        setting.social_media_links_on_footer_page = json.dumps([
            {
                'type': 'social_media_site',
                'value': {
                    'title': 'Social Media Site',
                    'link': 'www.socialmediasite.com',
                    'image': 0,
                }}
        ])
        setting.save()

        self.footer = FooterPage(
            title='Footer Page',
            slug='footer-page')
        self.footer_index.add_child(instance=self.footer)

        response = self.client.get('/')
        self.assertContains(
            response,
            'www.socialmediasite.com')

    def test_social_media_facebook_sharing(self):
        default_site = Site.objects.get(is_default_site=True)
        setting = SiteSettings.objects.create(site=default_site)
        setting.facebook_sharing = True
        setting.facebook_image = self.image
        setting.save()

        self.mk_articles(self.yourmind_sub, count=10)

        response = self.client.get(
            '/sections-main-1/your-mind/your-mind-subsection/test-page-1/')
        self.assertContains(
            response,
            'href="http://www.facebook.com/sharer.php?u=http')

    def test_social_media_twitter_sharing(self):
        default_site = Site.objects.get(is_default_site=True)
        setting = SiteSettings.objects.create(site=default_site)
        setting.twitter_sharing = True
        setting.twitter_image = self.image
        setting.save()

        self.mk_articles(self.yourmind_sub, count=10)

        response = self.client.get(
            '/sections-main-1/your-mind/your-mind-subsection/test-page-1/')
        self.assertContains(
            response,
            'href="https://twitter.com/share?url=http')

    def test_featured_homepage_listing_in_french(self):
        en_page = self.mk_article(
            self.yourmind_sub, featured_in_homepage_start_date=datetime.now())
        promote_articles()
        fr_page = self.mk_article_translation(
            en_page, self.french,
            title=en_page.title + ' in french',
            subtitle=en_page.subtitle + ' in french')
        response = self.client.get('/')
        self.assertContains(
            response,
            '<p class="promoted-article-list__desc'
            ' promoted-article-list__desc--theme-bg">'
            'Sample page description for 0</p>')
        self.assertNotContains(
            response,
            '<p>Sample page description for 0 in french</p>')

        response = self.client.get('/locale/fr/')
        response = self.client.get('/')

        self.assertNotContains(
            response,
            '<p class="promoted-article-list__desc'
            ' promoted-article-list__desc--theme-bg">'
            'Sample page description for 0</p>')
        self.assertContains(
            response,
            '<p class="promoted-article-list__desc'
            ' promoted-article-list__desc--theme-bg">'
            'Sample page description for 0 in french</p>')

        # unpublished article should fallback to main language
        fr_page.unpublish()
        response = self.client.get('/')
        self.assertContains(
            response,
            '<p class="promoted-article-list__desc'
            ' promoted-article-list__desc--theme-bg">'
            'Sample page description for 0</p>')
        self.assertNotContains(
            response,
            '<p class="promoted-article-list__desc'
            ' promoted-article-list__desc--theme-bg">'
            'Sample page description for 0 in french</p>')

    def test_page_moving(self):
        # Login
        self.user = self.login()

        self.yourmind_fr = self.mk_section_translation(
            self.yourmind, self.french, title='Your mind in french')
        self.yourmind_ar = self.mk_section_translation(
            self.yourmind, self.arabic, title='Your mind in arabic')
        en_page = self.mk_article(self.yourmind)

        response = self.client.get('/')
        self.assertContains(
            response, '<a href="/sections-main-1/your-mind/"'
            ' class="nav-list__anchor">Your mind</a>', html=True)
        response = self.client.get(
            '/sections-main-1/your-mind/%s/' % (en_page.slug))
        self.assertContains(
            response, 'Sample page content for 0')
        fr_page = self.mk_article_translation(
            en_page, self.french,
            title=en_page.title + ' in french',
            subtitle=en_page.subtitle + ' in french',
            body=json.dumps([{
                            'type': 'paragraph',
                            'value': 'Sample page content for %s' % (
                                en_page.title + ' in french')}]),
        )

        response = self.client.get('/locale/fr/')

        response = self.client.get(
            '/sections-main-1/your-mind/%s/' % (fr_page.slug))
        self.assertContains(response, 'Sample page content for %s' % (
            en_page.title + ' in french'))

        response = self.client.post(reverse(
            'wagtailadmin_pages:move_confirm',
            args=(en_page.id, self.yourmind_sub.id)), data={'blank': 'blank'})
        self.assertEqual(response.status_code, 302)

        page_en = ArticlePage.objects.get(pk=en_page.pk)
        self.assertEquals(page_en.get_parent().specific, self.yourmind_sub)

        page_fr = ArticlePage.objects.get(pk=fr_page.pk)
        self.assertEquals(page_fr.get_parent().specific, self.yourmind_sub)

    def test_health(self):
        environ['MARATHON_APP_ID'] = 'marathon-app-id'
        environ['MARATHON_APP_VERSION'] = 'marathon-app-version'
        response = self.client.get('/health/')
        self.assertEquals(
            response.status_code, 200)
        self.assertEquals(
            json.loads(response.content), {
                'id': 'marathon-app-id',
                'version': 'marathon-app-version',
            })

    def test_issue_with_django_admin_not_loading(self):
        User.objects.create_superuser(
            username='testuser', password='password', email='test@email.com')
        self.client.login(username='testuser', password='password')

        response = self.client.get(reverse('admin:index'))
        self.assertEquals(response.status_code, 200)

    def test_translation_redirects(self):
        en_page = self.mk_article(self.yourmind, featured_in_homepage=True)
        fr_page = self.mk_article_translation(
            en_page, self.french,
            title=en_page.title + ' in french',
            subtitle=en_page.subtitle + ' in french')

        response = self.client.get('/sections-main-1/your-mind/')
        self.assertEquals(response.status_code, 200)

        response = self.client.get('/sections-main-1/your-mind/test-page-0/')
        self.assertEquals(response.status_code, 200)

        response = self.client.get('/locale/fr/')

        response = self.client.get('/sections-main-1/your-mind/')
        self.assertRedirects(
            response,
            'http://main-1.localhost:8000/sections'
            '-main-1/your-mind-in-french/?')

        response = self.client.get('/sections-main-1/your-mind/test-page-0/')
        self.assertRedirects(
            response,
            'http://main-1.localhost:8000/sections-main-1/your-mind/'
            'test-page-0-in-french/?')

        # redirect from translation to main language should also work
        response = self.client.get('/locale/en/')

        response = self.client.get('/sections-main-1/your-mind-in-french/')
        self.assertRedirects(
            response,
            'http://main-1.localhost:8000/sections-main-1/your-mind/?')

        response = self.client.get('/sections-main-1/your-mind/'
                                   'test-page-0-in-french/')
        self.assertRedirects(
            response,
            'http://main-1.localhost:8000/sections-main-1/your-mind/test-pag'
            'e-0/?')

        # unpublished translation will not result in a redirect
        self.yourmind_fr.unpublish()
        response = self.client.get('/sections-main-1/your-mind/')
        self.assertEquals(response.status_code, 200)

        fr_page.unpublish()
        response = self.client.get('/sections-main-1/your-mind/test-page-0/')
        self.assertEquals(response.status_code, 200)

    def test_subsection_is_translated(self):
        en_page = self.mk_article(self.yourmind_sub)
        self.mk_article_translation(
            en_page, self.french,
            title=en_page.title + ' in french',
            subtitle=en_page.subtitle + ' in french')

        response = self.client.get('/sections-main-1/your-mind/')
        self.assertContains(response, 'Your mind subsection</a>')
        self.assertNotContains(response, 'Your mind subsection in french</a>')

        response = self.client.get('/locale/fr/')
        response = self.client.get('/sections-main-1/your-mind-in-french/')

        self.assertContains(response, 'Your mind subsection in french</a>')
        self.assertNotContains(response, 'Your mind subsection</a>')

        # ensure section fallbacks to main language
        self.yourmind_sub_fr.unpublish()
        response = self.client.get('/sections-main-1/your-mind-in-french/')

        self.assertContains(response, 'Your mind subsection</a>')
        self.assertNotContains(response, 'Your mind subsection in french</a>')

    def test_versions_comparison(self):
        response = self.client.get(reverse('versions'))
        self.assertContains(response, 'Molo')
        self.assertContains(response, 'Profiles')

        with patch('pkg_resources.get_distribution', return_value=Mock(
                version='2.5.0')):
            response = self.client.get(reverse('versions'))
            self.assertContains(response, '2.5.0')

        @responses.activate
        def get_pypi_version():
            for plugin in known_plugins():
                responses.add(
                    responses.GET, (
                        'https://pypi.python.org/pypi/%s/json' % plugin[0]),
                    body=json.dumps({'info': {'version': '9.0.0'}}),
                    content_type="application/json",
                    status=200)

            response = self.client.get(reverse('versions'))
            self.assertContains(response, '9.0.0')
            self.assertContains(response, 'Compare')
            self.assertContains(response, 'Not installed')
        get_pypi_version()

    def test_ga_session_for_noscript_middleware(self):
        # GA session doesn't exist until the middleware sets it
        self.assertFalse('MOLO_GA_SESSION_FOR_NOSCRIPT' in self.client.session)

        self.client.get('/')
        self.assertTrue('MOLO_GA_SESSION_FOR_NOSCRIPT' in self.client.session)

        current_session_key = self.client.session[
            'MOLO_GA_SESSION_FOR_NOSCRIPT']

        self.client.get('/')

        # session key should be the same after subsequent requests
        self.assertEquals(
            self.client.session['MOLO_GA_SESSION_FOR_NOSCRIPT'],
            current_session_key)

    def test_local_ga_tag_manager_setting(self):
        default_site = Site.objects.get(is_default_site=True)
        setting = SiteSettings.objects.create(site=default_site)

        response = self.client.get('/')
        self.assertNotContains(response, 'www.googletagmanager.com')

        setting.ga_tag_manager = 'GTM-1234567'
        setting.save()

        response = self.client.get('/')
        self.assertContains(response, 'www.googletagmanager.com')
        self.assertContains(response, 'GTM-1234567')

        self.assertTrue('MOLO_GA_SESSION_FOR_NOSCRIPT' in self.client.session)
        self.assertContains(
            response, self.client.session['MOLO_GA_SESSION_FOR_NOSCRIPT'])

    @responses.activate
    def test_local_ga_tracking_code_setting(self):
        default_site = Site.objects.get(is_default_site=True)
        setting = SiteSettings.objects.create(site=default_site)

        responses.add(
            responses.GET, 'http://www.google-analytics.com/collect',
            body='',
            status=200)

        self.client.get('/')
        self.assertEqual(len(responses.calls), 0)

        setting.local_ga_tracking_code = 'GA-1234567'
        setting.save()

        self.client.get('/')
        self.assertEqual(len(responses.calls), 1)
        self.assertTrue(responses.calls[0].request.url.startswith(
            'http://www.google-analytics.com/collect'))

    @responses.activate
    def test_global_ga_tracking_code_setting(self):
        default_site = Site.objects.get(is_default_site=True)
        setting = SiteSettings.objects.create(site=default_site)

        self.client.get('/')
        self.assertEqual(len(responses.calls), 0)

        setting.global_ga_tracking_code = 'GA-1234567'
        setting.save()

        self.client.get('/')
        self.assertEqual(len(responses.calls), 1)
        self.assertTrue(responses.calls[0].request.url.startswith(
            'http://www.google-analytics.com/collect'))

    @responses.activate
    def test_ga_title_is_filled_in_using_middleware(self):
        default_site = Site.objects.get(is_default_site=True)
        setting = SiteSettings.objects.create(site=default_site)

        self.client.get('/')
        self.assertEqual(len(responses.calls), 0)

        setting.local_ga_tracking_code = 'GA-1234567'
        setting.save()

        self.client.get('/')
        self.assertEqual(len(responses.calls), 1)
        self.assertTrue(responses.calls[0].request.url.startswith(
            'http://www.google-analytics.com/collect'))
        self.assertTrue('GA-1234567' in responses.calls[0].request.url)

        ga_url = responses.calls[0].request.url

        self.assertEqual(parse_qs(ga_url).get('t'), ['pageview'])
        self.assertEqual(parse_qs(ga_url).get('dp'), ['/'])
        self.assertEqual(parse_qs(ga_url).get('dt'), ['Main'])
        self.assertEqual(parse_qs(ga_url).get('tid'), ['GA-1234567'])

    def test_global_ga_tag_manager_setting(self):
        default_site = Site.objects.get(is_default_site=True)
        setting = SiteSettings.objects.create(site=default_site)

        response = self.client.get('/')
        self.assertNotContains(response, 'www.googletagmanager.com')

        setting.global_ga_tag_manager = 'GTM-2345678'
        setting.save()

        response = self.client.get('/')
        self.assertContains(response, 'www.googletagmanager.com')
        self.assertContains(response, 'GTM-2345678')

        self.assertTrue('MOLO_GA_SESSION_FOR_NOSCRIPT' in self.client.session)
        self.assertContains(
            response, self.client.session['MOLO_GA_SESSION_FOR_NOSCRIPT'])

    def test_admin_doesnt_translate_when_frontend_locale_changed(self):
        self.client.get('/locale/af/')

        User.objects.create_superuser(
            username='testuser', password='password', email='test@email.com')
        self.client.login(username='testuser', password='password')

        response = self.client.get('/admin/pages/%d/' % self.main.pk)
        self.assertNotContains(response, 'Skrap')

        response = self.client.get('/django-admin/')
        self.assertNotContains(response, 'Voeg')

    def test_pagination_for_articles_in_sections(self):
        self.mk_articles(self.yourmind, count=15)

        response = self.client.get('/sections-main-1/your-mind/')
        self.assertContains(response, 'Page 1 of 3')
        self.assertContains(response, '&rarr;')
        self.assertNotContains(response, '&larr;')

        response = self.client.get('/sections-main-1/your-mind/?p=2')

        self.assertContains(response, 'Page 2 of 3')
        self.assertContains(response, '&rarr;')
        self.assertContains(response, '&larr;')

        response = self.client.get('/sections-main-1/your-mind/?p=3')

        self.assertContains(response, 'Page 3 of 3')
        self.assertNotContains(response, '&rarr;')
        self.assertContains(response, '&larr;')

    def test_pagination_for_translated_articles_in_sections(self):
        en_articles = self.mk_articles(self.yourmind, count=12)
        self.mk_articles(self.yourmind, count=3)

        for p in en_articles:
            self.mk_article_translation(
                p, self.french, title=p.title + ' in french')

        self.client.get('/locale/fr/')

        response = self.client.get('/sections-main-1/your-mind-in-french/')
        self.assertContains(response, 'Page 1 of 3')
        self.assertContains(response, 'Test page 0 in french')

        response = self.client.get('/sections-main-1/your-mind-in-french/?p=2')
        self.assertContains(response, 'Page 2 of 3')
        self.assertContains(response, 'Test page 7 in french')

        response = self.client.get(
            '/locale/en/?next=/sections-main-1/your-mind-in-frenc'
            'h/?p=3', follow=True)

        self.assertContains(response, 'Page 3 of 3')
        self.assertNotContains(response, 'Test page 11 in french')
        self.assertContains(response, 'Test page 11')

    def test_pagination_for_articles_in_sub_sections(self):
        self.mk_articles(self.yourmind_sub, count=15)

        response = self.client.get('/sections-main-1/your-mind/')
        self.assertNotContains(response, 'Page 1 of 3')

        response = self.client.get('/sections-main-1/your-mind/your-min'
                                   'd-subsection/')
        self.assertContains(response, 'Page 1 of 3')
        self.assertContains(response, '&rarr;')
        self.assertNotContains(response, '&larr;')

        response = self.client.get(
            '/sections-main-1/your-mind/your-mind-subsection/?p=2')

        self.assertContains(response, 'Page 2 of 3')
        self.assertContains(response, '&rarr;')
        self.assertContains(response, '&larr;')

        response = self.client.get(
            '/sections-main-1/your-mind/your-mind-subsection/?p=3')

        self.assertContains(response, 'Page 3 of 3')
        self.assertNotContains(response, '&rarr;')
        self.assertContains(response, '&larr;')


class MultimediaViewTest(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)

        self.yourmind = self.mk_section(
            self.section_index, title='Your mind')

        self.article_page = self.mk_article(self.yourmind,
                                            title='Test Article')

    def add_media(self, media_type):
        fake_file = ContentFile(b("media"))
        fake_file.name = 'media.mp3'
        self.media = Media.objects.create(title="Test Media",
                                          file=fake_file,
                                          duration=100,
                                          type=media_type)

        self.article_page.body = json.dumps([{
            'type': 'media',
            'value': self.media.id,
        }])

        self.article_page.save_revision().publish()

    def test_audio_media(self):
        self.add_media('audio')
        response = self.client.get('/sections-main-1/your-mind/test-article/')
        self.assertContains(
            response,
            '''<div><audio controls><source src="{0}"
            type="audio/mpeg">Click here to download
            <a href="{0}">{1}</a></audio></div>'''
            .format(self.media.file.url, self.media.title),
            html=True)

    def test_video_media(self):
        self.add_media('video')
        response = self.client.get('/sections-main-1/your-mind/test-article/')
        self.assertContains(
            response,
            '''<div><video width="320" height="240" controls>
            <source src="{0}" type="video/mp4">Click here to download
            <a href="{0}">{1}</a></video></div>'''
            .format(self.media.file.url, self.media.title),
            html=True)


class TestArticlePageRelatedSections(TestCase, MoloTestCaseMixin):

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

    def test_article_related_section(self):
        section_a = self.mk_section(self.section_index, title='Section A')
        section_b = self.mk_section(self.section_index, title='Section B')

        article_a = self.mk_article(section_a, title='Article A')
        self.mk_article_translation(
            article_a, self.french, title=article_a.title + ' in french',)
        article_b = self.mk_article(section_b, title='Article B')
        self.mk_article_translation(
            article_b, self.french, title=article_b.title + ' in french',)

        article_a.related_sections.create(page=article_a, section=section_b)
        article_a.save_revision().publish()

        # check article A from section A exist in section A and B
        response = self.client.get('/sections-main-1/section-a/')
        self.assertContains(response, '/sections-main-1/section-a/article-a/')
        response = self.client.get('/sections-main-1/section-b/')
        self.assertContains(response, '/sections-main-1/section-a/article-a/')

        # check article A from section A exist in section A and B
        # when switching to french language and section B is not translated
        self.client.get('/locale/fr/')

        response = self.client.get('/sections-main-1/section-a/')
        self.assertContains(
            response, '/sections-main-1/section-a/article-a-in-french/')

        response = self.client.get('/sections-main-1/section-b/')
        self.assertContains(
            response, '/sections-main-1/section-a/article-a-in-french/')
        self.assertContains(
            response, '/sections-main-1/section-b/article-b-in-french/')

        # check article A from section A exist in section A and B
        # when switching to french language and section B is translated
        self.mk_section_translation(
            section_b, self.french, title=section_b.title + ' in french')

        response = self.client.get('/sections-main-1/section-a/')
        self.assertContains(
            response, '/sections-main-1/section-a/article-a-in-french/')

        response = self.client.get('/sections-main-1/section-b-in-french/')
        self.assertContains(
            response, '/sections-main-1/section-b/article-b-in-french/')
        self.assertContains(
            response, '/sections-main-1/section-a/article-a-in-french/')


class TestArticlePageRecommendedSections(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.main = Main.objects.all().first()
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

        self.section_a = self.mk_section(self.section_index, title='Section A')

        self.section_a.enable_recommended_section = True
        self.section_a.save()

        self.article_a = self.mk_article(self.section_a, title='Article A')
        self.article_a.save_revision().publish()
        self.article_b = self.mk_article(self.section_a, title='Article B')
        self.article_b.save_revision().publish()
        self.article_c = self.mk_article(self.section_a, title='Article C')
        self.article_c.save_revision().publish()
        self.article_d = self.mk_article(self.section_a, title='Article D')
        self.article_d.save_revision().publish()

        self.mk_article_translation(
            self.article_a,
            self.french,
            title=self.article_a.title + ' in french',)
        self.mk_article_translation(
            self.article_b, self.french,
            title=self.article_b.title + ' in french',)
        self.mk_article_translation(
            self.article_c, self.french,
            title=self.article_c.title + ' in french',)

        self.mk_article_translation(
            self.article_d, self.french,
            title=self.article_d.title + ' in french',)

        self.recommended_article_1 = ArticlePageRecommendedSections(
            page=self.article_a,
            recommended_article=self.article_b)
        self.recommended_article_1.save()

        self.recommended_article_2 = ArticlePageRecommendedSections(
            page=self.article_a,
            recommended_article=self.article_c)
        self.recommended_article_2.save()

    def test_article_recommended_section_enabled_disabled(self):

        self.assertTrue(
            self.article_a.get_parent_section()
            .enable_recommended_section)

        self.assertEquals(
            self.article_b,
            self.article_a.recommended_articles.first()
            .recommended_article.specific)

        response = self.client.get('/sections-main-1/section-a/article-a/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'Recommended')
        self.assertContains(response, self.article_b.title)

        self.section_a.enable_recommended_section = False
        self.section_a.save()

        response = self.client.get('/sections-main-1/section-a/article-a/')
        self.assertNotContains(response, 'Recommended')
        self.assertNotContains(response, self.article_b.title)

    def test_article_recommended_section_multi_language(self):
        self.client.get('/locale/fr/')

        response = self.client.get(
            '/sections-main-1/section-a/article-a-in-french/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, self.article_b.title + ' in french')
        self.assertContains(response, self.article_c.title + ' in french')

    def test_article_recommended_section_untranslated(self):
        ArticlePage.objects.get(
            title=self.article_b.title + ' in french').delete()

        self.client.get('/locale/fr/')

        response = self.client.get(
            '/sections-main-1/section-a/article-a-in-french/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, self.article_b.title)
        self.assertContains(response, self.article_c.title + ' in french')

    def test_article_recommended_section_only_translated(self):
        default_site = Site.objects.get(is_default_site=True)
        setting = SiteSettings.objects.create(site=default_site)
        setting.show_only_translated_pages = True
        setting.save()

        ArticlePage.objects.get(
            title=self.article_b.title + ' in french').delete()

        self.client.get('/locale/fr/')

        response = self.client.get(
            '/sections-main-1/section-a/article-a-in-french/')
        self.assertEquals(response.status_code, 200)
        self.assertNotContains(response, self.article_b.title)
        self.assertNotContains(response, self.article_b.title + 'in french')
        self.assertContains(response, self.article_c.title + ' in french')

    def test_article_recommended_custom_recommended_per_language(self):
        self.article_a_fr = ArticlePage.objects.get(
            title=self.article_a.title + ' in french')
        self.article_c_fr = ArticlePage.objects.get(
            title=self.article_c.title + ' in french')

        self.client.get('/locale/fr/')

        response = self.client.get(
            '/sections-main-1/section-a/article-a-in-french/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, self.article_b.title + ' in french')
        self.assertContains(response, self.article_c_fr.title)

        self.recommended_article_3 = ArticlePageRecommendedSections(
            page=self.article_a_fr,
            recommended_article=self.article_c_fr)
        self.recommended_article_3.save()

        self.recommended_article_4 = ArticlePageRecommendedSections(
            page=self.article_a_fr,
            recommended_article=self.article_d)
        self.recommended_article_4.save()

        response = self.client.get(
            '/sections-main-1/section-a/article-a-in-french/')
        self.assertEquals(response.status_code, 200)
        self.assertNotContains(response, self.article_b.title + ' in french')
        self.assertContains(response, self.article_d.title + ' in french')
        self.assertContains(response, self.article_c_fr.title)


class TestArticlePageNextArticle(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.main = Main.objects.all().first()
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

        self.section_a = self.mk_section(self.section_index, title='Section A')

        self.section_a.enable_next_section = True
        self.section_a.save()

        self.article_a = self.mk_article(self.section_a, title='Article A')
        self.article_a.save_revision().publish()
        self.article_b = self.mk_article(self.section_a, title='Article B')
        self.article_b.save_revision().publish()
        self.article_c = self.mk_article(self.section_a, title='Article C')
        self.article_c.save_revision().publish()

        self.mk_article_translation(
            self.article_a,
            self.french,
            title=self.article_a.title + ' in french',)
        self.mk_article_translation(
            self.article_b, self.french,
            title=self.article_b.title + ' in french',)
        self.mk_article_translation(
            self.article_c, self.french,
            title=self.article_c.title + ' in french',)

    def test_next_article_main_language(self):
        # assumes articles loop
        self.assertTrue(
            self.article_b.get_parent_section().enable_next_section)

        response = self.client.get('/sections-main-1/section-a/article-c/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'Next up in ' + self.section_a.title)
        self.assertContains(response, self.article_b.title)

        response = self.client.get('/sections-main-1/section-a/article-b/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'Next up in ' + self.section_a.title)
        self.assertContains(response, self.article_a.title)

        response = self.client.get('/sections-main-1/section-a/article-a/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'Next up in ' + self.section_a.title)
        self.assertContains(response, self.article_c.title)

        self.section_a.enable_next_section = False
        self.section_a.save()

        response = self.client.get('/sections-main-1/section-a/article-c/')
        self.assertEquals(response.status_code, 200)
        self.assertNotContains(response, 'Next up in ' + self.section_a.title)
        self.assertNotContains(response, self.article_b.title)

    def test_next_article_not_main_language(self):
        # assumes articles loop
        self.client.get('/locale/fr/')

        response = self.client.get(
            '/sections-main-1/section-a/article-c-in-french/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, self.article_b.title + ' in french')

        response = self.client.get(
            '/sections-main-1/section-a/article-b-in-french/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, self.article_a.title + ' in french')

        response = self.client.get(
            '/sections-main-1/section-a/article-a-in-french/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, self.article_c.title + ' in french')

    def test_next_article_show_untranslated_pages(self):
        response = self.client.get('/sections-main-1/section-a/article-c/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'Next up in ' + self.section_a.title)
        self.assertContains(response, self.article_b.title)

        ArticlePage.objects.get(
            title=self.article_b.title + ' in french').delete()

        self.client.get('/locale/fr/')

        response = self.client.get(
            '/sections-main-1/section-a/article-c-in-french/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, self.article_b.title)

    def test_next_article_show_only_translated_pages(self):
        default_site = Site.objects.get(is_default_site=True)
        setting = SiteSettings.objects.create(site=default_site)
        setting.show_only_translated_pages = True
        setting.save()

        response = self.client.get('/sections-main-1/section-a/article-c/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'Next up in ' + self.section_a.title)
        self.assertContains(response, self.article_b.title)

        ArticlePage.objects.get(
            title=self.article_b.title + ' in french').delete()

        self.client.get('/locale/fr/')

        response = self.client.get(
            '/sections-main-1/section-a/article-c-in-french/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, self.article_a.title + ' in french')

    def test_next_article_with_related_section(self):
        self.section_b = self.mk_section(self.section_index, title='Section B')
        self.section_b.enable_next_section = True
        self.section_b.save()

        self.article_1 = self.mk_article(self.section_b, title='Article 1')
        self.article_1.save_revision().publish()
        self.article_2 = self.mk_article(self.section_b, title='Article 2')
        self.article_2.related_sections.create(page=self.article_2,
                                               section=self.section_a)
        self.article_2.save_revision().publish()

        response = self.client.get('/sections-main-1/section-b/article-2/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, self.article_1.title)
        self.assertContains(response, 'Next up in ' + self.section_b.title)

    def test_next_article_not_displayed_for_single_article(self):
        self.section_b = self.mk_section(self.section_index, title='Section B')

        self.article_1 = self.mk_article(self.section_b, title='Article 1')
        self.article_1.save_revision().publish()

        response = self.client.get('/sections-main-1/section-b/article-1/')
        self.assertEquals(response.status_code, 200)
        self.assertNotContains(response, 'Next up in')

    def test_next_article_not_displayd_single_article_only_translated(self):
        default_site = Site.objects.get(is_default_site=True)
        setting = SiteSettings.objects.create(site=default_site)
        setting.show_only_translated_pages = True
        setting.save()

        self.section_b = self.mk_section(self.section_index, title='Section B')

        self.article_1 = self.mk_article(self.section_b, title='Article 1')
        self.article_1.save_revision().publish()

        response = self.client.get('/sections-main-1/section-b/article-1/')
        self.assertEquals(response.status_code, 200)
        self.assertNotContains(response, 'Next up in')


class TestDjangoAdmin(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)

    def test_upload_download_links(self):
        User.objects.create_superuser(
            username='testuser', password='password', email='test@email.com')
        self.client.login(username='testuser', password='password')

        response = self.client.get(reverse('admin:index'))

        self.assertEquals(response.status_code, 200)
        self.assertContains(
            response,
            '<a href="/django-admin/upload_media/">Upload Media</a>'
        )
        self.assertContains(
            response,
            '<a href="/django-admin/download_media/">Download Media</a>'
        )


class TestDeleteButtonRemoved(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        main = Main.objects.all().first()
        self.english = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(main.get_site()),
            locale='en',
            is_active=True)

        self.login()

    def test_delete_button_removed_for_index_pages_in_main(self):

        index_titles = [
            BannerIndexPage.objects.first().title,
            SectionIndexPage.objects.first().title,
            FooterIndexPage.objects.first().title,
        ]

        main_page = Main.objects.first()
        response = self.client.get('/admin/pages/{0}/'
                                   .format(str(main_page.pk)))
        self.assertEquals(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        # Get all the rows in the body of the table
        index_page_rows = soup.find_all('tbody')[0].find_all('tr')

        for row in index_page_rows:
            if row.h2.a.string in index_titles:
                self.assertTrue(row.find('a', string='Edit'))
                self.assertFalse(row.find('a', string='Delete'))

    def test_delete_button_removed_from_dropdown_menu_main(self):
        # Remove 'Delete' from drop-down menu
        main_page = Main.objects.first()
        response = self.client.get('/admin/pages/{0}/'
                                   .format(str(main_page.pk)))
        delete_link = ('<a href="/admin/pages/{0}/delete/" '
                       'title="Delete this page" class="u-link '
                       'is-live ">Delete</a>'.format(str(main_page.pk)))

        self.assertEquals(response.status_code, 200)
        self.assertNotContains(response, delete_link, html=True)

    def test_delete_button_removed_in_edit_menu(self):
        main_page = Main.objects.first()
        response = self.client.get('/admin/pages/{0}/edit/'
                                   .format(str(main_page.pk)))

        delete_button = ('<li><a href="/admin/pages/{0}/delete/" '
                         'class="shortcut">Delete</a></li>'
                         .format(str(main_page.pk)))

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, delete_button, html=True)

    def test_delete_button_not_removed_in_edit_menu_for_sections(self):
        section_page = self.mk_section(self.section_index, title='Section A')
        response = self.client.get('/admin/pages/{0}/edit/'
                                   .format(str(section_page.pk)))

        delete_button = ('<li><a href="/admin/pages/{0}/delete/" '
                         'class="shortcut">Delete</a></li>'
                         .format(str(section_page.pk)))

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, delete_button, html=True)


class TestWagtailAdmin(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)
        self.superuser = User.objects.create_superuser(
            username='testuser', password='password', email='test@email.com')

        self.expert_group, _created = Group.objects.get_or_create(
            name='Expert')

        # Create wagtail group with wagtail admin permissions
        self.wagtail_login_only_group, _created = Group.objects.get_or_create(
            name='Wagtail Login Only')

        wagtailadmin_content_type, created = ContentType.objects.get_or_create(
            app_label='wagtailadmin',
            model='admin'
        )

        # Create admin permission
        admin_permission, created = Permission.objects.get_or_create(
            content_type=wagtailadmin_content_type,
            codename='access_admin',
            name='Can access Wagtail admin'
        )

        # add the wagtail login permissions to group
        access_admin = Permission.objects.get(codename='access_admin')
        self.wagtail_login_only_group.permissions.add(access_admin)

        self.admin_user = User.objects.create_user(
            username='username', password='password', email='login@email.com')

    def can_see_explorer(self, client):
        response = client.get('/admin/')
        self.assertEquals(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertTrue(soup.find('a', string='Explorer'))

    def test_superuser_explorer_access(self):
        self.client.login(username='testuser', password='password')

        self.can_see_explorer(self.client)

        self.superuser.groups.set([self.expert_group])

        self.can_see_explorer(self.client)

    def test_wagtail_login_only_user_cannot_see_explorer(self):
        self.admin_user.groups.set([self.wagtail_login_only_group])

        self.client.login(
            username=self.admin_user.username,
            password='password')

        response = self.client.get('/admin/')

        self.assertEquals(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertFalse(soup.find('a', string='Explorer'))
