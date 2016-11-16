"""
Various importers for the different content types
"""
import requests

from molo.core.models import ArticlePage


class ArticlePageImporter(object):

    def __init__(self):
        self.content_type = "core.ArticlePage"
        self.fields = ArticlePage.get_api_fields()

    def get_content_from_url(self, base_url=None):
        url = base_url + "?type=" + self.content_type + \
            "&order=latest_revision_created_at" + "&fields=" + ",".join(self.fields)
        response = requests.get(url)
        return response.json()
