"""
Various importers for the different content types
"""
import json
import requests
from io import BytesIO

from django.core.files.images import ImageFile

from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.models import Image

from molo.core.models import ArticlePage
from molo.core.content_import.api.constants import (
    API_IMAGES_ENDPOINT, API_PAGES_ENDPOINT
)


class ArticlePageImporter(object):

    def __init__(self, content=None):
        self.content_type = "core.ArticlePage"
        self.fields = ArticlePage.get_api_fields()
        self.content = content
        self.base_url = None

    def get_content_from_url(self, base_url):
        # assemble url
        base_url = base_url.rstrip("/")
        url = base_url + API_PAGES_ENDPOINT + "?type=" + self.content_type + \
            "&order=latest_revision_created_at" + "&fields=" + ",".join(self.fields)

        # make request
        try:
            response = requests.get(url)
            self.base_url = base_url
            self.content = response.json()
            return self.content
        except requests.excpetions.ConnectionError:
            return "No content could be found from {}. " \
                "Are you sure this is the correct URL?".format(base_url)
        except requests.exceptions.RequestException:
            return "Content could not be imported at this time. Please try again later."

    def articles(self):
        if self.content:
            return self.content["pages"]
        return []

    def _separate_fields(self, fields):
        """
        Non-foreign key fields can be mapped to new article instances
        directly. Foreign key fields require a bit more work.
        This method returns a tuple, of the same format:
        (flat fields, nested fields)
        """
        flat_fields = {}
        for k, v in fields.items():
            if type(v) in [type({}), type([])]:
                pass
            else:
                flat_fields.update({k: v})
                del fields[k]
        return flat_fields, fields

    def _get_fields(self, id):
        if self.articles():
            self.articles()[id].pop("id")
            self.articles()[id].pop("meta")
            return self.articles()[id]
        return None

    def _get_related_image(self, id):
        image_attrs = requests.get(
            "http://localhost:8000/api/v2/images/" + str(id)
        ).json()
        image_file = requests.get("http://localhost:8000/media/images/iStock_67508687_SMALL_-_Copy.original.jpg")
        image = Image(
            title=image_attrs["title"],
            file=ImageFile(BytesIO(image_file.content), name=image_attrs["title"])
        )
        image.save()
        return image

    def save_articles(self, ids, parent_id):
        if self.articles():
            parent = Page.objects.get(id=parent_id)
            for article_id in ids:
                fields, nested_fields = self._separate_fields(
                    self._get_fields(article_id)
                )
                article = ArticlePage(**fields)
                # [u'metadata_tags', u'image', u'related_sections', u'body', u'tags']

                # process the nested fields
                if ("tags" in nested_fields) and nested_fields["tags"]:
                    article.tags.add(", ".join(nested_fields["tags"]))

                if ("metadata_tags" in nested_fields) and nested_fields["metadata_tags"]:
                    article.metadata_tags.add(", ".join(nested_fields["metadata_tags"]))

                if ("body" in nested_fields) and nested_fields["body"]:
                    article.body = json.dumps(nested_fields["body"])

                if ("image" in nested_fields) and nested_fields["image"]:
                    article.image = self._get_related_image(nested_fields["image"]["id"])

                parent.add_child(instance=article)
                parent.save_revision().publish()



