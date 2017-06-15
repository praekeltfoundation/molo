# coding=utf-8
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from molo.core.models import (
    Main, ReactionQuestionResponse,
    SiteLanguageRelation, Languages, ReactionQuestionChoice)
from molo.core.tests.base import MoloTestCaseMixin


class TestReactionQuestionResultsAdminView(TestCase, MoloTestCaseMixin):
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

    def test_reaction_question_appears_in_wagtail_admin(self):
        User.objects.create_superuser(
            username='testuser', password='password', email='test@email.com')
        self.client.login(username='testuser', password='password')
        article = self.mk_article(self.yourmind)
        article_site_2 = self.mk_article(self.yourmind2)
        question = self.mk_reaction_question(self.reaction_index, article)
        question2 = self.mk_reaction_question(
            self.reaction_index2, article_site_2)
        response = self.client.get(
            '/admin/core/reactionquestion/'
        )
        self.assertContains(
            response,
            '<a href="/admin/reactionquestion/%s/results/">'
            'Test Question</a>' % question.pk)
        self.assertNotContains(
            response,
            '<a href="/admin/reactionquestion/%s/results/">'
            'Test Question</a>' % question2.pk)

    def test_article_appears_in_wagtail_admin_summary(self):
        User.objects.create_superuser(
            username='testuser', password='password', email='test@email.com')
        self.client.login(username='testuser', password='password')
        article = self.mk_article(self.yourmind)
        article_site_2 = self.mk_article(self.yourmind2)
        self.mk_reaction_question(self.reaction_index, article)
        self.mk_reaction_question(
            self.reaction_index2, article_site_2)
        response = self.client.get(
            '/admin/core/articlepage/'
        )
        self.assertContains(
            response,
            '<a href="/admin/reactionquestion/%s/results/summary/">'
            'Test page 0</a>' % article.pk)
        self.assertNotContains(
            response,
            '<a href="/admin/reactionquestion/%s/results/summary/">'
            'Test page 0</a>' % article_site_2.pk)

    def test_reaction_question_results_view(self):
        super_user = User.objects.create_superuser(
            username='testuser', password='password', email='test@email.com')
        self.client.login(username='testuser', password='password')

        article = self.mk_article(self.yourmind)
        question = self.mk_reaction_question(self.reaction_index, article)
        choice1 = question.get_children().first()
        response = self.client.post(reverse(
            'reaction-vote', kwargs={
                'question_id': question.id, 'article_slug': article.slug}),
            {'choice': choice1.id})

        response = self.client.get(
            '/admin/reactionquestion/{0}/results/'.format(question.id)
        )

        expected_headings_html = '<tr><th>Submission Date</th><th>Answer</th>'\
                                 '<th>User</th><th>Article</th></tr>'

        self.assertContains(response, expected_headings_html, html=True)
        self.assertContains(response, choice1.title)
        self.assertContains(response, super_user.username)
        self.assertContains(response, article.title)

        # test CSV download
        response = self.client.get(
            '/admin/reactionquestion/{0}/results/?action=download'.format(
                question.id)
        )
        created_date = ReactionQuestionResponse.objects.first().created_at

        expected_output = (
            'Submission Date,Answer,User,Article\r\n'
            '{0},yes,{1},{2}\r\n'
        ).format(
            created_date,
            super_user.username, article.title
        )
        self.assertContains(response, expected_output)

    def test_reaction_question_results_summary_view(self):
        User.objects.create_superuser(
            username='testuser', password='password', email='test@email.com')
        self.client.login(username='testuser', password='password')

        article = self.mk_article(self.yourmind)
        question = self.mk_reaction_question(self.reaction_index, article)
        choice1 = question.get_children().first()
        response = self.client.post(reverse(
            'reaction-vote', kwargs={
                'question_id': question.id, 'article_slug': article.slug}),
            {'choice': choice1.id})

        response = self.client.get(
            '/admin/reactionquestion/{0}/results/summary/'.format(article.id)
        )

        expected_headings_html = '<tr><th>Article</th><th>yes</th>'\
                                 '<th>maybe</th><th>no</th></tr>'
        self.assertContains(response, expected_headings_html, html=True)
        self.assertContains(response, 'Test page 0')

        # test CSV download
        response = self.client.get(
            '/admin/reactionquestion/{0}/'
            'results/summary/?action=download'.format(article.id)
        )

        expected_output = (
            'Article,yes,maybe,no\r\n'
            '{0},1,0,0\r\n'
        ).format(
            article.title,
        )
        self.assertContains(response, expected_output)


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
        self.assertEquals(response.status_code, 302)
        self.assertEquals(
            response['Location'], '/reaction/test-page-0/20/yes/feedback/')
        response = self.client.get('/reaction/test-page-0/20/yes/feedback/')
        self.assertContains(
            response, '<a href="/sections-main-1/your-mind/test-page-0/">')
        self.assertContains(response, 'well done')
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
        translated_question = self.mk_reaction_translation(
            question,
            article,
            self.french,
            title=question.title + ' in french',)
        translated_choice = ReactionQuestionChoice(
            title='ja', success_message='mooi gedoen')
        question.add_child(instance=translated_choice)
        translated_choice.save_revision().publish()
        translated_choice = self.mk_translation(
            question.get_first_child(), self.french, translated_choice)

        self.client.get('/locale/fr/')
        response = self.client.get(
            '/sections-main-1/your-mind/test-page-0-in-french/')
        self.assertContains(response, 'Test Question in french')
        response = self.client.post(reverse(
            'reaction-vote', kwargs={
                'question_id': translated_question.id,
                'article_slug': article.slug}),
            {'choice': translated_choice.id})
        self.assertEquals(ReactionQuestionResponse.objects.all().count(), 1)
        response = self.client.get('/reaction/test-page-0/20/yes/feedback/')
        self.assertContains(
            response, '<a href="/sections-main-1/your-mind/test-page-0/">')
        self.assertContains(response, 'mooi gedoen')
