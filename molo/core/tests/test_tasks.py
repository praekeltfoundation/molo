from datetime import *

import pytest
from django.test import TestCase


from molo.core.models import LanguagePage
from molo.core.tests.base import MoloTestCaseMixin

from molo.core.tasks import rotate_content

from wagtail.wagtailimages.models import Image
from wagtail.wagtailimages.tests.utils import get_test_image_file
from wagtail.wagtailcore.models import Site
from wagtail.contrib.settings.context_processors import SettingsProxy


@pytest.mark.django_db
class TestTasks(TestCase, MoloTestCaseMixin):

    def setUp(self):
        # Create an image for running tests on
        self.image = Image.objects.create(
            title="Test image",
            file=get_test_image_file(),
        )

        self.mk_main()

        self.french = LanguagePage(
            title='French',
            code='fr',
            slug='french')
        self.main.add_child(instance=self.french)
        self.french.save_revision().publish()

        self.yourmind = self.mk_section(
            self.english, title='Your mind')
        self.yourmind_sub = self.mk_section(
            self.yourmind, title='Your mind subsection')

    def test_latest_rotation(self):
        self.mk_articles(self.yourmind_sub, count=10, featured_in_latest=True)
        self.mk_articles(self.yourmind_sub, count=10, featured_in_latest=False)
        self.assertEquals(self.english.latest_articles().count(), 10)
        first_article_old = self.english.latest_articles()[0].pk
        second_last_article_old = self.english.latest_articles()[8].pk
        last_article_old = self.english.latest_articles()[9].pk

        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        site_settings = settings['core']['SiteSettings']

        site_settings.content_rotation = True
        d = datetime.now()
        site_settings.content_rotation_time = d.hour
        site_settings.save()
        rotate_content()

        self.assertEquals(self.english.latest_articles().count(), 10)
        self.assertNotEquals(
            first_article_old, self.english.latest_articles()[0].pk)
        self.assertEquals(
            first_article_old, self.english.latest_articles()[1].pk)
        self.assertNotEquals(
            last_article_old, self.english.latest_articles()[9].pk)
        self.assertEquals(
            second_last_article_old, self.english.latest_articles()[9].pk)

        self.yourmind_fr = self.mk_section(
            self.french, title='Your mind french')
        self.yourmind_sub_fr = self.mk_section(
            self.yourmind_fr, title='Your mind subsection french')

        self.mk_articles(
            self.yourmind_sub_fr, count=10, featured_in_latest=True)
        self.mk_articles(
            self.yourmind_sub_fr, count=10, featured_in_latest=False)
        self.assertEquals(self.french.latest_articles().count(), 10)
        first_article_old = self.french.latest_articles()[0].pk
        second_last_article_old = self.french.latest_articles()[8].pk
        last_article_old = self.french.latest_articles()[9].pk

        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        site_settings = settings['core']['SiteSettings']

        site_settings.content_rotation = True
        d = datetime.now()
        site_settings.content_rotation_time = d.hour
        site_settings.save()
        rotate_content()

        self.assertEquals(self.french.latest_articles().count(), 10)
        self.assertNotEquals(
            first_article_old, self.french.latest_articles()[0].pk)
        self.assertEquals(
            first_article_old, self.french.latest_articles()[1].pk)
        self.assertNotEquals(
            last_article_old, self.french.latest_articles()[9].pk)
        self.assertEquals(
            second_last_article_old, self.french.latest_articles()[9].pk)
