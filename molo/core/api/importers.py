"""
Various importers for the different content types
"""
import math
import json
import requests
from io import BytesIO

from django.core.files.images import ImageFile

from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.models import Image

from molo.core.models import (
    Languages,
    SiteLanguageRelation,
    ArticlePage,
    SectionPage,
)
from molo.core.api.constants import (
    API_IMAGES_ENDPOINT, API_PAGES_ENDPOINT, KEYS_TO_EXCLUDE,
)

from django.core.exceptions import ObjectDoesNotExist


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

    # exclude "id" and "meta" elements
    for k, v in fields.items():
        if k not in KEYS_TO_EXCLUDE:
            if type(v) not in [type({}), type([])]:
                flat_fields.update({k: v})
            else:
                nested_fields.update({k: v})

    return flat_fields, nested_fields

from pprint import pprint
def list_of_objects_from_api(url):
        '''
        API only serves 20 pages by default
        This fetches info on all of items and return them as a list

        Assumption: limit of API is not less than 20
        '''
        response = requests.get(url)
        pprint("response")
        pprint(response)
        print("&&&&&&&&&&&&&&&&")
        pprint("response.content")
        pprint(response.content)
        pprint(type(response.content))

        content = json.loads(response.content)
        count = content["meta"]["total_count"]

        if count <= 20:
            return content["items"]
        else:
            items = [] + content["items"]
            num_requests = int(math.ceil(count // 20))

            for i in range(1, num_requests + 1):
                paginated_url = "{}?limit=20&offset={}".format(
                    url, str(i * 20))
                paginated_response = requests.get(paginated_url)
                items = items + list(json.loads(paginated_response.content)["items"])
        return items


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
                selected_article = self.content()[index]
                fields, nested_fields = separate_fields(selected_article)
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

    def _save_item(self, item, parent):
        if item["meta"]["type"] == "core.SectionPage":
            flat_fields, nested_fields = separate_fields(item)
            child_section = SectionPage(**flat_fields)

            if ("image" in nested_fields) and nested_fields["image"]:
                child_section.image = get_image(
                    self._base_url, nested_fields["image"]["id"]
                )

            parent.add_child(instance=child_section)
            parent.save_revision().publish()
            return child_section

        elif item["meta"]["type"] == "core.ArticlePage":
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

            parent.add_child(instance=child_article)
            parent.save_revision().publish()
            return child_article

    def process_child_section(self, id, parent):
        response = requests.get(
            self._base_url + API_PAGES_ENDPOINT + str(id)
        ).json()
        ancestor = self._save_item(response, parent)
        if response["meta"]["children"]:
            for child_id in response["meta"]["children"]["items"]:
                self.process_child_section(child_id, ancestor)
        return ancestor

    def recursive_children(self, node):
        results = [node['id']]
        if len(node['children']) > 0:
            for child in node['children']:
                results.extend(self.recursive_children(child))
        return results

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

            # Save the selected section page
            response = requests.get(
                self._base_url + API_PAGES_ENDPOINT + str(indexes[0]) + "/"
            )

            section_page = response.json()
            self.process_child_section(section_page["id"], parent)


class SiteImporter(object):

    def __init__(self, site_pk, base_url=''):
        self.base_url = base_url
        self.api_url = self.base_url + '/api/v2/'
        self.image_url = "{}images/".format(self.api_url)
        self.site_pk = site_pk
        self.content = None
        # maps foreign IDs to local page IDs
        self.id_map = {}
        # maps foreign image IDs to local IDs
        self.image_map = {}
        # maps local id to list of foreign section page ids
        self.related_sections = {}
        # maps local id to list of foreign page ids
        self.recommended_articles = {}
        # maps local pages to list of foreign reaction question IDs
        self.reaction_questions = {}
        # maps local pages to list of foreign nav_tag IDs
        self.nav_tags = {}
        # maps local pages to list of foreign section_tag IDs
        self.section_tags = {}

    def get_language_ids(self):
        language_url = "{}{}/".format(self.api_url, "languages")
        response = requests.get(language_url)

        language_ids = []
        # TODO: handle broken case
        for language in json.loads(response.content)["items"]:
            language_ids.append(language["id"])
        return language_ids

    def copy_site_languages(self):
        language_foreign_ids = self.get_language_ids()
        language_setting, created = Languages.objects.get_or_create(
            site_id=self.site_pk)
        for foreign_id in language_foreign_ids:
            language_url = "{}{}/{}/".format(self.api_url,
                                             "languages",
                                             foreign_id)
            response = requests.get(language_url)
            content = json.loads(response.content)

            # TODO: review whether this works with Multi-site
            # TODO: handle case where Main lang is not first
            sle, created = SiteLanguageRelation.objects.get_or_create(
                locale=content['locale'],
                is_active=content['is_active'],
                language_setting=language_setting)

    def import_images(self):
        '''
        Fetches images from site

        Attempts to avoid duplicates by matching image titles
        if a match is found it refers to local instance instead
        if it is not, the image is fetched, created and referenced
        '''
        images = list_of_objects_from_api(self.image_url)

        for image in images:
            image_detail_url = "{}{}/".format(self.image_url, image["id"])
            img_response = requests.get(image_detail_url)
            img_info = json.loads(img_response.content)

            local_image = None

            try:
                local_image = Image.objects.get(title=img_info['title'])
                # do not import image
                # update images references to point to existing image
            except ObjectDoesNotExist:
                # import the image
                local_image = self.fetch_and_create_image(
                    img_info['image_url'],
                    img_info["title"])

            self.image_map[image["id"]] = local_image.id

    def fetch_and_create_image(self, relative_url, image_title):
        '''
        fetches, creates and return image object
        '''
        # TODO: handle image unavailable
        image_media_url = "{}{}".format(self.base_url, relative_url)
        image_file = requests.get(image_media_url)
        local_image = Image(
            title=image_title,
            file=ImageFile(
                BytesIO(image_file.content), name=image_title
            )
        )
        local_image.save()
        return local_image

    def attach_image(self):
        # if not (image has already been imported)
        #   get_image()
        # attach image
        pass

    def create_page(self, parent, content):
        fields, nested_fields = separate_fields(content)

        # handle the unwanted fields
        foreign_id = content.pop('id')

        page = None
        if content["meta"]["type"] == "core.SectionPage":
            page = SectionPage(**fields)
        elif content["meta"]["type"] == "core.ArticlePage":
            page = ArticlePage(**fields)
        # TODO: handle other Page types

        parent.add_child(instance=page)

        # TODO: handle live/published
        # Need to review this line:
        #   handle drafts and 'not live' content
        parent.save_revision().publish()

        self.id_map[foreign_id] = page.id

        # time
        if (("time" in nested_fields) and
                nested_fields["time"]):
            page.time = json.dumps(nested_fields["time"])

        # section_tags/nav_tags
        #  list -> ["tag"]["id"]
        # -> Need to fetch and create the nav tags
        #  THEN create the link between page and nav_tag
        if (("section_tags" in nested_fields) and
                nested_fields["section_tags"]):
            self.section_tags[page.id] = []
            for section_tag in nested_fields["section_tags"]:
                self.section_tags[page.id].append(
                    section_tag["tag"]["id"])

        # nav_tags
        #  list -> ["tag"]["id"]
        # -> Need to fetch and create the nav tags
        #  THEN create the link between page and nav_tag
        if (("nav_tags" in nested_fields) and
                nested_fields["nav_tags"]):
            self.nav_tags[page.id] = []
            for nav_tag in nested_fields["nav_tags"]:
                self.nav_tags[page.id].append(
                    nav_tag["tag"]["id"])

        # reaction_questions
        #  list -> ["reaction_question"]["id"]
        # -> Need to fetch and create the reaction questions
        #  THEN create the link between page and reaction question
        if (("reaction_questions" in nested_fields) and
                nested_fields["reaction_questions"]):
            self.reaction_questions[page.id] = []
            for reaction_question in nested_fields["reaction_questions"]:
                self.reaction_questions[page.id].append(
                    reaction_question["reaction_question"]["id"])

        # recommended_articles
        #  list -> ["recommended_article"]["id"]
        # -> Only need to create the relationship
        if (("recommended_articles" in nested_fields) and
                nested_fields["recommended_articles"]):
            self.recommended_articles[page.id] = []
            for recommended_article in nested_fields["recommended_articles"]:
                self.recommended_articles[page.id].append(
                    recommended_article["recommended_article"]["id"])

        # related_sections
        #  list -> ["section"]["id"]
        # -> Only need to create the relationship
        if (("related_sections" in nested_fields) and
                nested_fields["related_sections"]):
            self.related_sections[page.id] = []
            for related_section in nested_fields["related_sections"]:
                self.related_sections[page.id].append(
                    related_section["section"]["id"])

        if ("body" in nested_fields) and nested_fields["body"]:
            page.body = json.dumps(nested_fields["body"])

        if ("tags" in nested_fields) and nested_fields["tags"]:
            for tag in nested_fields["tags"]:
                page.tags.add(tag)

        if (("metadata_tags" in nested_fields) and
                nested_fields["metadata_tags"]):
            for tag in nested_fields["metadata_tags"]:
                page.metadata_tags.add(tag)

        if (("social_media_image" in nested_fields) and
                nested_fields["social_media_image"]):
            self.attach_image()

        if ("image" in nested_fields) and nested_fields["image"]:
            self.attach_image()

        # update the state of the page ?
        page.save()
        return page
