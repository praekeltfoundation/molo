from __future__ import absolute_import, unicode_literals

from django.core.management.base import BaseCommand
import logging

from django.core.exceptions import ObjectDoesNotExist
from wagtail.wagtailcore.blocks import StreamValue
from molo.core.models import (
    ArticlePage,
    ArticlePageRecommendedSections,
)


def create_recomended_articles(main_article, article_list):
    '''
    Creates recommended article objects from article_list
    and _prepends_ to existing recommended articles.
    '''

    # store existing recommended articles
    existing_recommended_articles = [
        ra.recommended_article.specific
        for ra in main_article.recommended_articles.all()]
    # delete existing recommended articles
    ArticlePageRecommendedSections.objects.filter(page=main_article).delete()

    for hyperlinked_article in article_list:
        ArticlePageRecommendedSections(
            page=main_article,
            recommended_article=hyperlinked_article).save()

    # re-create existing recommended articles
    for article in existing_recommended_articles:
        if article not in article_list:
            ArticlePageRecommendedSections(
                page=main_article,
                recommended_article=article).save()


def convert_articles():
    '''
    Derived from https://github.com/wagtail/wagtail/issues/2110
    '''
    articles = ArticlePage.objects.all()

    for article in articles:
        stream_data = []
        linked_articles = []
        for block in article.body.stream_data:
            if block['type'] == 'page':
                try:
                    linked_articles.append(ArticlePage.objects.get(
                                           id=block['value']))
                except ObjectDoesNotExist:
                    logging.error(
                        ("[ERROR]: ArticlePage {0} with id {1} has "
                         "link to deleted article").format(
                            str(article.title),
                            str(article.id)))
            else:
                # add block to new stream_data
                stream_data.append(block)

        if linked_articles:
            create_recomended_articles(article, linked_articles)
            parent = article.get_parent().specific
            parent.enable_recommended_section = True
            parent.save()

        stream_block = article.body.stream_block
        article.body = StreamValue(stream_block, stream_data, is_lazy=True)
        article.save()


class Command(BaseCommand):
    help = ("Iterates through all articles in the database and moves any "
            "articles at the end of a StreamField to Recommended Articles.")

    def handle(self, **options):
        convert_articles()
