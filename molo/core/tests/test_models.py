import pytest
from datetime import datetime, timedelta
from django.test import TestCase

from molo.core.models import ArticlePage, SectionPage, LanguagePage, Page

from wagtail.wagtailimages.tests.utils import Image, get_test_image_file


@pytest.mark.django_db
class TestModels(TestCase):
    fixtures = ['molo/core/tests/fixtures/test.json']

    def test_article_order(self):
        now = datetime.now()
        article1 = ArticlePage.objects.get(pk=14)
        article1.first_published_at = now
        article1.save()

        article2 = ArticlePage.objects.get(pk=15)
        article2.first_published_at = now + timedelta(hours=1)
        article2.save()

        # most recent first
        section = SectionPage.objects.get(slug='your-mind-subsection')
        self.assertEquals(
            section.articles()[0].title, article1.title)

        # swap published date
        article1.first_published_at = now + timedelta(hours=4)
        article1.save()

        self.assertEquals(
            section.articles()[0].title, article1.title)

    def test_latest(self):
        lang = LanguagePage.objects.get(code='en')
        self.assertEquals(lang.latest_articles().count(), 4)

    def test_featured_homepage(self):
        section = SectionPage.objects.get(slug='your-mind')
        self.assertEquals(section.featured_articles_in_homepage().count(), 2)

    def test_latest_homepage(self):
        section = SectionPage.objects.get(slug='your-mind')
        self.assertEquals(section.latest_articles_in_homepage().count(), 2)

    def test_extra_css(self):
        main = Page.objects.get(slug='main')

        # extra_css set on current section
        new_section = SectionPage(
            title="New Section", slug="new-section",
            extra_style_hints='primary')
        main.add_child(instance=new_section)
        self.assertEquals(
            new_section.get_effective_extra_style_hints(), 'primary')

        # extra_css not set to use inherited value
        new_section2 = SectionPage(title="New Section 2", slug="new-section-2")
        new_section.add_child(instance=new_section2)
        self.assertEquals(
            new_section2.get_effective_extra_style_hints(), 'primary')

        # extra_css not set on either so should be blank
        new_section3 = SectionPage(title="New Section 3", slug="new-section-3")
        main.add_child(instance=new_section3)
        self.assertEquals(new_section3.get_effective_extra_style_hints(), '')

        # extra_css not set on child so should use parent value
        new_section4 = SectionPage(title="New Section 4", slug="new-section-4")
        new_section2.add_child(instance=new_section4)
        self.assertEquals(
            new_section4.get_effective_extra_style_hints(), 'primary')

        # extra_css is set on child so should use child value
        new_section5 = SectionPage(
            title="New Section 5", slug="new-section-5",
            extra_style_hints='secondary')
        new_section.add_child(instance=new_section5)
        self.assertEquals(
            new_section5.get_effective_extra_style_hints(), 'secondary')

    def setUp(self):
        # Create an image for running tests on
        self.image = Image.objects.create(
            title="Test image",
            file=get_test_image_file(),
        )

    def test_image(self):
        main = Page.objects.get(slug='main')
        new_section = SectionPage(
            title="New Section", slug="new-section",
            image=self.image)
        main.add_child(instance=new_section)
        self.assertEquals(
            new_section.get_effective_image(), self.image)

        # image not set to use inherited value
        new_section2 = SectionPage(title="New Section 2", slug="new-section-2")
        new_section.add_child(instance=new_section2)
        self.assertEquals(
            new_section2.get_effective_image(), new_section.image)

        # image not set to use inherited value
        new_section3 = SectionPage(title="New Section 3", slug="new-section-3")
        new_section2.add_child(instance=new_section3)
        self.assertEquals(
            new_section3.get_effective_image(), new_section.image)

    def test_parent_section(self):
        main = Page.objects.get(slug='main')
        new_section = SectionPage(
            title="New Section", slug="new-section")
        main.add_child(instance=new_section)
        new_section1 = SectionPage(title="New Section 1", slug="new-section-1")
        new_section.add_child(instance=new_section1)
        self.assertEquals(
            new_section1.get_parent_section(), new_section)
