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
from molo.core.api.constants import API_IMAGES_ENDPOINT, API_PAGES_ENDPOINT


#====================================================
# functions used to find images
def get_image_attributes(base_url, image_id):
    image_attrs = requests.get(
        base_url + API_IMAGES_ENDPOINT + str(image_id)
    ).json()
    return image_attrs


def get_image(base_url, image_id):
    # TODO: guard against non-existent images
    image_attributes = get_image_attributes(base_url, image_id)
    image_file = requests.get(image_attributes["file"])
    image = Image(
        title=image_attributes["title"],
        file=ImageFile(
            BytesIO(image_file.content), name=image_attributes["title"]
        )
    )
    image.save()
    return image


class ArticlePageImporter(object):

    def __init__(self, base_url=None, content=None):
        self.content_type = "core.ArticlePage"
        self.fields = ArticlePage.get_api_fields()
        self.content = content
        self.base_url = base_url

    def get_content_from_url(self, base_url):
        # assemble url
        base_url = base_url.rstrip("/")
        url = base_url + API_PAGES_ENDPOINT + "?type=" + self.content_type + \
            "&fields=" + ",".join(self.fields) + \
            "&order=latest_revision_created_at"

        # make request
        try:
            response = requests.get(url)
            self.base_url = base_url
            self.content = response.json()
            return self.content
        except requests.exceptions.ConnectionError:
            return "No content could be found from {}. " \
                "Are you sure this is the correct URL?".format(base_url)
        except requests.exceptions.RequestException:
            return "Content could not be imported at this time. " \
                   "Please try again later."

    def articles(self):
        if self.content:
            return self.content["items"]
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
            if type(v) not in [type({}), type([])]:
                flat_fields.update({k: v})
                del fields[k]

        return flat_fields, fields

    def _get_fields(self, index):
        if self.articles():
            # remove the fields we do not need, i.e. "id" and "meta"
            if "id" in self.articles()[index]:
                self.articles()[index].pop("id")

            if "meta" in self.articles()[index]:
                self.articles()[index].pop("meta")

            return self.articles()[index]

        return None

    def save_articles(self, article_indexes, parent_id):
        if self.articles():
            parent = Page.objects.get(id=parent_id)
            for index in article_indexes:
                fields, nested_fields = self._separate_fields(
                    self._get_fields(index)
                )
                article = ArticlePage(**fields)

                # TODO: u'related_sections'
                # process the nested fields
                if ("tags" in nested_fields) and nested_fields["tags"]:
                    article.tags.add(", ".join(nested_fields["tags"]))

                if ("metadata_tags" in nested_fields) and \
                        nested_fields["metadata_tags"]:
                    article.metadata_tags.add(
                        ", ".join(nested_fields["metadata_tags"])
                    )

                if ("body" in nested_fields) and nested_fields["body"]:
                    article.body = json.dumps(nested_fields["body"])

                if ("image" in nested_fields) and nested_fields["image"]:
                    article.image = get_image(
                        self.base_url, nested_fields["image"]["id"]
                    )

                parent.add_child(instance=article)
                parent.save_revision().publish()
