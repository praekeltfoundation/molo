"""
Various importers for the different content types
"""
import requests

from molo.core.models import ArticlePage, SectionPage


class ArticlePageImporter(object):

    def __init__(self):
        self.content_type = "core.ArticlePage"
        self.fields = ArticlePage.get_api_fields()
        self.content = None

    def get_content_from_url(self, base_url=None):
        url = base_url + "?type=" + self.content_type + \
            "&order=latest_revision_created_at" + "&fields=" + ",".join(self.fields)
        response = requests.get(url)
        self.content = response.json()
        return self.content

    def articles(self):
        if self.content:
            return self.content["pages"]
        return []

    def _available_sections(self):
        # ArticlePage objects can only be added to SectionPages. It's thus
        # required that a list of available sections is obtained. If
        # there are no SectionPages, then ArticlePages cannot be created.
        sections = SectionPage.objects.all()
        return sections

    def _get_fields(self, id):
        if self.articles():
            self.articles()[id].pop("id")
            self.articles()[id].pop("meta")
            return self.articles()[id]
        return None

    def save_articles(self, ids):
        if self.articles():
            for id in ids:
                fields = self._get_fields(id)
                article = ArticlePage(fields)