import csv
from collections import OrderedDict
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic.edit import FormView
from molo.core.models import ReactionQuestionResponse, ReactionQuestion, \
    ArticlePageReactionQuestions, ArticlePage


class ReactionQuestionSummaryAdminView(FormView):
    def get(self, request, *args, **kwargs):
        article = kwargs['article']
        article = get_object_or_404(ArticlePage, pk=article)
        question = ArticlePageReactionQuestions.objects.get(
            page=article).reaction_question
        data_headings = ['Article']
        data_rows = []
        choices = question.get_children().filter(
            languages__language__is_main_language=True)
        choice_totals = []
        for choice in choices:
            data_headings.append(choice.title)
            responses = ReactionQuestionResponse.objects.filter(
                question=question, article=article, choice=choice)
            choice_totals.append(responses.count())
        row = OrderedDict({})
        article = article.title
        row['article'] = article
        counter = 0
        for i in choice_totals:
            row[counter] = i
            counter += 1
        data_rows.append(row)
        action = request.GET.get('action', None)
        if action == 'download':
            return self.send_csv(question.title, data_headings, data_rows)

        context = {
            'page_title': question.title,
            'data_headings': data_headings,
            'data_rows': data_rows
        }

        return render(request, 'admin/question_results.html', context)

    def send_csv(self, question_title, data_headings, data_rows):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = \
            'attachment;filename="reaction-question-{0}-results.csv"'.format(
                question_title)

        writer = csv.writer(response)
        writer.writerow(data_headings)

        for item in data_rows:
            writer.writerow(item.values())

        return response


class ReactionQuestionResultsAdminView(FormView):
    def get(self, request, *args, **kwargs):
        parent = kwargs['parent']
        question = get_object_or_404(ReactionQuestion, pk=parent)

        data_headings = ['Submission Date', 'Answer', 'User', 'Article']
        data_rows = []

        for response in ReactionQuestionResponse.objects.filter(
                question=question):
            data_rows.append(OrderedDict({
                'submission_date': response.created_at,
                'answer': response.choice,
                'user': response.user,
                'article': response.article
            }))

        action = request.GET.get('action', None)
        if action == 'download':
            return self.send_csv(question.title, data_headings, data_rows)

        context = {
            'page_title': question.title,
            'data_headings': ['Submission Date', 'Answer', 'User', 'Article'],
            'data_rows': data_rows
        }

        return render(request, 'admin/question_results.html', context)

    def send_csv(self, question_title, data_headings, data_rows):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = \
            'attachment;filename="reaction-question-{0}-results.csv"'.format(
                question_title)

        writer = csv.writer(response)
        writer.writerow(data_headings)

        for item in data_rows:
            writer.writerow(item.values())

        return response
