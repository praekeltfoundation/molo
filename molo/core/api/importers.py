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
    FooterPage,
    BannerPage,
    Tag,
    ArticlePageRecommendedSections,
    ArticlePageRelatedSections,
    PageTranslation,
    ArticlePageTags,
    SectionPageTags,
)
from molo.core.api.constants import (
    API_IMAGES_ENDPOINT, API_PAGES_ENDPOINT, KEYS_TO_EXCLUDE,
)
from molo.core.utils import get_image_hash

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


def list_of_objects_from_api(url):
        '''
        API only serves 20 pages by default
        This fetches info on all of items and return them as a list

        Assumption: limit of API is not less than 20
        '''
        response = requests.get(url)

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
                items = items + json.loads(paginated_response.content)["items"]
        return items


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


def record_foreign_key(field, record_keeper, id_key="id"):
    '''
    returns a function with the attributes necessary to replicate
    a foreign key relation
    '''
    def _record_foreign_key(nested_fields, page_id):
        if ((field in nested_fields) and nested_fields[field]):
            record_keeper[page_id] = nested_fields[field][id_key]
    return _record_foreign_key


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


def attach_image(field, image_map):
    '''
    Returns a function that attaches an image to page if it exists

    Assumes that images have already been imported
    otherwise will fail silently
    '''
    def _attach_image(nested_fields, page):
        if (field in nested_fields) and nested_fields[field]:
            foreign_image_id = nested_fields[field]["id"]
            try:
                local_image_id = image_map[foreign_image_id]
                local_image = Image.objects.get(id=local_image_id)
                setattr(page, field, local_image)
            except (KeyError, ObjectDoesNotExist):
                # TODO: log when page is not found
                pass
    return _attach_image


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
        if base_url[-1] == '/':
            self.base_url = base_url[:-1]
        else:
            self.base_url = base_url

        self.api_url = self.base_url + '/api/v2/'
        self.image_url = "{}images/".format(self.api_url)
        self.site_pk = site_pk
        self.language_setting, created = Languages.objects.get_or_create(
            site_id=self.site_pk)
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
        # maps local banner page id to foreign linked page id
        self.banner_page_links = {}

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
        self.record_banner_page_link = record_foreign_key(
            "banner_link_page",
            self.banner_page_links)

        self.add_article_body = add_json_dump("body")
        self.add_section_time = add_json_dump("time")

        self.add_tags = add_list_of_things("tags")
        self.add_metadata_tags = add_list_of_things("metadata_tags")

        self.attach_image = attach_image("image", self.image_map)
        self.attach_social_media_image = attach_image("social_media_image",
                                                      self.image_map)
        self.attach_banner_image = attach_image("banner", self.image_map)

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

        if not images:
            return None

        # store info about local images in order to match
        # with imported images
        local_image_hashes = {}
        image_width = {}
        image_height = {}

        for local_image in Image.objects.all():
            local_image_hashes[get_image_hash(local_image)] = local_image

            if local_image.width in image_width:
                image_width[local_image.width].append(local_image)
            else:
                image_width[local_image.width] = [local_image]

            if local_image.height in image_height:
                image_height[local_image.height].append(local_image)
            else:
                image_height[local_image.height] = [local_image]

        # iterate through foreign images
        for image in images:
            image_detail_url = "{}{}/".format(self.image_url, image["id"])
            img_response = requests.get(image_detail_url)
            img_info = json.loads(img_response.content)

            if img_info["image_hash"] is None:
                raise ValueError('image hash should not be none')

            # check if a replica exists
            if img_info["width"] in image_width:
                possible_matches = image_width[img_info["width"]]
                if img_info["height"] in image_height:
                    possible_matches = list(
                        set(image_height[img_info["height"]] +
                            possible_matches))
                    if img_info["image_hash"] in local_image_hashes:
                        result = list(
                            set([local_image_hashes[img_info["image_hash"]]] +
                                possible_matches))
                        # edge case where we have more than one match
                        result = result[0]

                        # use the local title of the image
                        self.image_map[image["id"]] = result.id
                        # LOG THIS
                        continue

            new_image = self.fetch_and_create_image(
                img_info['image_url'],
                img_info["title"])
            self.image_map[image["id"]] = new_image.id

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

    def create_translated_content(self, local_main_lang_page,
                                  content, locale):
        '''
        Wrapper for  create_content

        Creates the content
        Then attaches a language relation from the main language page to the
        newly created Page
        Note: we get the parent from the main language page
        '''
        page = self.create_page(local_main_lang_page.get_parent(), content)

        language = SiteLanguageRelation.objects.get(
            language_setting=self.language_setting, locale=locale)
        language_relation = page.languages.first()
        language_relation.language = language
        language_relation.save()
        page.save_revision().publish()
        PageTranslation.objects.get_or_create(
            page=local_main_lang_page,
            translated_page=page)
        return page

    def create_page(self, parent, content):
        fields, nested_fields = separate_fields(content)

        # handle the unwanted fields
        foreign_id = content.pop('id')
        # ignore when article was last revised
        if 'latest_revision_created_at' in content:
            content.pop('latest_revision_created_at')

        page = None
        if content["meta"]["type"] == "core.SectionPage":
            page = SectionPage(**fields)
        elif content["meta"]["type"] == "core.ArticlePage":
            page = ArticlePage(**fields)
        elif content["meta"]["type"] == "core.FooterPage":
            page = FooterPage(**fields)
        elif content["meta"]["type"] == "core.BannerPage":
            page = BannerPage(**fields)
        elif content["meta"]["type"] == "core.Tag":
            page = Tag(**fields)

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
        self.record_banner_page_link(nested_fields, page.id)

        self.add_article_body(nested_fields, page)
        self.add_section_time(nested_fields, page)

        self.add_tags(nested_fields, page)
        self.add_metadata_tags(nested_fields, page)

        self.attach_image(nested_fields, page)
        self.attach_social_media_image(nested_fields, page)
        self.attach_banner_image(nested_fields, page)

        # note that unpublished pages will be published
        page.save_revision().publish()
        return page

    def create_recommended_articles(self):
        # iterate through articles with recomended articles
        for article_id, foreign_rec_article_id_list in self.recommended_articles.iteritems():  # noqa

            main_article = ArticlePage.objects.get(id=article_id)
            for foreign_rec_article_id in foreign_rec_article_id_list:
                local_version_page_id = self.id_map[foreign_rec_article_id]
                rec_article = ArticlePage.objects.get(id=local_version_page_id)

                ArticlePageRecommendedSections(
                    page=main_article,
                    recommended_article=rec_article
                ).save()

    def create_related_sections(self):
        # iterate through articles with related sections
        for article_id, foreign_rel_section_id_list in self.related_sections.iteritems():  # noqa

            main_article = ArticlePage.objects.get(id=article_id)
            for foreign_rel_section_id in foreign_rel_section_id_list:
                local_version_page_id = self.id_map[foreign_rel_section_id]
                rel_section = SectionPage.objects.get(id=local_version_page_id)

                ArticlePageRelatedSections(
                    page=main_article,
                    section=rel_section
                ).save()

    def create_nav_tag_relationships(self):
        for page_id, foreign_tags_id_list in self.nav_tags.iteritems():
            page = Page.objects.get(id=page_id).specific
            for foreign_tag_id in foreign_tags_id_list:
                local_tag_id = self.id_map[foreign_tag_id]
                tag = Tag.objects.get(id=local_tag_id)

                ArticlePageTags(
                    page=page,
                    tag=tag
                ).save()

    def create_section_tag_relationship(self):
        for page_id, foreign_tags_id_list in self.section_tags.iteritems():
            page = Page.objects.get(id=page_id).specific
            for foreign_tag_id in foreign_tags_id_list:
                local_tag_id = self.id_map[foreign_tag_id]
                tag = Tag.objects.get(id=local_tag_id)

                SectionPageTags(
                    page=page,
                    tag=tag
                ).save()

    def create_banner_page_links(self):
        for banner_page_id, linked_page_foreign_id in self.banner_page_links.iteritems():  # noqa
            banner = BannerPage.objects.get(id=banner_page_id)
            local_id = self.id_map[linked_page_foreign_id]
            linked_page = Page.objects.get(id=local_id).specific
            banner.banner_link_page = linked_page
            banner.save_revision().publish()

    def get_foreign_page_id_from_type(self, page_type):
        '''
        Get the foreign page id based on type

        Only works for index pages
        '''
        response = requests.get("{}pages/?type={}".format(
            self.api_url, page_type))
        content = json.loads(response.content)
        return content["items"][0]["id"]

    def copy_children(self, foreign_id, existing_node):
        '''
        Initiates copying of tree, with existing_node acting as root
        '''
        url = "{}/api/v2/pages/{}/".format(self.base_url, foreign_id)

        response = requests.get(url)
        content = json.loads(response.content)

        main_language_child_ids = content["meta"]["main_language_children"]
        for main_language_child_id in main_language_child_ids:
                self.copy_page_and_children(foreign_id=main_language_child_id,
                                            parent_id=existing_node.id)

    def copy_page_and_children(self, foreign_id, parent_id):
        '''
        Recusively copies over pages, their translations and child pages
        '''
        url = "{}/api/v2/pages/{}/".format(self.base_url, foreign_id)

        # TODO handle connection errors
        response = requests.get(url)
        content = json.loads(response.content)

        parent = Page.objects.get(id=parent_id).specific
        page = self.create_page(parent, content)

        # create translations
        if content["meta"]["translations"]:
            for translation_obj in content["meta"]["translations"]:
                _url = "{}/api/v2/pages/{}/".format(self.base_url,
                                                    translation_obj["id"])
                _response = requests.get(_url)
                _content = json.loads(_response.content)

                self.create_translated_content(
                    page, _content, translation_obj["locale"])

        main_language_child_ids = content["meta"]["main_language_children"]

        # recursively iterate through child nodes
        if main_language_child_ids:
            for main_language_child_id in main_language_child_ids:
                self.copy_page_and_children(foreign_id=main_language_child_id,
                                            parent_id=page.id)
