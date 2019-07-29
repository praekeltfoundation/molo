# coding=utf-8
import pytest
from mock import patch
from django.contrib.auth.models import User
from django.utils import timezone
from django.test import TestCase, RequestFactory
from molo.core.models import (
    Main, SiteLanguageRelation, Languages, BannerPage, ArticlePageTags,
    FormPage, SiteSettings, ArticleOrderingChoices, ReactionQuestionChoice,
    ReactionQuestion, ReactionQuestionResponse, ReactionQuestionIndexPage)
from molo.core.tests.base import MoloTestCaseMixin
from molo.core.templatetags.core_tags import (
    get_parent, bannerpages, load_tags_for_article, get_recommended_articles,
    hero_article, render_translations, load_descendant_articles_for_section,
    load_child_articles_for_section, load_reaction_choice_submission_count,
    load_user_choice_reaction_question, get_tag_articles
)
from molo.core.templatetags.forms_tags import forms_list


@pytest.mark.django_db
class TestModels(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.main = Main.objects.all().first()
        self.factory = RequestFactory()
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

        self.yourmind = self.mk_section(
            self.section_index, title='Your mind')
        self.yourmind_sub = self.mk_section(
            self.yourmind, title='Your mind subsection')
        # create a requset object
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        self.request.site = self.site

    def create_form_page(
            self, parent, title="Test Form",
            slug="test-form", **kwargs):
        form_page = FormPage(
            title=title,
            slug=slug,
            intro='Introduction to Test Form ...',
            thank_you_text='Thank you for taking the Test Form',
            **kwargs
        )
        parent.add_child(instance=form_page)
        form_page.save_revision().publish()
        return form_page

    def test_get_form_list_homepage(self):
        context = {
            'locale_code': 'en',
            'request': self.request,
            'forms': self.create_form_page(self.form_index)
        }
        context = forms_list(context)
        self.assertEqual(len(context['forms']), 1)

    def test_load_user_choice_reaction_question(self):
        article = self.mk_articles(self.yourmind, 1)[0]
        question = ReactionQuestion(title='q1')
        ReactionQuestionIndexPage.objects.last().add_child(instance=question)
        question.save_revision().publish()
        choice = ReactionQuestionChoice(title='yes')
        question.add_child(instance=choice)
        choice.save_revision().publish()
        choice2 = ReactionQuestionChoice(title='no')
        question.add_child(instance=choice2)
        choice2.save_revision().publish()
        user = User.objects.create_superuser(
            username='testuser', password='password', email='test@email.com')
        ReactionQuestionResponse.objects.create(
            choice=choice, article=article, question=question,
            user=user)
        request = self.factory.get('/')
        request.user = user
        self.assertTrue(load_user_choice_reaction_question(
            {'request': request},
            question=question,
            choice=choice,
            article=article))
        self.assertFalse(load_user_choice_reaction_question(
            {'request': request},
            question=question,
            choice=choice2,
            article=article))

    def test_reaction_question_submission_count(self):
        article = self.mk_articles(self.yourmind, 1)[0]
        question = ReactionQuestion(title='q1')
        ReactionQuestionIndexPage.objects.last().add_child(instance=question)
        question.save_revision().publish()
        choice = ReactionQuestionChoice(title='yes')
        question.add_child(instance=choice)
        choice.save_revision().publish()
        choice2 = ReactionQuestionChoice(title='no')
        question.add_child(instance=choice2)
        choice2.save_revision().publish()
        ReactionQuestionResponse.objects.create(
            choice=choice, article=article, question=question)
        count = load_reaction_choice_submission_count(
            choice=choice, article=article, question=question)
        self.assertEqual(count, 1)
        count = load_reaction_choice_submission_count(
            choice=choice2, article=article, question=question)
        self.assertEqual(count, 0)

    def test_render_translations(self):
        # this should return an empty dictionary for non main lang pages
        article = self.mk_articles(self.yourmind, 1)[0]
        fr_article = self.mk_article_translation(article, self.french)
        self.assertEqual(render_translations({}, fr_article), {})

    def test_bannerpages_without_position(self):
        banner = BannerPage(title='test banner')
        self.banner_index.add_child(instance=banner)
        banner.save_revision().publish()
        banner2 = BannerPage(title='test banner 2')
        self.banner_index.add_child(instance=banner2)
        banner2.save_revision().publish()
        banner3 = BannerPage(title='test banner 3')
        self.banner_index.add_child(instance=banner3)
        banner3.save_revision().publish()
        self.assertEqual(self.main.bannerpages().count(), 3)

        request = self.factory.get('/')
        request.site = self.site

        self.assertEqual(len(bannerpages({
            'locale_code': 'en', 'request': request})['bannerpages']), 3)

    def test_bannerpages_with_position(self):
        banner = BannerPage(title='test banner')
        self.banner_index.add_child(instance=banner)
        banner.save_revision().publish()
        banner2 = BannerPage(title='test banner 2')
        self.banner_index.add_child(instance=banner2)
        banner2.save_revision().publish()
        banner3 = BannerPage(title='test banner 3')
        self.banner_index.add_child(instance=banner3)
        banner3.save_revision().publish()
        self.assertEqual(self.main.bannerpages().count(), 3)

        request = self.factory.get('/')
        request.site = self.site

        self.assertEqual(len(bannerpages({
            'locale_code': 'en',
            'request': request}, position=0)['bannerpages']), 1)
        self.assertEqual(bannerpages({
            'locale_code': 'en',
            'request': request}, position=0)['bannerpages'][0].title,
            'test banner')
        self.assertEqual(bannerpages({
            'locale_code': 'en',
            'request': request}, position=1)['bannerpages'][0].title,
            'test banner 2')

    def test_bannerpages_with_position_out_of_range(self):
        banner = BannerPage(title='test banner')
        self.banner_index.add_child(instance=banner)
        banner.save_revision().publish()
        banner2 = BannerPage(title='test banner 2')
        self.banner_index.add_child(instance=banner2)
        banner2.save_revision().publish()
        banner3 = BannerPage(title='test banner 3')
        self.banner_index.add_child(instance=banner3)
        banner3.save_revision().publish()
        self.assertEqual(self.main.bannerpages().count(), 3)

        request = self.factory.get('/')
        request.site = self.site

        self.assertEqual(bannerpages({
            'locale_code': 'en',
            'request': request}, position=4), None)

    def test_get_parent_template_tag(self):
        request = self.factory.get('/')
        request.site = self.site

        article = self.mk_articles(self.yourmind, 1)[0]
        fr_article = self.mk_article_translation(article, self.french)

        self.assertEqual(
            get_parent({'locale_code': 'fr', 'request': request}, article),
            self.yourmind)
        self.assertEqual(
            get_parent({'locale_code': 'fr', 'request': request}, fr_article),
            self.yourmind)
        self.assertEqual(get_parent(
            {'locale_code': 'fr', 'request': request}, self.yourmind_sub),
            self.yourmind)

        fr_yourmind = self.mk_section_translation(self.yourmind, self.french)
        self.assertEqual(
            get_parent({'locale_code': 'en', 'request': request}, article),
            self.yourmind)
        self.assertEqual(
            get_parent({'locale_code': 'en', 'request': request}, fr_article),
            self.yourmind)
        self.assertEqual(get_parent(
            {'locale_code': 'en', 'request': request}, self.yourmind_sub),
            self.yourmind)

        self.assertEqual(
            get_parent({'locale_code': 'fr', 'request': request}, article),
            fr_yourmind)
        self.assertEqual(
            get_parent({'locale_code': 'fr', 'request': request}, fr_article),
            fr_yourmind)
        self.assertEqual(get_parent(
            {'locale_code': 'fr', 'request': request}, self.yourmind_sub),
            fr_yourmind)

        self.assertEqual(get_parent(
            {'locale_code': 'fr', 'request': request}, self.yourmind),
            None)

    def test_load_tags_for_article(self):
        request = self.factory.get('/')
        request.site = self.site
        article1 = self.mk_article(self.yourmind, title='article 1')

        tag = self.mk_tag(parent=self.tag_index)
        ArticlePageTags.objects.create(page=article1, tag=tag)
        self.assertEqual(load_tags_for_article(
            {
                'locale_code': 'en',
                'request': request
            }, article1)[0],
            tag)
        self.assertEqual(load_tags_for_article(
            {
                'locale_code': 'en',
                'request': request
            }, self.yourmind),
            None)

    def test_article_ordering_descendant_articles(self):
        today = timezone.now()
        request = self.factory.get('/')
        request.site = self.site
        settings = SiteSettings.objects.create(
            site=self.site,
            article_ordering_within_section=ArticleOrderingChoices.PK
        )
        article1 = self.mk_article(
            self.yourmind, title='article 1',
            first_published_at=today - timezone.timedelta(hours=1),
            featured_in_section_start_date=today - timezone.timedelta(hours=1)
        )
        article2 = self.mk_article(
            self.yourmind, title='article 2',
            first_published_at=today,
            featured_in_section_start_date=today
        )

        self.assertEqual(load_descendant_articles_for_section({
            'locale_code': 'en', 'request': request
        }, self.yourmind)[0], article1)
        self.assertEqual(load_descendant_articles_for_section({
            'locale_code': 'en', 'request': request
        }, self.yourmind)[1], article2)

        settings.article_ordering_within_section =\
            ArticleOrderingChoices.PK_DESC
        settings.save()

        self.assertEqual(load_descendant_articles_for_section({
            'locale_code': 'en', 'request': request
        }, self.yourmind)[0], article2)
        self.assertEqual(load_descendant_articles_for_section({
            'locale_code': 'en', 'request': request
        }, self.yourmind)[1], article1)

    def test_article_ordering_child_articles(self):
        today = timezone.now()
        request = self.factory.get('/')
        request.site = self.site
        settings = SiteSettings.objects.create(
            site=self.site,
            article_ordering_within_section=ArticleOrderingChoices.PK
        )
        article1 = self.mk_article(self.yourmind, title='article 1')
        article1.first_published_at = today + timezone.timedelta(hours=1)
        article1.save()

        article2 = self.mk_article(self.yourmind, title='article 2')
        article2.first_published_at = today - timezone.timedelta(hours=1)
        article2.save()

        self.assertEqual(load_child_articles_for_section({
            'locale_code': 'en', 'request': request
        }, self.yourmind)[0], article1)
        self.assertEqual(load_child_articles_for_section({
            'locale_code': 'en', 'request': request
        }, self.yourmind)[1], article2)

        settings.article_ordering_within_section =\
            ArticleOrderingChoices.PK_DESC
        settings.save()

        self.assertEqual(load_child_articles_for_section({
            'locale_code': 'en', 'request': request
        }, self.yourmind)[0], article2)
        self.assertEqual(load_child_articles_for_section({
            'locale_code': 'en', 'request': request
        }, self.yourmind)[1], article1)

    def test_get_recommended_articles(self):
        request = self.factory.get('/')
        request.site = self.site
        article1 = self.mk_article(self.yourmind, title='article 1')

        self.assertEqual(get_recommended_articles(
            {'locale_code': 'en', 'request': request}, article1),
            [])

    @patch('molo.core.templatetags.core_tags.get_pages')
    def test_hero_article_empty_queryset_if_no_site(self, get_pages_mock):
        request = self.factory.get('/')
        request.site = None
        context = {'request': request, 'locale_code': 'en'}
        get_pages_mock.return_value = []

        self.assertEqual(
            hero_article(context),
            {
                'articles': [],
                'request': request,
                'locale_code': 'en',
            }
        )

    def test_get_tag_articles(self):
        request = self.factory.get('/')
        request.site = self.site
        your_body = self.mk_section(
            self.section_index, title='Your body')

        article01 = self.mk_article(your_body, title='Your body 1')
        article02 = self.mk_article(your_body, title='Your body 2')

        article1 = self.mk_article(self.yourmind, title='article 1')
        article2 = self.mk_article(self.yourmind, title='article 2')

        self.mk_article(self.yourmind, title='article 3')
        self.mk_article(self.yourmind, title='article 4')
        self.mk_article(self.yourmind, title='article 5')
        self.mk_article(self.yourmind, title='article 6')
        self.mk_article(self.yourmind, title='article 7')
        self.mk_article(self.yourmind, title='article 8')
        self.mk_article(self.yourmind, title='article 9')

        tag1 = self.mk_tag(parent=self.main, feature_in_homepage=True)
        tag2 = self.mk_tag(parent=self.main, feature_in_homepage=True)

        ArticlePageTags.objects.create(page=article1, tag=tag1)
        ArticlePageTags.objects.create(page=article01, tag=tag1)

        ArticlePageTags.objects.create(page=article2, tag=tag2)
        ArticlePageTags.objects.create(page=article02, tag=tag2)

        articles = get_tag_articles({'locale_code': 'en', 'request': request})
        tag_articles = articles['tags_list'][0][1]

        for i in tag_articles:
            self.assertNotIn(i, articles['sections'])
            self.assertNotIn(i, articles['latest_articles'])
