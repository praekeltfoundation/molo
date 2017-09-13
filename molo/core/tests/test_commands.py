import json

from django.test import TestCase

from molo.core.tests.base import MoloTestCaseMixin
from molo.core.models import ArticlePageRecommendedSections
from molo.core.management.commands.move_page_links_to_recomended_articles import convert_articles  # noqa


def fake_page_stream_block(id_):
    return {
        "type": "page",
        "value": id_
    }


def fake_pragraph_stream_block():
    return {
        "type": "paragraph",
        "value": "paragraph content"
    }


class TestCommands(MoloTestCaseMixin, TestCase):
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
        This function check the page and recommended articles

        It is necessary because RA Objects are destroyed and re-created
        during
        '''
        self.assertEqual(ra1.page.specific, ra2.page.specific)
        self.assertEqual(ra1.recommended_article.specific,
                         ra2.recommended_article.specific)

    def test_convert_articles(self):

        self.assertEqual(self.main_article.body.stream_data, self.body)
        self.assertEqual(
            ArticlePageRecommendedSections.objects.count(), 0
        )

        convert_articles()

        self.main_article.refresh_from_db()
        self.assertEqual(self.main_article.body.stream_data, [])
        self.assertEqual(
            ArticlePageRecommendedSections.objects.count(), 1)
        rec_art = ArticlePageRecommendedSections.objects.first()

        self.assertEqual(rec_art.page, self.main_article)
        self.assertEqual(rec_art.recommended_article.specific,
                         self.linked_article)

    def test_convert_article_body_____(self):
        '''
        Test the existing recommended articles are preserved
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

        convert_articles()

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

        convert_articles()

        self.assertEqual(
            ArticlePageRecommendedSections.objects.count(), 1)

        [rec_art] = self.main_article.recommended_articles.all()
        self.assert_recommended_article_equal(rec_art, rec_art1)
