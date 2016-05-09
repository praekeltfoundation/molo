from datetime import *

import pytest
from django.test import TestCase


from molo.core.models import SiteSettings
from molo.core.tests.base import MoloTestCaseMixin
from testapp.tasks import rotate_content
from wagtail.wagtailimages.models import Image
from wagtail.wagtailimages.tests.utils import get_test_image_file


@pytest.mark.django_db
class TestTasks(TestCase, MoloTestCaseMixin):

    def setUp(self):
        # Create an image for running tests on
        self.image = Image.objects.create(
            title="Test image",
            file=get_test_image_file(),
        )

        self.mk_main()
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
        SiteSettings.content_rotation = True
        d = datetime.now()
        hour = d.hour + d.minute / 60. + d.second / 3600.
        SiteSettings.content_rotation_time = hour
        rotate_content()

        self.assertEquals(self.english.latest_articles().count(), 10)
        self.assertNotEquals(first_article_old, self.english.latest_articles()[0].pk)
        self.assertEquals(first_article_old, self.english.latest_articles()[1].pk)
        self.assertNotEquals(last_article_old, self.english.latest_articles()[9].pk)
        self.assertEquals(second_last_article_old, self.english.latest_articles()[9].pk)
