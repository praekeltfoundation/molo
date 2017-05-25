# coding=utf-8
from django.test import TestCase
from django.core.urlresolvers import reverse

from molo.core.models import (
    Main, ReactionQuestionResponse,
    SiteLanguageRelation, Languages)
from molo.core.tests.base import MoloTestCaseMixin


class TestReactionQuestions(TestCase, MoloTestCaseMixin):

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
            self.section_index, title='Your mind')

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

    def test_can_react_on_article(self):
        article = self.mk_article(self.yourmind)
        question = self.mk_reaction_question(self.reaction_index, article)
        self.user = self.login()
        response = self.client.get(article.url)
        self.assertContains(response, question.title)
        for choice in question.get_children():
            self.assertContains(response, choice.title)
        choice1 = question.get_children().first()
        self.assertEquals(ReactionQuestionResponse.objects.all().count(), 0)
        response = self.client.post(reverse(
            'reaction-vote', kwargs={
                'question_id': question.id, 'article_slug': article.slug}),
            {'choice': choice1.id})
        self.assertEquals(ReactionQuestionResponse.objects.all().count(), 1)

        # test user can only submit once
        response = self.client.post(reverse(
            'reaction-vote', kwargs={
                'question_id': question.id, 'article_slug': article.slug}),
            {'choice': choice1.id})
        self.assertEquals(ReactionQuestionResponse.objects.all().count(), 1)

    def test_correct_reaction_shown_for_locale(self):
        article = self.mk_article(self.yourmind)
        question = self.mk_reaction_question(self.reaction_index, article)
        self.mk_article_translation(
            article,
            self.french,
            title=article.title + ' in french',)
        self.mk_reaction_translation(
            question,
            article,
            self.french,
            title=question.title + ' in french',)

        self.client.get('/locale/fr/')
        response = self.client.get(
            '/sections-main-1/your-mind/test-page-0-in-french/')
        self.assertContains(response, 'Test Question in french')
