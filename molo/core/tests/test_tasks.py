from datetime import datetime, timedelta

from json import dumps
import pytest
from django.test import TestCase

from molo.core.models import SiteLanguage, FooterPage, ArticlePage, Main
from molo.core.tests.base import MoloTestCaseMixin
from molo.core.tasks import rotate_content, demote_articles, promote_articles
from molo.core.templatetags.core_tags import \
    load_descendant_articles_for_section

from wagtail.wagtailcore.models import Site
from wagtail.contrib.settings.context_processors import SettingsProxy


@pytest.mark.django_db
class TestTasks(TestCase, MoloTestCaseMixin):

    def setUp(self):
        # Creates Main language
        self.english = SiteLanguage.objects.create(
            locale='en',
        )
        self.mk_main()

        self.yourmind = self.mk_section(
            self.section_index, title='Your mind')
        self.yourmind_sub = self.mk_section(
            self.yourmind, title='Your mind subsection')
        self.yourmind_sub2 = self.mk_section(
            self.yourmind, title='Your mind subsection2')
        self.yourmind_sub3 = self.mk_section(
            self.yourmind, title='Your mind subsection3')

    def test_order_by_promote_date_latest(self):
        article = self.mk_article(
            self.yourmind, title='article', slug='article')
        article.featured_in_latest_start_date = datetime.now()
        article.save()
        article2 = self.mk_article(
            self.yourmind, title='article2', slug='article2')
        article2.featured_in_latest_start_date = datetime.now()
        article2.save()
        article3 = self.mk_article(
            self.yourmind, title='article3', slug='article3')
        article3.featured_in_latest_start_date = datetime.now()
        article3.save()
        demote_articles()
        promote_articles()
        latest_articles = Main.objects.all().first().latest_articles()
        self.assertEquals(latest_articles[0].title, 'article3')
        article2.featured_in_latest_start_date = datetime.now()
        article2.save()
        demote_articles()
        promote_articles()
        latest_articles = Main.objects.all().first().latest_articles()
        self.assertEquals(latest_articles[0].title, 'article2')

    def test_order_by_promote_date_homepage(self):
        article = self.mk_article(
            self.yourmind, title='article', slug='article')
        article.featured_in_homepage_start_date = datetime.now()
        article.save()
        article2 = self.mk_article(
            self.yourmind, title='article2', slug='article2')
        article2.featured_in_homepage_start_date = datetime.now()
        article2.save()
        article3 = self.mk_article(
            self.yourmind, title='article3', slug='article3')
        article3.featured_in_homepage_start_date = datetime.now()
        article3.save()
        demote_articles()
        promote_articles()
        homepage_articles = load_descendant_articles_for_section(
            {}, self.yourmind, featured_in_homepage=5)
        self.assertEquals(homepage_articles[0].title, 'article3')
        article2.featured_in_homepage_start_date = datetime.now()
        article2.save()
        demote_articles()
        promote_articles()
        homepage_articles = load_descendant_articles_for_section(
            {}, self.yourmind, featured_in_homepage=5)
        self.assertEquals(homepage_articles[0].title, 'article2')

    def test_order_by_promote_date_section(self):
        article = self.mk_article(
            self.yourmind, title='article', slug='article')
        article.featured_in_section_start_date = datetime.now()
        article.save()
        article2 = self.mk_article(
            self.yourmind, title='article2', slug='article2')
        article2.featured_in_section_start_date = datetime.now()
        article2.save()
        article3 = self.mk_article(
            self.yourmind, title='article3', slug='article3')
        article3.featured_in_section_start_date = datetime.now()
        article3.save()
        demote_articles()
        promote_articles()
        section_articles = load_descendant_articles_for_section(
            {}, self.yourmind, featured_in_section=5)
        self.assertEquals(section_articles[0].title, 'article3')
        article2.featured_in_section_start_date = datetime.now()
        article2.save()
        demote_articles()
        promote_articles()
        section_articles = load_descendant_articles_for_section(
            {}, self.yourmind, featured_in_section=5)
        self.assertEquals(section_articles[0].title, 'article2')

    def test_promote_articles_latest(self):
        article = self.mk_article(
            self.yourmind, title='article', slug='article')
        article.featured_in_latest_start_date = datetime.now()
        article.save()
        demote_articles()
        promote_articles()
        article = ArticlePage.objects.all().first()
        self.assertTrue(article.featured_in_latest)

    def test_demote_articles_latest(self):
        article = self.mk_article(
            self.yourmind, title='article', slug='article')
        article.featured_in_latest_start_date = datetime.now()
        article.save()
        demote_articles()
        promote_articles()
        article = ArticlePage.objects.all().first()
        self.assertTrue(article.featured_in_latest)
        article.featured_in_latest_end_date = datetime.now()
        article.save()
        demote_articles()
        promote_articles()
        article = ArticlePage.objects.all().first()
        self.assertFalse(article.featured_in_latest)

    def test_promote_articles_homepage(self):
        article = self.mk_article(
            self.yourmind, title='article', slug='article')
        article.featured_in_homepage_start_date = datetime.now()
        article.save()
        demote_articles()
        promote_articles()
        article = ArticlePage.objects.all().first()
        self.assertTrue(article.featured_in_homepage)

    def test_demote_articles_homepage(self):
        article = self.mk_article(
            self.yourmind, title='article', slug='article')
        article.featured_in_homepage_start_date = datetime.now()
        article.save()
        demote_articles()
        promote_articles()
        article = ArticlePage.objects.all().first()
        self.assertTrue(article.featured_in_homepage)
        article.featured_in_homepage_end_date = datetime.now()
        article.save()
        demote_articles()
        promote_articles()
        article = ArticlePage.objects.all().first()
        self.assertFalse(article.featured_in_homepage)

    def test_promote_articles_section(self):
        article = self.mk_article(
            self.yourmind, title='article', slug='article')
        article.featured_in_section_start_date = datetime.now()
        article.save()
        demote_articles()
        promote_articles()
        article = ArticlePage.objects.all().first()
        self.assertTrue(article.featured_in_section)

    def test_demote_articles_section(self):
        article = self.mk_article(
            self.yourmind, title='article', slug='article')
        article.featured_in_section_start_date = datetime.now()
        article.save()
        demote_articles()
        promote_articles()
        article = ArticlePage.objects.all().first()
        self.assertTrue(article.featured_in_section)
        article.featured_in_section_end_date = datetime.now()
        article.save()
        demote_articles()
        promote_articles()
        article = ArticlePage.objects.all().first()
        self.assertFalse(article.featured_in_section)

    def test_latest_rotation_on(self):
        """This test that if the date range, weekdays and times are set for
        content rotation, that the content rotates accordingly"""
        # sets the site settings
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        site_settings = settings['core']['SiteSettings']

        site_settings.content_rotation_start_date = datetime.now()
        site_settings.content_rotation_end_date = datetime.now() + timedelta(
            days=1)
        time1 = str(datetime.now().time())[:8]
        time2 = str((datetime.now() + timedelta(minutes=1)).time())[:8]
        site_settings.time = dumps([{
            'type': 'time', 'value': time1}, {'type': 'time', 'value': time2}])
        site_settings.monday_rotation = True
        site_settings.save()

        # creates articles and pages, some set to feature in latest, others not
        for i in range(5):
            self.footer = FooterPage(
                title='Footer Page %s', slug='footer-page-%s' % (i, ))
            self.footer_index.add_child(instance=self.footer)

        self.assertEquals(FooterPage.objects.live().count(), 5)
        self.assertEquals(self.main.latest_articles().count(), 0)

        self.mk_articles(
            self.yourmind_sub, count=10,
            featured_in_latest_start_date=datetime.now())
        promote_articles()
        self.mk_articles(self.yourmind_sub, count=10, featured_in_latest=False)
        self.assertEquals(self.main.latest_articles().count(), 10)
        # gets the first and last articles of the list before it rotates
        first_article_old = self.main.latest_articles()[0].pk
        last_article_old = self.main.latest_articles()[9].pk

        rotate_content(day=0)

        # checks to see that the number of latest articles has not increased
        self.assertEquals(self.main.latest_articles().count(), 10)
        # checks to see the the old first articles is not still the first one
        self.assertNotEquals(
            first_article_old, self.main.latest_articles()[0].pk)
        # checks to see the old first article has moved up 2 places
        self.assertEquals(
            first_article_old, self.main.latest_articles()[2].pk)
        # checks to see the the old last article is not still last
        self.assertNotEquals(
            last_article_old, self.main.latest_articles()[8].pk)

    def test_latest_rotation_on_draft_articles(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        site_settings = settings['core']['SiteSettings']

        site_settings.content_rotation_start_date = datetime.now()
        site_settings.content_rotation_end_date = datetime.now() + timedelta(
            days=1)
        time1 = str(datetime.now().time())[:8]
        time2 = str((datetime.now() + timedelta(minutes=1)).time())[:8]
        site_settings.time = dumps([{
            'type': 'time', 'value': time1}, {'type': 'time', 'value': time2}])
        site_settings.monday_rotation = True
        site_settings.save()

        article = self.mk_article(
            self.yourmind, title='article', slug='article')
        article.featured_in_latest_start_date = datetime.now()
        article.save()
        article2 = self.mk_article(
            self.yourmind, title='article2', slug='article2')
        article2.featured_in_latest_start_date = datetime.now()
        article2.save()

        article3 = self.mk_article(
            self.yourmind, title='article3', slug='article3')
        article3.save()

        promote_articles()

        article.refresh_from_db()
        article2.refresh_from_db()
        article3.refresh_from_db()
        self.assertTrue(article.live)
        self.assertTrue(article2.live)
        self.assertTrue(article3.live)

        article.unpublish()
        article.refresh_from_db()
        self.assertTrue(article.featured_in_latest)
        self.assertTrue(article2.featured_in_latest)
        self.assertFalse(article3.featured_in_latest)

        rotate_content(0)
        article.refresh_from_db()
        article2.refresh_from_db()
        article3.refresh_from_db()
        self.assertFalse(article.live)
        self.assertTrue(article2.live)
        self.assertTrue(article3.live)

    def test_latest_rotation_no_valid_days(self):
        """This test that if the date range and times are set for
        content rotation, that it doesn't rotate without any weekdays set"""
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        site_settings = settings['core']['SiteSettings']
        site_settings.monday_rotation = True
        site_settings.content_rotation_start_date = datetime.now()
        site_settings.content_rotation_end_date = datetime.now() + timedelta(
            days=1)
        time1 = str(datetime.now().time())[:8]
        time2 = str((datetime.now() + timedelta(minutes=1)).time())[:8]
        site_settings.time = dumps([{
            'type': 'time', 'value': time1}, {'type': 'time', 'value': time2}])
        site_settings.save()

        for i in range(5):
            self.footer = FooterPage(
                title='Footer Page %s', slug='footer-page-%s' % (i, ))
            self.footer_index.add_child(instance=self.footer)

        self.assertEquals(FooterPage.objects.live().count(), 5)
        self.assertEquals(self.main.latest_articles().count(), 0)

        self.mk_articles(
            self.yourmind_sub, count=10,
            featured_in_latest_start_date=datetime.now())
        promote_articles()
        self.mk_articles(self.yourmind_sub, count=10, featured_in_latest=False)
        self.assertEquals(self.main.latest_articles().count(), 10)
        first_article_old = self.main.latest_articles()[0].pk
        last_article_old = self.main.latest_articles()[9].pk
        rotate_content(4)
        self.assertEquals(first_article_old, self.main.latest_articles()[0].pk)
        self.assertEquals(last_article_old, self.main.latest_articles()[9].pk)

    def test_latest_rotation_no_time(self):
        """This test that if the date range and weekdays are set for
        content rotation, that the content doesn't rotates with no times set"""
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        site_settings = settings['core']['SiteSettings']
        site_settings.monday_rotation = True
        site_settings.content_rotation_start_date = datetime.now()
        site_settings.content_rotation_end_date = datetime.now() + timedelta(
            days=1)
        site_settings.save()

        for i in range(5):
            self.footer = FooterPage(
                title='Footer Page %s', slug='footer-page-%s' % (i, ))
            self.footer_index.add_child(instance=self.footer)

        self.assertEquals(FooterPage.objects.live().count(), 5)
        self.assertEquals(self.main.latest_articles().count(), 0)

        self.mk_articles(
            self.yourmind_sub, count=10,
            featured_in_latest_start_date=datetime.now())
        promote_articles()
        self.mk_articles(self.yourmind_sub, count=10, featured_in_latest=False)
        self.assertEquals(self.main.latest_articles().count(), 10)
        first_article_old = self.main.latest_articles()[0].pk
        last_article_old = self.main.latest_articles()[9].pk
        rotate_content(0)
        self.assertEquals(first_article_old, self.main.latest_articles()[0].pk)
        self.assertEquals(last_article_old, self.main.latest_articles()[9].pk)

    def test_latest_rotation_no_start_or_end_date(self):
        """This test that if the weekdays and times are set for
        content rotation, that the content doesn't rotates with no dates set"""
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        site_settings = settings['core']['SiteSettings']
        site_settings.monday_rotation = True
        site_settings.tuesday_rotation = True
        site_settings.wednesday_rotation = True
        site_settings.thursday_rotation = True
        site_settings.friday_rotation = True
        site_settings.saturday_rotation = True
        site_settings.sunday_rotation = True
        site_settings.save()

        for i in range(5):
            self.footer = FooterPage(
                title='Footer Page %s', slug='footer-page-%s' % (i, ))
            self.footer_index.add_child(instance=self.footer)

        self.assertEquals(FooterPage.objects.live().count(), 5)
        self.assertEquals(self.main.latest_articles().count(), 0)

        self.mk_articles(
            self.yourmind_sub, count=10,
            featured_in_latest_start_date=datetime.now())
        promote_articles()
        self.mk_articles(self.yourmind_sub, count=10, featured_in_latest=False)
        self.assertEquals(self.main.latest_articles().count(), 10)
        first_article_old = self.main.latest_articles()[0].pk
        last_article_old = self.main.latest_articles()[9].pk
        rotate_content()
        self.assertEquals(first_article_old, self.main.latest_articles()[0].pk)
        self.assertEquals(last_article_old, self.main.latest_articles()[9].pk)

    def test_homepage_rotation(self):

        def get_featured_articles(section):
            return section.featured_in_homepage_articles()

        non_rotating_articles = self.mk_articles(
            self.yourmind, count=3, featured_in_homepage=False)
        rotate_content()
        for article in non_rotating_articles:
            self.assertFalse(article.featured_in_latest)
        self.assertEquals(get_featured_articles(self.yourmind).count(), 0)
        self.mk_articles(
            self.yourmind_sub, count=10,
            featured_in_homepage_start_date=datetime.now())
        promote_articles()
        self.mk_articles(
            self.yourmind_sub, count=10, featured_in_homepage=False)
        self.assertEquals(
            get_featured_articles(self.yourmind_sub).count(), 10)
        first_article_old = get_featured_articles(self.yourmind_sub)[0].pk
        last_article_old = get_featured_articles(self.yourmind_sub)[9].pk
        self.yourmind_sub.content_rotation_start_date = datetime.now()
        self.yourmind_sub.content_rotation_end_date = datetime.now() + \
            timedelta(days=1)
        time1 = str(datetime.now().time())[:8]
        time2 = str((datetime.now() + timedelta(minutes=1)).time())[:8]
        self.yourmind_sub.time = dumps([{
            'type': 'time', 'value': time1}, {'type': 'time', 'value': time2}])
        self.yourmind_sub.monday_rotation = True
        self.yourmind_sub.tuesday_rotation = True
        self.yourmind_sub.wednesday_rotation = True
        self.yourmind_sub.thursday_rotation = True
        self.yourmind_sub.friday_rotation = True
        self.yourmind_sub.saturday_rotation = True
        self.yourmind_sub.sunday_rotation = True
        self.yourmind_sub.save_revision().publish()
        rotate_content()
        self.assertEquals(
            get_featured_articles(self.yourmind_sub).count(), 10)
        self.assertNotEquals(
            first_article_old, get_featured_articles(self.yourmind_sub)[0].pk)
        self.assertEquals(
            first_article_old, get_featured_articles(self.yourmind_sub)[2].pk)
        self.assertNotEquals(
            last_article_old, get_featured_articles(self.yourmind_sub)[9].pk)

    def test_homepage_rotation_subcategories(self):

        def get_featured_articles(section):
            return section.featured_in_homepage_articles()

        non_rotating_articles = self.mk_articles(
            self.yourmind_sub, count=3, featured_in_homepage=False)
        rotate_content()
        for article in non_rotating_articles:
            self.assertFalse(article.featured_in_latest)
        self.assertEquals(get_featured_articles(self.yourmind).count(), 0)
        self.mk_articles(
            self.yourmind_sub2, count=5,
            featured_in_homepage_start_date=datetime.now())
        self.mk_articles(
            self.yourmind_sub3, count=5,
            featured_in_homepage_start_date=datetime.now())
        promote_articles()
        self.mk_articles(
            self.yourmind_sub, count=10, featured_in_homepage=False)
        self.mk_articles(
            self.yourmind_sub2, count=10, featured_in_homepage=False)
        self.mk_articles(
            self.yourmind_sub3, count=10, featured_in_homepage=False)
        self.assertEquals(
            get_featured_articles(self.yourmind_sub).count(), 0)
        self.assertEquals(
            get_featured_articles(self.yourmind_sub2).count(), 5)
        self.assertEquals(
            get_featured_articles(self.yourmind_sub3).count(), 5)
        self.yourmind_sub.content_rotation_start_date = datetime.now()
        self.yourmind_sub.content_rotation_end_date = datetime.now() + \
            timedelta(days=1)
        time1 = str(datetime.now().time())[:8]
        time2 = str((datetime.now() + timedelta(minutes=1)).time())[:8]
        self.yourmind_sub.time = dumps([{
            'type': 'time', 'value': time1}, {'type': 'time', 'value': time2}])
        self.yourmind_sub.monday_rotation = True
        self.yourmind_sub.tuesday_rotation = True
        self.yourmind_sub.wednesday_rotation = True
        self.yourmind_sub.thursday_rotation = True
        self.yourmind_sub.friday_rotation = True
        self.yourmind_sub.saturday_rotation = True
        self.yourmind_sub.sunday_rotation = True
        self.yourmind_sub.save_revision().publish()
        rotate_content()
        self.assertEquals(
            ArticlePage.objects.live().filter(
                featured_in_homepage=True).count(), 10)
        self.assertTrue(ArticlePage.objects.live().filter(
            featured_in_homepage=True).child_of(self.yourmind_sub).exists())
