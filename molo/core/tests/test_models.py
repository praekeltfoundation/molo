# coding=utf-8
import pytest
from django.test import TestCase, RequestFactory, Client
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType

from mock import patch

from molo.core.models import (
    ArticlePage, CmsSettings, Main,
    SiteLanguageRelation, Languages, SectionIndexPage, FooterIndexPage,
    BannerIndexPage, TagIndexPage, BannerPage,
    Timezone, Tag, ArticlePageTags, Site, LanguageRelation
)
from molo.core import constants
from molo.core.templatetags.core_tags import (
    load_child_articles_for_section,
    get_translation)
from molo.core.molo_wagtail_models import MoloPage
from molo.core.tests.base import MoloTestCaseMixin
from molo.core.tasks import promote_articles
from molo.core.wagtail_hooks import copy_translation_pages
from wagtail.images.tests.utils import Image, get_test_image_file


@pytest.mark.django_db
class TestModels(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.factory = RequestFactory()
        self.main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)

        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en', is_active=True)

        LanguageRelation.objects.create(
            page=self.main, language=self.english)

        self.french = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='fr', is_active=True)

        LanguageRelation.objects.create(
            page=self.main, language=self.french)

        LanguageRelation.objects.create(
            page=self.main, language=self.english)

        LanguageRelation.objects.create(
            page=self.banner_index, language=self.english)

        LanguageRelation.objects.create(
            page=self.tag_index, language=self.english)

        # Create an image for running tests on
        self.image = Image.objects.create(
            title="Test image",
            file=get_test_image_file(),
        )

        self.yourmind = self.mk_section(
            self.section_index, title='Your mind')
        self.yourmind_sub = self.mk_section(
            self.yourmind, title='Your mind subsection')

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

        LanguageRelation.objects.create(
            page=self.main2, language=self.english2)

        LanguageRelation.objects.create(
            page=self.main2, language=self.spanish)

        # Create an image for running tests on
        self.image = Image.objects.create(
            title="Test image",
            file=get_test_image_file(),
        )
        self.image2 = Image.objects.create(
            title="Test image 2",
            file=get_test_image_file(),
        )

        self.yourmind2 = self.mk_section(
            self.section_index2, title='Your mind')
        self.yourmind_sub2 = self.mk_section(
            self.yourmind2, title='Your mind subsection')

        self.client = Client()
        self.client.get("/")
        self.site = self.main.get_site()

    def test_multisite_one_root_page(self):
        second_site = Site.objects.create(
            hostname='kaios.mr.com', port=80, root_page=self.main,
            is_default_site=False, site_name='kaios main')
        self.assertEqual(self.main.get_site().pk, second_site.pk)

    def test_copy_method_of_article_page_copies_over_languages(self):
        self.assertFalse(
            Languages.for_site(
                self.main2.get_site()).languages.filter(locale='fr').exists())
        article = self.mk_articles(self.yourmind, 1)[0]

        LanguageRelation.objects.create(
            page=article, language=self.english2)

        self.mk_article_translation(article, self.french)
        article2 = article.copy(to=self.yourmind2)
        copy_translation_pages(article, article2)
        self.assertTrue(
            Languages.for_site(
                self.main2.get_site()).languages.filter(locale='fr').exists())
        self.assertFalse(
            Languages.for_site(
                self.main2.get_site()).languages.filter(
                locale='fr').first().is_active)

    def test_move_method_of_article_page_copies_over_languages(self):
        self.assertFalse(
            Languages.for_site(
                self.main2.get_site()).languages.filter(locale='fr').exists())
        article = self.mk_articles(self.yourmind, 1)[0]
        fr_article = self.mk_article_translation(article, self.french)
        fr_article.move(self.yourmind2)
        self.assertTrue(
            Languages.for_site(
                self.main2.get_site()).languages.filter(locale='fr').exists())
        self.assertFalse(
            Languages.for_site(
                self.main2.get_site()).languages.filter(
                locale='fr').first().is_active)

    def test_sections_method_of_main_gives_children_of_main_only(self):
        sections = self.main.sections()
        self.assertFalse(sections.child_of(self.main2).exists())

    @pytest.mark.django_db(transaction=True)
    def test_copy_method_of_section_index_wont_duplicate_index_pages(self):
        LanguageRelation.objects.create(
            page=SectionIndexPage.objects.child_of(self.main2).first(),
            language=self.spanish)
        self.assertEqual(
            SectionIndexPage.objects.child_of(self.main2).count(), 1)
        self.section_index.copy(to=self.main2)
        self.assertEqual(
            SectionIndexPage.objects.child_of(self.main2).count(), 1)

    @pytest.mark.django_db(transaction=True)
    def test_copy_method_of_tag_index_wont_duplicate_index_pages(self):
        LanguageRelation.objects.create(
            page=TagIndexPage.objects.child_of(self.main2).first(),
            language=self.spanish)
        self.assertEqual(
            TagIndexPage.objects.child_of(self.main2).count(), 1)
        self.tag_index.copy(to=self.main2)
        self.assertEqual(
            TagIndexPage.objects.child_of(self.main2).count(), 1)

    @pytest.mark.django_db(transaction=True)
    def test_copy_method_of_footer_index_wont_duplicate_index_pages(self):
        LanguageRelation.objects.create(
            page=FooterIndexPage.objects.child_of(self.main2).first(),
            language=self.spanish)
        self.assertEqual(
            FooterIndexPage.objects.child_of(self.main2).count(), 1)
        self.section_index.copy(to=self.main2)
        self.assertEqual(
            FooterIndexPage.objects.child_of(self.main2).count(), 1)

    @pytest.mark.django_db(transaction=True)
    def test_copy_method_of_banner_index_wont_duplicate_index_pages(self):
        LanguageRelation.objects.create(
            page=BannerIndexPage.objects.child_of(self.main2).first(),
            language=self.spanish)
        self.assertEqual(
            BannerIndexPage.objects.child_of(self.main2).count(), 1)
        self.section_index.copy(to=self.main2)
        self.assertEqual(
            BannerIndexPage.objects.child_of(self.main2).count(), 1)

    def test_main_returns_bannerpages(self):
        banner = BannerPage(title='test banner')
        self.banner_index.add_child(instance=banner)
        banner.save_revision().publish()
        banner = BannerPage(title='test banner 2')
        self.banner_index.add_child(instance=banner)
        banner.save_revision().publish()
        self.assertEqual(self.main.bannerpages().count(), 2)

    def test_get_parent_section_for_article(self):
        article = self.mk_article(self.yourmind_sub)
        parent = article.get_parent_section()
        self.assertEqual(parent.pk, self.yourmind_sub.pk)

    def test_get_parent_section_for_section(self):
        parent = self.yourmind_sub.get_parent_section()
        self.assertEqual(parent.pk, self.yourmind.pk)

    def test_get_top_level_parent(self):
        title = 'title'
        main_content_type, created = ContentType.objects.get_or_create(
            model='main', app_label='core')
        main = Main.objects.create(
            title=title, slug=title, content_type=main_content_type,
            path='00010011', depth=2, numchild=0, url_path='/home/',
        )
        SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(main.get_site()),
            locale='en', is_active=True)

        french = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(main.get_site()),
            locale='fr', is_active=True)

        en_section = self.mk_section(
            main, title="New Section", slug="new-section")
        en_section2 = self.mk_section(
            en_section, title="New Section 2", slug="new-section-2")
        en_section3 = self.mk_section(
            en_section2, title="New Section 3", slug="new-section-3")
        en_section4 = self.mk_section(
            en_section3, title="New Section 4", slug="new-section-4")

        self.mk_section_translation(en_section, french)
        self.mk_section_translation(en_section2, french)
        fr_section3 = self.mk_section_translation(en_section3, french)
        fr_section4 = self.mk_section_translation(en_section4, french)

        parent = fr_section3.get_top_level_parent(locale='en')
        self.assertEqual(parent.pk, en_section.pk)
        self.assertEqual(fr_section3.depth, 5)
        self.assertEqual(parent.depth, 3)

        parent = fr_section4.get_top_level_parent(locale='en')
        self.assertEqual(parent.pk, en_section.pk)
        self.assertEqual(fr_section4.depth, 6)
        self.assertEqual(parent.depth, 3)

        parent = fr_section4.get_top_level_parent(locale='en', depth=4)
        self.assertEqual(parent.pk, en_section2.pk)
        self.assertEqual(fr_section4.depth, 6)
        self.assertEqual(parent.depth, 4)

        parent = fr_section4.get_top_level_parent(locale='en', depth=2)
        self.assertEqual(parent.pk, main.pk)
        self.assertEqual(parent.depth, 2)

        parent = fr_section4.get_top_level_parent(locale='en', depth=-1)
        self.assertEqual(parent, None)

    def test_article_order(self):
        now = timezone.now()
        article1 = self.mk_article(
            self.yourmind_sub, first_published_at=now)

        self.mk_article(
            self.yourmind_sub,
            first_published_at=now + timezone.timedelta(hours=1))

        # most recent first
        self.assertEqual(
            self.yourmind_sub.articles()[0].title, article1.title)

        # swap published date
        article1.first_published_at = now + timezone.timedelta(hours=4)
        article1.save_revision().publish()

        self.assertEqual(
            self.yourmind_sub.articles()[0].title, article1.title)

    def test_get_effective_image_for_sections(self):
        en_section = self.mk_section(
            self.section_index,
            title="New Section", slug="new-section",
            image=self.image)
        self.assertEqual(
            en_section.get_effective_image(), self.image)

        # image not set to use inherited value
        en_section2 = self.mk_section(
            en_section, title="New Section 2", slug="new-section-2")
        self.assertEqual(
            en_section2.get_effective_image(), en_section.image)

        # image not set to use inherited value
        en_section3 = self.mk_section(
            en_section2, title="New Section 3", slug="new-section-3")
        self.assertEqual(
            en_section3.get_effective_image(), en_section.image)

        # set the image
        en_section3.image = self.image2
        self.assertEqual(
            en_section3.get_effective_image(), self.image2)
        # if translated section doesn't have
        # an image it will inherited from the parent
        fr_section3 = self.mk_section_translation(en_section3, self.french)
        self.assertEqual(
            fr_section3.get_effective_image(), en_section3.image)

        fr_section2 = self.mk_section_translation(en_section2, self.french)
        self.assertEqual(
            fr_section2.get_effective_image(), en_section.image)

        # check if the section doesn't have image it will return None
        en_section4 = self.mk_section(
            self.section_index,
            title="New Section 4", slug="new-section-4", )
        self.assertEqual(
            en_section4.get_effective_image(), '')
        fr_section4 = self.mk_section_translation(en_section4, self.french)
        self.assertEqual(
            fr_section4.get_effective_image(), '')

    def test_get_effective_image_for_articles(self):
        section = self.mk_section(
            self.section_index, title="Section", slug="section")

        en_article1, en_article2 = self.mk_articles(section, 2)
        fr_article1 = self.mk_article_translation(en_article1, self.french)

        self.assertEqual(
            en_article1.get_effective_image(), '')
        self.assertEqual(
            fr_article1.get_effective_image(), '')

        en_article1.image = self.image
        en_article1.save()
        self.assertEqual(
            en_article1.get_effective_image(), self.image)

        # if image not set it should inherite from the main language article
        self.assertEqual(
            fr_article1.get_effective_image(), en_article1.image)

        # if the translated article has an image it should return its image
        fr_article1.image = self.image2
        fr_article1.save()
        self.assertEqual(
            fr_article1.get_effective_image(), self.image2)

    def test_number_of_child_sections(self):
        new_section = self.mk_section(self.section_index)
        self.mk_sections(new_section, count=12)
        self.client.get('/')
        response = self.client.get('/sections-main-1/test-section-0/')
        self.assertContains(response, 'Test Section 11')

    def test_number_of_child_articles_in_section(self):
        new_section = self.mk_section(self.section_index)
        self.mk_articles(new_section, count=12)
        request = self.factory.get('/sections-main-1/test-section-0/')
        request._wagtail_site = self.site
        articles = load_child_articles_for_section(
            {'request': request, 'locale_code': 'en'}, new_section, count=None)
        self.assertEqual(len(articles), 12)

    def test_parent_section(self):
        new_section = self.mk_section(
            self.section_index, title="New Section", slug="new-section")
        new_section1 = self.mk_section(
            new_section, title="New Section 1", slug="new-section-1")
        self.assertEqual(
            new_section1.get_parent_section('en'), new_section)

    def test_article_service_aggregator(self):
        new_section = self.mk_section(
            self.section_index, title="New Section", slug="new-section",
            is_service_aggregator=True)

        with self.assertRaises(ValidationError):
            self.mk_article(
                new_section, title="New Section 1", slug="new-section-1",
                featured_in_latest=True)

    def test_section_service_aggregator(self):
        with self.assertRaises(ValidationError):
            self.mk_section(
                self.section_index, title="New Section", slug="new-section",
                is_service_aggregator=True, monday_rotation=True)

    def test_commenting_closed_settings_fallbacks(self):
        new_section = self.mk_section(
            self.section_index, title="New Section", slug="new-section")
        new_article = self.mk_article(new_section, title="New article")
        # test fallback to section_index
        self.section_index.commenting_state = constants.COMMENTING_CLOSED
        self.section_index.save()
        comment_settings = new_article.get_effective_commenting_settings()
        self.assertEqual(
            comment_settings['state'], constants.COMMENTING_CLOSED)
        # test overriding settings in section
        new_section.commenting_state = constants.COMMENTING_CLOSED
        new_section.save()
        comment_settings = new_article.get_effective_commenting_settings()
        self.assertEqual(
            comment_settings['state'], constants.COMMENTING_CLOSED)
        # test overriding settings in article
        new_article.commenting_state = constants.COMMENTING_DISABLED
        new_article.save_revision().publish()
        comment_settings = new_article.get_effective_commenting_settings()
        self.assertEqual(
            comment_settings['state'], constants.COMMENTING_DISABLED)

    def test_commenting_allowed(self):
        new_section = self.mk_section(
            self.section_index, title="New Section", slug="new-section")
        new_article = self.mk_article(
            new_section, title="New article",
            commenting_state=constants.COMMENTING_OPEN)
        now = timezone.now()
        # with commenting open
        self.assertTrue(new_article.allow_commenting())
        # with commenting disabled and no reopen_time given
        new_article.commenting_state = constants.COMMENTING_DISABLED
        self.assertFalse(new_article.allow_commenting())
        # with commenting closed but past reopen time
        new_article.commenting_state = constants.COMMENTING_CLOSED
        new_article.commenting_open_time = now - timezone.timedelta(days=1)
        self.assertTrue(new_article.allow_commenting())
        # with commenting timestamped and within specified time
        new_article.commenting_state = constants.COMMENTING_TIMESTAMPED
        new_article.commenting_open_time = now - timezone.timedelta(days=1)
        new_article.commenting_close_time = now + timezone.timedelta(days=1)
        self.assertTrue(new_article.allow_commenting())
        # with commenting closed and not yet reopen_time
        new_article.commenting_state = constants.COMMENTING_CLOSED
        new_article.commenting_open_time = now + timezone.timedelta(days=1)
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
            'recommended_articles-INITIAL_FORMS': 0,
            'recommended_articles-MAX_NUM_FORMS': 1000,
            'recommended_articles-MIN_NUM_FORMS': 0,
            'recommended_articles-TOTAL_FORMS': 0,
            'nav_tags-INITIAL_FORMS': 0,
            'nav_tags-MAX_NUM_FORMS': 1000,
            'nav_tags-MIN_NUM_FORMS': 0,
            'nav_tags-TOTAL_FORMS': 0,
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
            'action-publish': 'Publish',
            'homepage_media-count': 0
        }
        self.client.post(
            reverse('wagtailadmin_pages:add',
                    args=('core', 'articlepage', self.yourmind.id,)),
            post_data)
        post_data.update({
            'title': 'this is a test article2',
            'slug': 'this-is-a-test-article-2',
            'tags': 'peace, war',
        })
        self.client.post(
            reverse('wagtailadmin_pages:add',
                    args=('core', 'articlepage', self.yourmind.id,)),
            post_data)

        self.assertEqual(
            ArticlePage.objects.filter(tags__name='war').count(), 2)
        self.assertEqual(
            ArticlePage.objects.filter(tags__name='love').count(), 1)
        self.assertEqual(
            ArticlePage.objects.filter(tags__name='peace').count(), 1)

    def test_meta_data_tags(self):
        User.objects.create_superuser(
            username='testuser', password='password', email='test@email.com')
        self.client.login(username='testuser', password='password')

        post_data = {
            'title': 'this is a test article',
            'slug': 'this-is-a-test-article',
            'recommended_articles-INITIAL_FORMS': 0,
            'recommended_articles-MAX_NUM_FORMS': 1000,
            'recommended_articles-MIN_NUM_FORMS': 0,
            'recommended_articles-TOTAL_FORMS': 0,
            'related_sections-INITIAL_FORMS': 0,
            'related_sections-MAX_NUM_FORMS': 1000,
            'related_sections-MIN_NUM_FORMS': 0,
            'related_sections-TOTAL_FORMS': 0,
            'nav_tags-INITIAL_FORMS': 0,
            'nav_tags-MAX_NUM_FORMS': 1000,
            'nav_tags-MIN_NUM_FORMS': 0,
            'nav_tags-TOTAL_FORMS': 0,
            'body-count': 1,
            'body-0-value': 'Hello',
            'body-0-deleted': False,
            'body-0-order': 1,
            'body-0-type': 'paragraph',
            'metadata_tags': 'love, happiness',
            'action-publish': 'Publish',
            'homepage_media-count': 0
        }
        self.client.post(
            reverse('wagtailadmin_pages:add',
                    args=('core', 'articlepage', self.yourmind.id,)),
            post_data)
        post_data.update({
            'title': 'this is a test article2',
            'slug': 'this-is-a-test-article-2',
            'metadata_tags': 'peace, happiness',
        })
        self.client.post(
            reverse('wagtailadmin_pages:add',
                    args=('core', 'articlepage', self.yourmind.id,)),
            post_data)

        self.assertEqual(
            ArticlePage.objects.filter(
                metadata_tags__name='happiness').count(), 2)
        self.assertEqual(
            ArticlePage.objects.filter(
                metadata_tags__name='love').count(), 1)
        self.assertEqual(
            ArticlePage.objects.filter(
                metadata_tags__name='peace').count(), 1)

    def test_nav_tag_delete_updates_article(self):
        """
        ArticlePageTags with no tags should not be saved
        """
        tag_index = TagIndexPage.objects.child_of(self.main).first()
        article = self.mk_article(
            parent=self.yourmind, title='first_main_article')

        article2 = self.mk_article(
            parent=self.yourmind, title='second_main_article')
        tag = Tag(title='New tag')
        tag2 = Tag(title='Another New tag')
        tag_index.add_child(instance=tag)
        tag.save_revision().publish()
        tag_index.add_child(instance=tag2)
        tag2.save_revision().publish()

        article.nav_tags.create(tag=tag)
        article.save()

        article2.nav_tags.create(tag=tag)
        article2.nav_tags.create(tag=tag2)
        article2.save()
        self.assertEqual(article.nav_tags.get(tag=tag).tag,
                         article2.nav_tags.get(tag=tag).tag,
                         )
        # delete the tag
        tag.delete()
        # test the nav_tags are deleted and removed from the articles
        self.assertEqual(ArticlePageTags.objects.count(), 1)
        self.assertFalse(article.nav_tags.filter(pk=1).exists())
        self.assertTrue(article2.nav_tags.get(), tag2)

    def test_social_media(self):
        User.objects.create_superuser(
            username='testuser', password='password', email='test@email.com')
        self.client.login(username='testuser', password='password')

        self.mk_article(
            self.yourmind, title="New article",
            social_media_title='media title',
            social_media_description='media description', )

        self.mk_article(
            self.yourmind, title="New article2",
            social_media_title='media title',
            social_media_image=self.image, )

        self.assertEqual(
            ArticlePage.objects.filter(
                social_media_title='media title').count(), 2)
        self.assertEqual(
            ArticlePage.objects.filter(
                social_media_description='media description').count(), 1)
        self.assertEqual(
            ArticlePage.objects.filter(
                social_media_image=self.image).count(), 1)

        response = self.client.get('/sections-main-1/your-mind/new-article/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'content="media title"')

    def test_site_languages(self):
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
            locale='sp',
            is_active=False)

        response = self.client.get('/')
        self.assertContains(response, 'English')
        self.assertContains(response, 'français')
        self.assertNotContains(response, 'español')

    def test_get_translation_template_tag(self):
        section = self.mk_section(self.section_index)
        section2 = self.mk_section(self.section_index)
        translated_section = self.mk_section_translation(section, self.french)
        request = self.factory.get('/')
        request._wagtail_site = self.site
        qs = get_translation({
            'locale_code': 'fr', 'request': request}, section)
        self.assertEqual(translated_section.id, qs.id)
        qs = get_translation({
            'locale_code': 'fr', 'request': request}, section2)
        self.assertEqual(section2.id, qs.id)

    def test_hero_article(self):
        User.objects.create_superuser(
            username='testuser', password='password', email='test@email.com')
        self.client.login(username='testuser', password='password')

        # create a new article and go to it's edit page
        new_section = self.mk_section(
            self.section_index, title="New Section", slug="new-section")
        new_article = self.mk_article(new_section, title="New article", )
        response = self.client.get(
            reverse('wagtailadmin_pages:edit', args=(new_article.id,)))
        self.assertEqual(response.status_code, 200)

        # Marking article as Hero Article with no promote date
        # or demote date raises error
        post_data = {
            "feature_as_hero_article": True,
            'title': 'this is a test article',
            'slug': 'this-is-a-test-article',
            'recommended_articles-INITIAL_FORMS': 0,
            'recommended_articles-MAX_NUM_FORMS': 1000,
            'recommended_articles-MIN_NUM_FORMS': 0,
            'recommended_articles-TOTAL_FORMS': 0,
            'nav_tags-INITIAL_FORMS': 0,
            'nav_tags-MAX_NUM_FORMS': 1000,
            'nav_tags-MIN_NUM_FORMS': 0,
            'nav_tags-TOTAL_FORMS': 0,
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
            'action-publish': 'Publish',
            'homepage_media-count': 0
        }
        self.client.post(
            reverse('wagtailadmin_pages:edit', args=(new_article.id,)),
            post_data
        )
        self.assertRaisesMessage(
            ValidationError,
            "Please specify the date and time that you would like this "
            "article to appear as the Hero Article."
        )

        # Raises error if promote_date is in the past
        post_data.update({
            "promote_date": timezone.now() + timezone.timedelta(days=-1),
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
            "demote_date": timezone.now() + timezone.timedelta(days=-1)
        })
        self.client.post(
            reverse('wagtailadmin_pages:edit', args=(new_article.id,)),
            post_data
        )
        self.assertRaisesMessage(
            ValidationError,
            "The article cannot be demoted before it has been promoted."
        )

    def test_demote_articles_post_save(self):
        article = self.mk_article(
            self.yourmind_sub, title='article', slug='article',
            featured_in_section=True, featured_in_homepage=True,
            featured_in_latest=True)
        self.assertFalse(article.featured_in_latest)
        self.assertFalse(article.featured_in_homepage)
        self.assertFalse(article.featured_in_section)

        article.slug = 'article-slug'
        article.save()
        self.assertFalse(article.featured_in_latest)
        self.assertFalse(article.featured_in_homepage)
        self.assertFalse(article.featured_in_section)

        article.featured_in_section = True
        article.featured_in_homepage = True
        article.featured_in_latest = True
        self.assertTrue(article.featured_in_latest)
        self.assertTrue(article.featured_in_homepage)
        self.assertTrue(article.featured_in_section)

        article.save()
        self.assertFalse(article.featured_in_latest)
        self.assertFalse(article.featured_in_homepage)
        self.assertFalse(article.featured_in_section)

    def test_is_hero_article(self):
        promote_date = timezone.now() + timezone.timedelta(days=-1)
        demote_date = timezone.now() + timezone.timedelta(days=1)
        article_1 = ArticlePage(
            title="New article",
            feature_as_hero_article=True,
            promote_date=promote_date,
            demote_date=demote_date
        )
        self.yourmind.add_child(instance=article_1)
        self.assertTrue(article_1.is_current_hero_article())

        promote_date = timezone.now() + timezone.timedelta(days=2)
        demote_date = timezone.now() + timezone.timedelta(days=4)
        article_2 = ArticlePage(
            title="New article",
            promote_date=promote_date,
            demote_date=demote_date
        )
        self.yourmind.add_child(instance=article_2)
        self.assertFalse(article_2.is_current_hero_article())

    def test_molo_page_helper_method_is_content_page(self):
        self.assertTrue(self.yourmind.is_content_page("Your mind"))
        self.assertFalse(self.yourmind.is_content_page("Not Your mind"))

    # exclude future-scheduled Hero Article articles from the
    # latest articles queryset.
    # Create two articles, one with present promote date and one
    # with future promote date. Verify that the article with a
    # future promote date does not appear in latest articles
    # queryset.
    def test_future_hero_article_not_in_latest(self):
        promote_date = timezone.now() + timezone.timedelta(days=2)
        demote_date = timezone.now() + timezone.timedelta(days=4)
        future_article = ArticlePage(
            title="Future article",
            promote_date=promote_date,
            demote_date=demote_date,
            depth="1",
            path="0003",
            featured_in_latest=True,
            feature_as_hero_article=True
        )
        self.yourmind.add_child(instance=future_article)
        future_article.save()
        main = Main.objects.all().first()
        self.assertQuerysetEqual(main.latest_articles(), [])

        promote_date = timezone.now() + timezone.timedelta(days=-2)
        demote_date = timezone.now() + timezone.timedelta(days=-1)
        present_article = ArticlePage(
            title="Present article",
            promote_date=promote_date,
            demote_date=demote_date,
            depth="1",
            path="0004",
            featured_in_latest_start_date=promote_date,
            feature_as_hero_article=True
        )
        self.yourmind.add_child(instance=present_article)
        present_article.save()
        promote_articles()
        self.assertQuerysetEqual(
            main.latest_articles(), [repr(present_article), ])


@patch('django.utils.timezone.activate')
class TestCmsSettings(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.mk_main2()

        # Something creates CmsSettings for both sites when only
        # one is explicitly created here.
        self.assertEqual(len(CmsSettings.objects.all()), 0)
        self.settings = CmsSettings.objects.create(site=self.site)
        self.assertEqual(len(CmsSettings.objects.all()), 2)

        self.timezone = Timezone(title='FakeContinent/FakeCity')
        self.timezone.save()

    def test_cms_settings_activates_timezone_once(self, timezone_activate):
        self.settings.timezone = self.timezone
        self.settings.save()

        timezone_activate.assert_called_once_with('FakeContinent/FakeCity')

    def test_cms_settings_save_updates_all_timezones(self, timezone_activate):
        self.settings.timezone = self.timezone
        self.settings.save()

        for settings in CmsSettings.objects.all():
            self.assertEqual(settings.timezone, self.timezone)


class MoloPageTestCase(TestCase):

    def test_can_exist_under_method(self):
        self.assertEqual(MoloPage.can_exist_under(None), False)
