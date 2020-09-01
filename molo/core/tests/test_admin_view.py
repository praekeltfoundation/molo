from django.test import TestCase
from django.contrib.auth.models import User
from wagtail.images.tests.utils import get_test_image_file, Image

from molo.core.utils import generate_slug
from molo.core.tests.base import MoloTestCaseMixin
from molo.core.models import (
    Main, SiteLanguageRelation, Languages, ArticlePage)


class TestAdminView(TestCase, MoloTestCaseMixin):
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

        self.yourmind = self.mk_section(
            self.section_index, title='Your Mind')

        self.yourmind_fr = self.mk_section_translation(
            self.yourmind, self.french, title='Your mind in french')

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
        User.objects.create_superuser(
            username='testuser', password='password', email='test@email.com')
        self.client.login(username='testuser', password='password')

    def test_articles_appears_in_admin_view(self):
        self.mk_article(self.yourmind)
        response = self.client.get(
            '/admin/core/articlepagelanguageproxy/'
        )
        self.assertContains(response, 'Test page 0')

    def test_section_in_admin_view(self):
        self.mk_article(self.yourmind)
        response = self.client.get(
            '/admin/core/articlepagelanguageproxy/'
        )
        self.assertContains(response, 'Your Mind')

    def test_article_tag_in_admin_view(self):
        article = self.mk_article(self.yourmind, title='article')
        article.tags.add("the tag")
        article.save_revision().publish()
        response = self.client.get(
            '/admin/core/articlepagelanguageproxy/'
        )
        self.assertContains(response, 'the tag')

    def test_article_image_in_admin_view(self):
        self.image = Image.objects.create(
            title="Test image",
            file=get_test_image_file(),
        )
        article = self.mk_article(self.yourmind,
                                  title='article',
                                  image=self.image
                                  )
        article.save_revision().publish()
        response = self.client.get(
            '/admin/core/articlepagelanguageproxy/'
        )
        self.assertContains(response, '<img src="/media/images/')

    def test_status_custom_filter_published_in_admin_view(self):
        self.mk_articles(self.yourmind)
        self.article2 = ArticlePage.objects.get(title="Test page 1")
        self.article2.unpublish()
        response = self.client.get(
            '/admin/core/articlepagelanguageproxy/?status=published'
        )
        self.assertContains(response, 'Test page 0')
        self.assertNotContains(response, 'Test page 1')

    def test_status_custom_filter_in_review_in_admin_view(self):
        self.mk_articles(self.yourmind)
        self.article2 = ArticlePage.objects.get(title="Test page 1")
        self.article2.save_revision(submitted_for_moderation=True)
        response = self.client.get(
            '/admin/core/articlepagelanguageproxy/?status=in_review'
        )
        self.assertNotContains(response, 'Test page 0')
        self.assertContains(response, 'Test page 1')

    def test_status_custom_filter_draft_in_admin_view(self):
        self.mk_articles(self.yourmind)
        self.article2 = ArticlePage.objects.get(title="Test page 1")
        self.article2.unpublish()
        response = self.client.get(
            '/admin/core/articlepagelanguageproxy/?status=draft'
        )
        self.assertNotContains(response, 'Test page 0')
        self.assertContains(response, 'Test page 1')

    def test_status_custom_filter_sections_in_admin_view(self):
        self.mk_articles(self.yourmind)
        self.article2 = ArticlePage.objects.get(title="Test page 1")
        self.article2.unpublish()
        response = self.client.get(
            '/admin/core/articlepagelanguageproxy/?section=%d' %
            self.yourmind.id
        )
        self.assertContains(response, 'Test page 0')
        self.assertContains(response, 'Test page 1')

    def test_404_on_object_does_not_exist(self):
        response = self.client.get(
            '/admin/pages/{}/edit/'.format(self.yourmind.pk)
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            '/admin/pages/1234567/edit/'
        )
        self.assertEqual(response.status_code, 404)

    def test_article_preview(self):
        title = 'Test page'
        data = {
            'title': title,
            'slug': generate_slug(title),
            'subtitle': 'Sample page description'
        }
        article = ArticlePage(**data)
        self.yourmind.add_child(instance=article)
        article.save_revision()

        response = self.client.get(
            '/admin/pages/{}/edit/preview/'.format(article.pk)
        )
        self.assertEqual(response.status_code, 200)

        article.get_latest_revision().publish()
        response = self.client.get(
            '/admin/pages/{}/edit/preview/'.format(article.pk)
        )
        self.assertEqual(response.status_code, 200)
