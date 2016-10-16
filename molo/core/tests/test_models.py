# coding=utf-8
import pytest
import datetime as dt
from datetime import datetime, timedelta
from django.test import TestCase, RequestFactory
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from django.core.exceptions import ValidationError

from molo.core.models import (
    ArticlePage, SiteLanguage, PageTranslation, SectionPage, Main)
from molo.core import constants
from molo.core.templatetags.core_tags import (
    load_descendant_articles_for_section, load_child_articles_for_section,
    get_translation)
from molo.core.tests.base import MoloTestCaseMixin

from wagtail.wagtailimages.tests.utils import Image, get_test_image_file


@pytest.mark.django_db
class TestModels(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.factory = RequestFactory()
        self.english = SiteLanguage.objects.create(locale='en')
        self.french = SiteLanguage.objects.create(locale='fr')

        # Create an image for running tests on
        self.image = Image.objects.create(
            title="Test image",
            file=get_test_image_file(),
        )

        self.yourmind = self.mk_section(
            self.section_index, title='Your mind')
        self.yourmind_sub = self.mk_section(
            self.yourmind, title='Your mind subsection')

    def test_article_order(self):
        now = datetime.now()
        article1 = self.mk_article(
            self.yourmind_sub, first_published_at=now)

        self.mk_article(
            self.yourmind_sub, first_published_at=now + timedelta(hours=1))

        # most recent first
        self.assertEquals(
            self.yourmind_sub.articles()[0].title, article1.title)

        # swap published date
        article1.first_published_at = now + timedelta(hours=4)
        article1.save_revision().publish()

        self.assertEquals(
            self.yourmind_sub.articles()[0].title, article1.title)

    def test_latest(self):
        en_latest = self.mk_articles(
            self.yourmind_sub, count=4, featured_in_latest=True)
        for p in en_latest:
            self.mk_article_translation(
                p, self.french, title=p.title + ' in french')

        fr_articles = self.mk_articles(self.yourmind_sub, count=10)
        for p in fr_articles:
            self.mk_article_translation(
                p, self.french, title=p.title + ' in french')

        self.assertEquals(self.main.latest_articles().count(), 4)

    def test_featured_homepage(self):
        self.mk_articles(self.yourmind_sub, count=2, featured_in_homepage=True)
        self.mk_articles(self.yourmind_sub, count=10)

        self.assertEquals(
            len(load_descendant_articles_for_section(
                {}, self.yourmind, featured_in_homepage=True)), 2)

    def test_latest_homepage(self):
        self.mk_articles(self.yourmind_sub, count=2, featured_in_latest=True)
        self.mk_articles(self.yourmind_sub, count=10)

        self.assertEquals(
            len(load_descendant_articles_for_section(
                {}, self.yourmind, featured_in_latest=True)), 2)

    def test_image(self):
        new_section = self.mk_section(
            self.section_index,
            title="New Section", slug="new-section",
            image=self.image)
        self.assertEquals(
            new_section.get_effective_image(), self.image)

        # image not set to use inherited value
        new_section2 = self.mk_section(
            new_section, title="New Section 2", slug="new-section-2")
        self.assertEquals(
            new_section2.get_effective_image(), new_section.image)

        # image not set to use inherited value
        new_section3 = self.mk_section(
            new_section2, title="New Section 3", slug="new-section-3")
        self.assertEquals(
            new_section3.get_effective_image(), new_section.image)

    def test_number_of_child_sections(self):
        new_section = self.mk_section(self.section_index)
        self.mk_sections(new_section, count=12)
        response = self.client.get('/sections/test-section-0/')
        self.assertContains(response, 'Test Section 11')

    def test_number_of_child_articles_in_section(self):
        new_section = self.mk_section(self.section_index)
        self.mk_articles(new_section, count=12)
        request = self.factory.get('/sections/test-section-0/')
        request.site = self.site
        articles = load_child_articles_for_section(
            {'request': request, 'locale_code': 'en'}, new_section, count=None)
        self.assertEquals(len(articles), 12)

    def test_parent_section(self):
        new_section = self.mk_section(
            self.section_index, title="New Section", slug="new-section")
        new_section1 = self.mk_section(
            new_section, title="New Section 1", slug="new-section-1")
        self.assertEquals(
            new_section1.get_parent_section(), new_section)

    def test_commenting_closed_settings_fallbacks(self):
        new_section = self.mk_section(
            self.section_index, title="New Section", slug="new-section")
        new_article = self.mk_article(new_section, title="New article")
        # test fallback to section_index
        self.section_index.commenting_state = constants.COMMENTING_CLOSED
        self.section_index.save()
        comment_settings = new_article.get_effective_commenting_settings()
        self.assertEquals(comment_settings['state'],
                          constants.COMMENTING_CLOSED)
        # test overriding settings in section
        new_section.commenting_state = constants.COMMENTING_CLOSED
        new_section.save()
        comment_settings = new_article.get_effective_commenting_settings()
        self.assertEquals(comment_settings['state'],
                          constants.COMMENTING_CLOSED)
        # test overriding settings in article
        new_article.commenting_state = constants.COMMENTING_DISABLED
        new_article.save_revision().publish()
        comment_settings = new_article.get_effective_commenting_settings()
        self.assertEquals(comment_settings['state'],
                          constants.COMMENTING_DISABLED)

    def test_commenting_allowed(self):
        new_section = self.mk_section(
            self.section_index, title="New Section", slug="new-section")
        new_article = self.mk_article(
            new_section, title="New article",
            commenting_state=constants.COMMENTING_OPEN)
        now = datetime.now()
        # with commenting open
        self.assertTrue(new_article.allow_commenting())
        # with commenting disabled and no reopen_time given
        new_article.commenting_state = constants.COMMENTING_DISABLED
        self.assertFalse(new_article.allow_commenting())
        # with commenting closed but past reopen time
        new_article.commenting_state = constants.COMMENTING_CLOSED
        new_article.commenting_open_time = timezone.make_aware(
            now - dt.timedelta(1))
        self.assertTrue(new_article.allow_commenting())
        # with commenting timestamped and within specified time
        new_article.commenting_state = constants.COMMENTING_TIMESTAMPED
        new_article.commenting_open_time = timezone.make_aware(
            now - dt.timedelta(1))
        new_article.commenting_close_time = timezone.make_aware(
            now + dt.timedelta(1))
        self.assertTrue(new_article.allow_commenting())
        # with commenting closed and not yet reopen_time
        new_article.commenting_state = constants.COMMENTING_CLOSED
        new_article.commenting_open_time = timezone.make_aware(
            now + dt.timedelta(1))
        self.assertFalse(new_article.allow_commenting())

    def test_commenting_enabled(self):
        article_1 = ArticlePage(
            title="New article", commenting_state=constants.COMMENTING_OPEN)
        self.assertTrue(article_1.is_commenting_enabled())
        article_2 = ArticlePage(
            title="New article", commenting_state=constants.COMMENTING_CLOSED)
        self.assertTrue(article_2.is_commenting_enabled())
        article_3 = ArticlePage(
            title="New article",
            commenting_state=constants.COMMENTING_DISABLED)
        self.assertFalse(article_3.is_commenting_enabled())

    def test_tags(self):
        User.objects.create_superuser(
            username='testuser', password='password', email='test@email.com')
        self.client.login(username='testuser', password='password')

        post_data = {
            'title': 'this is a test article',
            'slug': 'this-is-a-test-article',
            'related_sections-INITIAL_FORMS': 0,
            'related_sections-MAX_NUM_FORMS': 1000,
            'related_sections-MIN_NUM_FORMS': 0,
            'related_sections-TOTAL_FORMS': 0,
            'body-count': 1,
            'body-0-value': 'Hello',
            'body-0-deleted': False,
            'body-0-order': 1,
            'body-0-type': 'paragraph',
            'tags': 'love, war',
            'action-publish': 'Publish'
        }
        self.client.post(
            reverse('wagtailadmin_pages:add',
                    args=('core', 'articlepage', self.yourmind.id, )),
            post_data)
        post_data.update({
            'title': 'this is a test article2',
            'slug': 'this-is-a-test-article-2',
            'tags': 'peace, war',
        })
        self.client.post(
            reverse('wagtailadmin_pages:add',
                    args=('core', 'articlepage', self.yourmind.id, )),
            post_data)

        self.assertEquals(
            ArticlePage.objects.filter(tags__name='war').count(), 2)
        self.assertEquals(
            ArticlePage.objects.filter(tags__name='love').count(), 1)
        self.assertEquals(
            ArticlePage.objects.filter(tags__name='peace').count(), 1)

    def test_meta_data_tags(self):
        User.objects.create_superuser(
            username='testuser', password='password', email='test@email.com')
        self.client.login(username='testuser', password='password')

        post_data = {
            'title': 'this is a test article',
            'slug': 'this-is-a-test-article',
            'related_sections-INITIAL_FORMS': 0,
            'related_sections-MAX_NUM_FORMS': 1000,
            'related_sections-MIN_NUM_FORMS': 0,
            'related_sections-TOTAL_FORMS': 0,
            'body-count': 1,
            'body-0-value': 'Hello',
            'body-0-deleted': False,
            'body-0-order': 1,
            'body-0-type': 'paragraph',
            'metadata_tags': 'love, happiness',
            'action-publish': 'Publish'
        }
        self.client.post(
            reverse('wagtailadmin_pages:add',
                    args=('core', 'articlepage', self.yourmind.id, )),
            post_data)
        post_data.update({
            'title': 'this is a test article2',
            'slug': 'this-is-a-test-article-2',
            'metadata_tags': 'peace, happiness',
        })
        self.client.post(
            reverse('wagtailadmin_pages:add',
                    args=('core', 'articlepage', self.yourmind.id, )),
            post_data)

        self.assertEquals(
            ArticlePage.objects.filter(
                metadata_tags__name='happiness').count(), 2)
        self.assertEquals(
            ArticlePage.objects.filter(
                metadata_tags__name='love').count(), 1)
        self.assertEquals(
            ArticlePage.objects.filter(
                metadata_tags__name='peace').count(), 1)

    def test_social_media(self):

        User.objects.create_superuser(
            username='testuser', password='password', email='test@email.com')
        self.client.login(username='testuser', password='password')

        self.mk_article(
            self.yourmind, title="New article",
            social_media_title='media title',
            social_media_description='media description',)

        self.mk_article(
            self.yourmind, title="New article2",
            social_media_title='media title',
            social_media_image=self.image,)

        self.assertEquals(
            ArticlePage.objects.filter(
                social_media_title='media title').count(), 2)
        self.assertEquals(
            ArticlePage.objects.filter(
                social_media_description='media description').count(), 1)
        self.assertEquals(
            ArticlePage.objects.filter(
                social_media_image=self.image).count(), 1)

        response = self.client.get('/sections/your-mind/new-article/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'content= "media title"')

    def test_site_languages(self):
        self.english = SiteLanguage.objects.create(
            locale='en',
        )
        self.french = SiteLanguage.objects.create(
            locale='fr',
        )
        self.spanish = SiteLanguage.objects.create(
            locale='sp', is_active=False
        )
        response = self.client.get('/')
        self.assertContains(response, 'English')
        self.assertContains(response, 'français')
        self.assertNotContains(response, 'español')

    def test_signal_on_page_delete_removes_translations(self):
        spanish = SiteLanguage.objects.create(locale='es')

        section = self.mk_section(
            self.section_index, title="Section", slug="section")
        self.mk_section_translation(section, self.french)
        self.mk_section_translation(section, spanish)

        section_sub1 = self.mk_section(
            section, title='Section subsection')
        self.mk_section_translation(section_sub1, self.french)
        p1, p2 = self.mk_articles(section_sub1, 2)
        self.mk_article_translation(p1, self.french)
        self.mk_article_translation(p1, spanish)

        section_sub2 = self.mk_section(
            section, title='Section subsection')
        p3, p4 = self.mk_articles(section_sub2, 2)
        self.mk_article_translation(p4, self.french)

        p5, p6 = self.mk_articles(section, 2)
        self.mk_article_translation(p5, self.french)

        self.mk_section_translation(self.yourmind, self.french)
        self.mk_section_translation(self.yourmind_sub, self.french)

        p7, p8, p9 = self.mk_articles(self.yourmind_sub, 3)
        self.mk_article_translation(p7, self.french)
        self.mk_article_translation(p7, spanish)
        self.mk_article_translation(p8, self.french)
        sub_sec = self.mk_section(self.yourmind_sub, title='Sub sec')

        self.assertEqual(ArticlePage.objects.all().count(), 16)
        self.assertEqual(SectionPage.objects.all().count(), 11)
        self.assertEqual(PageTranslation.objects.all().count(), 12)

        section.delete()
        self.assertEqual(ArticlePage.objects.all().count(), 6)
        self.assertEqual(SectionPage.objects.all().count(), 5)
        self.assertEqual(PageTranslation.objects.all().count(), 5)

        p7.delete()
        self.assertEqual(ArticlePage.objects.all().count(), 3)
        self.assertEqual(SectionPage.objects.all().count(), 5)
        self.assertEqual(PageTranslation.objects.all().count(), 3)

        p9.delete()
        self.assertEqual(ArticlePage.objects.all().count(), 2)
        self.assertEqual(SectionPage.objects.all().count(), 5)
        self.assertEqual(PageTranslation.objects.all().count(), 3)

        sub_sec.delete()
        self.assertEqual(ArticlePage.objects.all().count(), 2)
        self.assertEqual(SectionPage.objects.all().count(), 4)
        self.assertEqual(PageTranslation.objects.all().count(), 3)

        self.yourmind_sub.delete()
        self.assertEqual(ArticlePage.objects.all().count(), 0)
        self.assertEqual(SectionPage.objects.all().count(), 2)
        self.assertEqual(PageTranslation.objects.all().count(), 1)

        self.yourmind.delete()
        self.assertEqual(ArticlePage.objects.all().count(), 0)
        self.assertEqual(SectionPage.objects.all().count(), 0)
        self.assertEqual(PageTranslation.objects.all().count(), 0)

    def test_get_translation_template_tag(self):
        section = self.mk_section(self.section_index)
        section2 = self.mk_section(self.section_index)
        translated_section = self.mk_section_translation(section, self.french)
        qs = get_translation({'locale_code': 'fr'}, section)
        self.assertEquals(translated_section.id, qs.id)
        qs = get_translation({'locale_code': 'fr'}, section2)
        self.assertEquals(section2.id, qs.id)

    def test_topic_of_the_day(self):
        User.objects.create_superuser(
            username='testuser', password='password', email='test@email.com')
        self.client.login(username='testuser', password='password')

        # create a new article and go to it's edit page
        new_section = self.mk_section(
            self.section_index, title="New Section", slug="new-section")
        new_article = self.mk_article(new_section, title="New article",)
        response = self.client.get(
            reverse('wagtailadmin_pages:edit', args=(new_article.id,)))
        self.assertEqual(response.status_code, 200)

        # Marking article as Topic of the day with no promote date
        # or demote date raises error
        post_data = {
            "feature_as_topic_of_the_day": True,
            'title': 'this is a test article',
            'slug': 'this-is-a-test-article',
            'related_sections-INITIAL_FORMS': 0,
            'related_sections-MAX_NUM_FORMS': 1000,
            'related_sections-MIN_NUM_FORMS': 0,
            'related_sections-TOTAL_FORMS': 0,
            'body-count': 1,
            'body-0-value': 'Hello',
            'body-0-deleted': False,
            'body-0-order': 1,
            'body-0-type': 'paragraph',
            'metadata_tags': 'love, happiness',
            'action-publish': 'Publish'
        }
        self.client.post(
            reverse('wagtailadmin_pages:edit', args=(new_article.id,)),
            post_data
        )
        self.assertRaisesMessage(
            ValidationError,
            "Please specify the date and time that you would like this "
            "article to appear as the Topic of the Day."
        )

        # Raises error if promote_date is in the past
        post_data.update({
            "promote_date": timezone.now() + timedelta(days=-1),
        })
        self.client.post(
            reverse('wagtailadmin_pages:edit', args=(new_article.id,)),
            post_data
        )
        self.assertRaisesMessage(
            ValidationError,
            "Please select the present date, or a future date."
        )

        # Raise error is demote date is before
        # promote date
        post_data.update({
            "promote_date": timezone.now(),
            "demote_date": timezone.now() + timedelta(days=-1)
        })
        self.client.post(
            reverse('wagtailadmin_pages:edit', args=(new_article.id,)),
            post_data
        )
        self.assertRaisesMessage(
            ValidationError,
            "The article cannot be demoted before it has been promoted."
        )

    def test_is_topic_of_the_day(self):
        promote_date = timezone.now() + timedelta(days=-1)
        demote_date = timezone.now() + timedelta(days=1)
        article_1 = ArticlePage(
            title="New article",
            feature_as_topic_of_the_day=True,
            promote_date=promote_date,
            demote_date=demote_date
        )
        self.assertTrue(article_1.is_current_topic_of_the_day())

        promote_date = timezone.now() + timedelta(days=2)
        demote_date = timezone.now() + timedelta(days=4)
        article_2 = ArticlePage(
            title="New article",
            promote_date=promote_date,
            demote_date=demote_date
        )
        self.assertFalse(article_2.is_current_topic_of_the_day())

    # exclude future-scheduled topic of the day articles from the
    # latest articles queryset.
    # Create two articles, one with present promote date and one
    # with future promote date. Verify that the article with a
    # future promote date does not appear in latest articles
    # queryset.
    def test_future_topic_of_the_day_not_in_latest(self):
        promote_date = timezone.now() + timedelta(days=2)
        demote_date = timezone.now() + timedelta(days=4)
        future_article = ArticlePage(
            title="Future article",
            promote_date=promote_date,
            demote_date=demote_date,
            depth="1",
            path="0003",
            featured_in_latest=True,
            feature_as_topic_of_the_day=True
        )
        future_article.save()
        self.assertQuerysetEqual(Main().latest_articles(), [])

        promote_date = timezone.now() + timedelta(days=-2)
        demote_date = timezone.now() + timedelta(days=-1)
        present_article = ArticlePage(
            title="Present article",
            promote_date=promote_date,
            demote_date=demote_date,
            depth="1",
            path="0004",
            featured_in_latest=True,
            feature_as_topic_of_the_day=True
        )
        present_article.save()
        self.assertQuerysetEqual(
            Main().latest_articles(), [repr(present_article), ])
