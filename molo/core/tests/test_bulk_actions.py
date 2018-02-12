# -*- coding: utf-8 -*-
import pytest
import datetime

from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings

from molo.core.tests.base import MoloTestCaseMixin

from molo.core.models import (
    SiteLanguageRelation, Languages, ArticlePage, ArticlePageTags,
    SectionPage)

from pytz import UTC


@pytest.mark.django_db
@override_settings(GOOGLE_ANALYTICS={}, CELERY_ALWAYS_EAGER=True)
class TestCopyBulkAction(TestCase, MoloTestCaseMixin):

    def setUp(self):
        # make main one with section and sub section with fr translations
        self.mk_main()
        self.english = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(self.main.get_site()),
            locale='en',
            is_active=True)

        self.french = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(self.main.get_site()),
            locale='fr',
            is_active=True)

        self.yourmind = self.mk_section(
            self.section_index, title='Your mind', slug='yourmind')
        self.yourmind_sub = self.mk_section(
            self.yourmind, title='Your mind subsection')

        self.yourmind_fr = self.mk_section_translation(
            self.yourmind, self.french, title='Your mind in french',
            slug='yourmind_fr')
        self.yourmind_sub_fr = self.mk_section_translation(
            self.yourmind_sub, self.french,
            title='Your mind subsection in french')

        # make main 2 with different section to main 1
        self.mk_main2()
        self.language_setting2 = Languages.objects.create(
            site_id=self.main2.get_site().pk)
        self.english2 = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting2,
            locale='en',
            is_active=True)
        self.french2 = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting2,
            locale='fr',
            is_active=True)
        self.yourmind2 = self.mk_section(
            self.section_index2, title='Your mind', slug='yourmind')
        self.yourmind_sub2 = self.mk_section(
            self.yourmind2, title='Your mind subsection2')
        self.yourmind_fr2 = self.mk_section_translation(
            self.yourmind2, self.french2, title='Your mind in french',
            slug='yourmind_fr')

        # create main 3 with nothing
        self.mk_main3()

    def test_copy_to_all(self):
        # Login
        self.user = self.login()
        # create article in main 1 with translation page
        article = self.mk_articles(self.yourmind, 1)[0]
        translated_article = self.mk_article_translation(
            article, self.french,
            title=article.title + ' in french',
            subtitle=article.subtitle + ' in french')

        # create tags in main 1 and link them to the article in main 1
        tag = self.mk_tag(parent=self.tag_index, slug='tag')
        tag.save_revision().publish()
        tag2 = self.mk_tag(parent=self.tag_index2, slug='tag')
        tag2.save_revision().publish()
        tag3 = self.mk_tag(parent=self.tag_index3, slug='tag')
        tag3.save_revision().publish()
        ArticlePageTags.objects.create(page=article, tag=tag)

        # assert the article does not exist in main 2 or main 3
        self.assertFalse(ArticlePage.objects.descendant_of(
            self.main2).filter(slug=article.slug).exists())
        self.assertFalse(ArticlePage.objects.descendant_of(
            self.main3).filter(slug=article.slug).exists())
        self.assertFalse(ArticlePage.objects.descendant_of(
            self.main2).filter(slug=translated_article.slug).exists())
        self.assertFalse(ArticlePage.objects.descendant_of(
            self.main3).filter(slug=translated_article.slug).exists())

        # copy the article to all the sites
        self.client.post(reverse('copy-to-all', args=(article.id,)))

        # assert that it now exists in main 2 and not main 3
        self.assertTrue(ArticlePage.objects.descendant_of(
            self.main2).filter(slug=article.slug).exists())
        self.assertFalse(ArticlePage.objects.descendant_of(
            self.main3).filter(slug=article.slug).exists())
        self.assertTrue(ArticlePage.objects.descendant_of(
            self.main2).filter(slug=translated_article.slug).exists())
        self.assertFalse(ArticlePage.objects.descendant_of(
            self.main3).filter(slug=translated_article.slug).exists())

        # check that the linked tags have now been linked to the new tags
        article_2 = ArticlePage.objects.descendant_of(
            self.main2).get(slug=article.slug)
        self.assertTrue(ArticlePageTags.objects.filter(
            page=article_2, tag=tag2).exists())

        # copying the article to all the sites again should not
        # copy to site 2 again as the article already exists there now
        self.client.post(reverse('copy-to-all', args=(article.id,)))

        # assert that only exists once in site 2 and not in site 3
        self.assertEquals(ArticlePage.objects.descendant_of(
            self.main2).filter(slug=article.slug).count(), 1)
        self.assertFalse(ArticlePage.objects.descendant_of(
            self.main3).filter(slug=article.slug).exists())

        # make sure the slug of all the section indexes are the same
        self.section_index3.slug = self.section_index.slug
        self.section_index3.save_revision().publish()
        self.section_index2.slug = self.section_index.slug
        self.section_index2.save_revision().publish()

        # now copy the yourmind section to all sites
        self.client.post(reverse('copy-to-all', args=(self.yourmind.id,)))

        # it should copy the section, the translations, and all the child pages
        self.assertTrue(SectionPage.objects.descendant_of(
            self.main3).filter(slug=self.yourmind.slug).exists())
        self.assertTrue(ArticlePage.objects.descendant_of(
            self.main3).filter(slug=translated_article.slug).exists())
        self.assertTrue(ArticlePage.objects.descendant_of(
            self.main3).filter(slug=article.slug).exists())
        self.assertTrue(SectionPage.objects.descendant_of(
            self.main3).filter(slug=self.yourmind_fr.slug).exists())

        # it should copy the article relations too
        article_3 = ArticlePage.objects.descendant_of(
            self.main3).get(slug=article.slug)
        self.assertTrue(ArticlePageTags.objects.filter(
            page=article_3, tag=tag3).exists())

    def test_copy_to_all_scheduled_page(self):
        self.user = self.login()

        date = datetime.datetime(2019, 3, 10, 17, 0, tzinfo=UTC)
        article = ArticlePage(
            title='article 1', slug='article1', go_live_at=date, live=False)
        self.yourmind.add_child(instance=article)
        article.save_revision().publish()

        tag = self.mk_tag(parent=self.tag_index, slug='tag')
        tag.save_revision().publish()
        tag2 = self.mk_tag(parent=self.tag_index2, slug='tag')
        tag2.save_revision().publish()
        ArticlePageTags.objects.create(page=article, tag=tag)
        article.refresh_from_db()

        self.assertEquals(article.status_string, 'scheduled')

        self.client.post(reverse('copy-to-all', args=(article.id,)))
        new_article = ArticlePage.objects.descendant_of(
            self.main2).get(slug=article.slug)
        self.assertEquals(new_article.status_string, 'scheduled')
