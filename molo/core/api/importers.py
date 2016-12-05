"""
Various importers for the different content types
"""
import json
import requests
from io import BytesIO

from django.core.files.images import ImageFile

from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.models import Image

from molo.core.models import ArticlePage, SectionPage
from molo.core.api.constants import API_IMAGES_ENDPOINT, API_PAGES_ENDPOINT


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


def separate_fields(fields):
    """
    Non-foreign key fields can be mapped to new article instances
    directly. Foreign key fields require a bit more work.
    This method returns a tuple, of the same format:
    (flat fields, nested fields)
    """
    flat_fields = {}
    nested_fields = {}
    for k, v in fields.items():
        if type(v) not in [type({}), type([])]:
            flat_fields.update({k: v})
        else:
            nested_fields.update({k: v})

    return flat_fields, nested_fields


class PageImporter(object):

    def __init__(self, base_url=None, content=None, content_type=None):
        self._content_type = content_type
        self._fields = []
        self._content = content
        self._base_url = base_url

    def get_content_from_url(self, base_url):
        """
        Sections can have SectionPage and ArticlePage child objects.
        These have different fields, and thus have to be treated
        differently.
        """
        # assemble url
        base_url = base_url.rstrip("/")
        url = base_url + API_PAGES_ENDPOINT + "?type=" + self._content_type + \
            "&fields=" + ",".join(self._fields) + \
            "&order=latest_revision_created_at"

        # make request
        try:
            response = requests.get(url)
            self._base_url = base_url
            self._content = response.json()
            self._content = self._content["items"]
            return self._content
        except requests.exceptions.ConnectionError:
            return "No content could be found from {}. " \
                "Are you sure this is the correct URL?".format(base_url)
        except requests.exceptions.RequestException:
            return "Content could not be imported at this time. " \
                   "Please try again later."

    def content(self):
        if self._content:
            return self._content
        return []

    def save(self, indexes, parent_id):
        pass


class ArticlePageImporter(PageImporter):

    def __init__(self, base_url=None, content=None, content_type=None):
        super(ArticlePageImporter, self).__init__(
            base_url=base_url, content=content, content_type=content_type
        )
        self._content_type = "core.ArticlePage"
        self._fields = ArticlePage.get_api_fields()

    def save(self, indexes, parent_id):
        if self.content():
            parent = Page.objects.get(id=parent_id)
            for index in indexes:
                # Remove "id" and "meta" fields
                self.content()[index].pop("id")
                self.content()[index].pop("meta")
                fields, nested_fields = separate_fields(self.content()[index])
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
                        self._base_url, nested_fields["image"]["id"]
                    )

                parent.add_child(instance=article)
                parent.save_revision().publish()


class SectionPageImporter(PageImporter):

    def __init__(self, base_url=None, content=None, content_type=None):
        super(SectionPageImporter, self).__init__(
            base_url=base_url, content=content, content_type=content_type
        )
        self._content_type = "core.SectionPage"
        self._fields = SectionPage.get_api_fields()

    def save(self, indexes, parent_id):
        """
        Save the selected section. This will save the selected section
        as well as its direct child pages obtained through the ?child_of
        query parameter. The ?descendant_of query parameter is probably
         better suited because it all pages under that part of the tree will
         be obtained. The problem , however, is that that will require being
         able to traverse the tree and recreate parent-child relationships
         after they are imported
        """
        if self.content():
            parent = Page.objects.get(id=parent_id)

            # Get child articles pages
            url = self._base_url + API_PAGES_ENDPOINT + \
                "?child_of=" + str(indexes[0])
            response = requests.get(url)
            pages = response.json()
            children = pages["items"]

            # Save the selected section page
            response = requests.get(
                self._base_url + API_PAGES_ENDPOINT + str(indexes[0])
            )

            page = response.json()
            page.pop("id")
            page.pop("meta")
            flat_fields, nested_fields = separate_fields(page)
            section = SectionPage(**flat_fields)

            if ("image" in nested_fields) and nested_fields["image"]:
                section.image = get_image(
                    self._base_url, nested_fields["image"]["id"]
                )

            parent.add_child(instance=section)
            parent.save_revision().publish()

            # Save child pages to the newly imported SectionPage
            for page in children:
                item = requests.get(page["meta"]["detail_url"]).json()
                if item["meta"]["type"] == "core.SectionPage":
                    item.pop("id")
                    item.pop("meta")
                    flat_fields, nested_fields = separate_fields(item)
                    child_section = SectionPage(**flat_fields)

                    if ("image" in nested_fields) and nested_fields["image"]:
                        child_section.image = get_image(
                            self._base_url, nested_fields["image"]["id"]
                        )

                    section.add_child(instance=child_section)
                    section.save_revision().publish()
                elif item["meta"]["type"] == "core.ArticlePage":
                    item.pop("id")
                    item.pop("meta")
                    flat_fields, nested_fields = separate_fields(item)
                    child_article = ArticlePage(**flat_fields)
                    if ("tags" in nested_fields) and nested_fields["tags"]:
                        child_article.tags.add(
                            ", ".join(nested_fields["tags"])
                        )

                    if ("metadata_tags" in nested_fields) and \
                            nested_fields["metadata_tags"]:
                        child_article.metadata_tags.add(
                            ", ".join(nested_fields["metadata_tags"])
                        )

                    if ("body" in nested_fields) and nested_fields["body"]:
                        child_article.body = json.dumps(nested_fields["body"])

                    if ("image" in nested_fields) and nested_fields["image"]:
                        child_article.image = get_image(
                            self._base_url, nested_fields["image"]["id"]
                        )

                    section.add_child(instance=child_article)
                    section.save_revision().publish()
