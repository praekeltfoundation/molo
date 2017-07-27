"""
Various importers for the different content types
"""
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


def record_foreign_relation(field, key, record_keeper, id_key="id"):
    '''
    returns a function with the attributes necessary to
    correctly reference the necessary objects, to correctly record
    the relationship between a page and its foreign foreign-key pages
    '''
    def record_relationship(nested_fields, page_id):
        if ((field in nested_fields) and nested_fields[field]):
            record_keeper[page_id] = []
            for thing in nested_fields[field]:
                record_keeper[page_id].append(thing[key][id_key])
    return record_relationship


def add_json_dump(field):
    def _add_json_dump(nested_fields, page):
        if ((field in nested_fields) and
                nested_fields[field]):
            setattr(page, field, json.dumps(nested_fields[field]))
    return _add_json_dump


def add_list_of_things(field):
    def _add_list_of_things(nested_fields, page):
        if (field in nested_fields) and nested_fields[field]:
            attr = getattr(page, field)
            for item in nested_fields[field]:
                attr.add(item)
    return _add_list_of_things


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

        self.record_recommended_articles = record_foreign_relation(
            "recommended_articles", "recommended_article",
            self.recommended_articles)
        self.record_section_tags = record_foreign_relation(
            "section_tags", "tag",
            self.section_tags)
        self.record_nav_tags = record_foreign_relation(
            "nav_tags", "tag",
            self.nav_tags)
        self.record_reaction_questions = record_foreign_relation(
            "reaction_questions", "reaction_question",
            self.reaction_questions)
        self.record_related_sections = record_foreign_relation(
            "related_sections", "section",
            self.related_sections)

        self.add_article_body = add_json_dump("body")
        self.add_section_time = add_json_dump("time")

        self.add_tags = add_list_of_things("tags")
        self.add_metadata_tags = add_list_of_things("metadata_tags")

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

    def fetch_and_create_image(self):
        # create image object
        # update self.image_map
        # return image
        pass

    def attach_image(self):
        # if not (image has already been imported)
        #   get_image()
        # attach image
        pass

    def create_page(self, parent, content):
        fields, nested_fields = separate_fields(content)

        # handle the unwanted fields
        foreign_id = content.pop('id')
        # ignore when article was last revised
        content.pop('latest_revision_created_at')

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

        self.record_section_tags(nested_fields, page.id)
        self.record_nav_tags(nested_fields, page.id)
        self.record_reaction_questions(nested_fields, page.id)
        self.record_recommended_articles(nested_fields, page.id)
        self.record_related_sections(nested_fields, page.id)

        self.add_article_body(nested_fields, page)
        self.add_section_time(nested_fields, page)

        self.add_tags(nested_fields, page)
        self.add_metadata_tags(nested_fields, page)

        if (("social_media_image" in nested_fields) and
                nested_fields["social_media_image"]):
            self.attach_image()

        if ("image" in nested_fields) and nested_fields["image"]:
            self.attach_image()

        # note that unpublished pages will be published
        page.save_revision().publish()
        return page
