from datetime import *

import pytest
from django.test import TestCase


from molo.core.models import SiteLanguage, FooterPage, ArticlePage
from molo.core.tests.base import MoloTestCaseMixin

from molo.core.tasks import rotate_content

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

    def test_latest_rotation(self):
        self.footer = FooterPage(title='Footer Page', slug='footer-page')
        self.footer_index.add_child(instance=self.footer)
        self.mk_articles(self.yourmind_sub, count=10, featured_in_latest=True)
        self.mk_articles(self.yourmind_sub, count=10, featured_in_latest=False)
        self.assertEquals(self.main.latest_articles().count(), 10)
        first_article_old = self.main.latest_articles()[0].pk
        second_last_article_old = self.main.latest_articles()[8].pk
        last_article_old = self.main.latest_articles()[9].pk

        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        site_settings = settings['core']['SiteSettings']

        site_settings.content_rotation = True
        d = datetime.now()
        site_settings.content_rotation_time = d.hour
        site_settings.save()
        rotate_content()

        self.assertIsInstance(self.main.latest_articles()[0], ArticlePage)
        self.assertEquals(self.main.latest_articles().count(), 10)
        self.assertNotEquals(
            first_article_old, self.main.latest_articles()[0].pk)
        self.assertEquals(
            first_article_old, self.main.latest_articles()[1].pk)
        self.assertNotEquals(
            last_article_old, self.main.latest_articles()[9].pk)
        self.assertEquals(
            second_last_article_old, self.main.latest_articles()[9].pk)
