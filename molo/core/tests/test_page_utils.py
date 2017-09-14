import json

from django.test import TestCase

from molo.core.tests.base import MoloTestCaseMixin
from molo.core.models import ArticlePageRecommendedSections
from molo.core.page_utils import (  # noqa
    move_page_links_to_recommended_articles,
    seperate_end_page_links,
    get_page_ids_from_page_blocks,
    get_pages_from_id_list,
)


def fake_page_stream_block(id_):
    return {
        "type": "page",
        "value": id_
    }


def fake_paragraph_stream_block():
    return {
        "type": "paragraph",
        "value": "paragraph content"
    }


class TestPageUtils(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.other_block_1 = fake_paragraph_stream_block()
        self.page_block_1 = fake_page_stream_block(1)
        self.page_block_2 = fake_page_stream_block(2)

    def test_seperate_end_page_links_1(self):
        test_stream = [
            self.other_block_1,
            self.page_block_1,
        ]

        (remaining_blocks, end_article_page_blocks) = seperate_end_page_links(test_stream)  # noqa

        self.assertEqual(remaining_blocks, [self.other_block_1])
        self.assertEqual(end_article_page_blocks, [self.page_block_1])

    def test_seperate_end_page_links_2(self):
        test_stream = [
            self.page_block_1,
            self.other_block_1,
        ]

        (remaining_blocks, end_article_page_blocks) = seperate_end_page_links(test_stream)  # noqa

        self.assertEqual(remaining_blocks, test_stream)
        self.assertEqual(end_article_page_blocks, [])

    def test_seperate_end_page_links_3(self):
        test_stream = [
            self.other_block_1,
            self.page_block_1,
            self.page_block_2,
        ]

        (remaining_blocks, end_article_page_blocks) = seperate_end_page_links(test_stream)  # noqa

        self.assertEqual(remaining_blocks, [self.other_block_1])
        self.assertEqual(
            end_article_page_blocks,
            [self.page_block_1,
             self.page_block_2])

    def test_get_page_ids_from_page_blocks(self):
        test_stream = [
            fake_page_stream_block(1),
            fake_page_stream_block(2),
            fake_page_stream_block(3),
        ]

        result = get_page_ids_from_page_blocks(test_stream)

        self.assertEqual(result, [1, 2, 3])

    def test_get_page_ids_from_page_blocks_empty_list(self):
        test_stream = []

        result = get_page_ids_from_page_blocks(test_stream)

        self.assertEqual(result, [])

    def test_get_pages_from_id_list(self):
        self.mk_main()
        [art1, art2, art3] = self.mk_articles(self.section_index, count=3)
        id_list = [art1.id, art2.id, art3.id]

        result = get_pages_from_id_list(id_list)

        self.assertEqual(result, [art1, art2, art3])

    def test_get_pages_from_id_list_empty_list(self):
        id_list = []

        result = get_pages_from_id_list(id_list)

        self.assertEquals(result, [])


class TestConvertingPageBlocksToRecommendedArticles(MoloTestCaseMixin, TestCase):  # noqa
    '''
    Test Cases:
    - page links to RA
    - end page links only
    - existing Recommended Articles
    '''
    def setUp(self):
        self.mk_main()

        self.linked_article = self.mk_article(self.section_index)
        self.main_article = self.mk_article(self.section_index)
        self.body = [fake_page_stream_block(self.linked_article.id)]
        setattr(self.main_article, 'body', json.dumps(self.body))
        self.main_article.save()

    def assert_recommended_article_equal(self, ra1, ra2):
        '''
        This function checks the page and recommended articles are the same

        It is necessary because RA Objects are destroyed and re-created
        during the conversion process.
        '''
        self.assertEqual(ra1.page.specific, ra2.page.specific)
        self.assertEqual(ra1.recommended_article.specific,
                         ra2.recommended_article.specific)

    def test_move_page_links_to_recommended_articles(self):

        self.assertEqual(self.main_article.body.stream_data, self.body)
        self.assertEqual(
            ArticlePageRecommendedSections.objects.count(), 0
        )

        move_page_links_to_recommended_articles()

        self.main_article.refresh_from_db()
        self.assertEqual(self.main_article.body.stream_data, [])
        self.assertEqual(
            ArticlePageRecommendedSections.objects.count(), 1)
        rec_art = ArticlePageRecommendedSections.objects.first()

        self.assertEqual(rec_art.page, self.main_article)
        self.assertEqual(rec_art.recommended_article.specific,
                         self.linked_article)

    def test_convert_article_body(self):
        '''
        Test that the existing recommended articles are preserved.
        '''
        linked_article_1 = self.mk_article(self.section_index,
                                           title="linked_article_1")
        linked_article_2 = self.mk_article(self.section_index,
                                           title="linked_article_2")

        rec_art1 = ArticlePageRecommendedSections.objects.create(
            page=self.main_article,
            recommended_article=linked_article_1)
        rec_art2 = ArticlePageRecommendedSections.objects.create(
            page=self.main_article,
            recommended_article=linked_article_2)
        self.assertEqual(ArticlePageRecommendedSections.objects.count(), 2)

        move_page_links_to_recommended_articles()

        self.main_article.refresh_from_db()
        self.assertEqual(self.main_article.body.stream_data, [])
        self.assertEqual(
            ArticlePageRecommendedSections.objects.count(), 3
        )

        rec_arts = list(self.main_article.recommended_articles.all())

        # check that ordering follows the pattern of linked articles
        # first, existing recommended articles afterwards
        self.assertEqual(rec_arts[0].page.specific, self.main_article)
        self.assertEqual(rec_arts[0].recommended_article.specific,
                         self.linked_article)
        self.assert_recommended_article_equal(rec_arts[1], rec_art1)
        self.assert_recommended_article_equal(rec_arts[2], rec_art2)

    def test_convert_article_body_no_duplicates(self):
        # create Rec Art object with the same linked page as
        # the embedded page link
        rec_art1 = ArticlePageRecommendedSections.objects.create(
            page=self.main_article,
            recommended_article=self.linked_article)

        self.assertEqual(
            ArticlePageRecommendedSections.objects.count(), 1)

        move_page_links_to_recommended_articles()

        self.assertEqual(
            ArticlePageRecommendedSections.objects.count(), 1)

        [rec_art] = self.main_article.recommended_articles.all()
        self.assert_recommended_article_equal(rec_art, rec_art1)
