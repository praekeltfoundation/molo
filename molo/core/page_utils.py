import logging

from django.core.exceptions import ObjectDoesNotExist
from wagtail.core.models import Page
from wagtail.core.blocks import StreamValue
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


def seperate_end_page_links(stream_data):
    '''
    Seperate out page blocks at the end of a StreamField.

    Accepts: List of streamfield blocks
    Returns: Tuple of 2 lists of blocks - (remaining body, final article)
    '''
    stream_data_copy = list(stream_data)
    end_page_links = []

    for block in stream_data_copy[::-1]:
        if block['type'] == 'page':
            end_page_links.insert(0, block)
            stream_data_copy.pop()
        else:
            break

    return (stream_data_copy, end_page_links)


def get_page_ids_from_page_blocks(block_list):
    '''
    Extract ids from list of page blocks

    Accepts: list of stream blocks all with type 'page'
    Returns: list of page ids
    '''
    id_list = []
    for block in block_list:
        id_list.append(block['value'])
    return id_list


def get_pages_from_id_list(id_list):
    '''
    Accepts: list of page ids
    Returns: list of specific page objects
    '''
    page_list = []
    for id_ in id_list:
        try:
            page_list.append(
                Page.objects.get(id=id_).specific)
        except ObjectDoesNotExist:
            logging.error(
                "Attempted to fetch non-existent"
                " page with id of {}".format(id_))
    return page_list


def move_page_links_to_recommended_articles():
    '''
    Derived from https://github.com/wagtail/wagtail/issues/2110
    '''
    articles = ArticlePage.objects.all()

    for article in articles:
        (remaining_blocks, linked_article_blocks) = seperate_end_page_links(
            article.body.stream_data)

        if linked_article_blocks:
            linked_article_ids = get_page_ids_from_page_blocks(
                linked_article_blocks)
            linked_articles = get_pages_from_id_list(linked_article_ids)
            create_recomended_articles(article, linked_articles)
            parent = article.get_parent().specific
            parent.enable_recommended_section = True
            parent.save()

        stream_block = article.body.stream_block
        article.body = StreamValue(stream_block,
                                   remaining_blocks,
                                   is_lazy=True)
        article.save()
