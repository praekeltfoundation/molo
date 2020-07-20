import os
import shutil
import zipfile
import re
import tempfile
import hashlib
import json
import distutils.dir_util

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from wagtail.core.utils import cautious_slugify
from wagtail.core.models import Page
from wagtail.images.models import Image

from molo.core.api.constants import KEYS_TO_EXCLUDE


def copy_translation_pages(page, new_page):
    from molo.core.models import Languages
    # Only copy translations for TranslatablePageMixin
    if not hasattr(page.specific, 'copy_language'):
        return 'Not translatable page'

    current_site = page.get_site()
    destination_site = new_page.get_site()
    if current_site is not destination_site and (page.depth > 2):
        page.specific.copy_language(current_site, destination_site)
    languages = Languages.for_site(destination_site).languages
    if languages.filter(is_main_language=True).exists():
        new_page.language = languages.filter(is_main_language=True).first()

    for translation in page.specific.translated_pages.all():
        new_lang = translation.specific.copy_language(
            current_site, destination_site)
        new_translation = translation.copy(
            to=new_page.get_parent())
        new_translation.language = new_lang
        new_translation.specific.translated_pages.add(new_page)
        new_page.specific.translated_pages.add(new_translation)
        new_page.save()
        new_translation.save()
        for translated_page in \
                page.specific.translated_pages.all():
            translations = page.specific.translated_pages.all().\
                exclude(language__pk=translated_page.language.pk)
            for translation in translations:
                translated_page.translated_pages.add(translation)
            translated_page.save()
        new_translation.save()


def create_new_article_relations(original_page, copied_page):
    from molo.core.models import ArticlePage, Tag, ArticlePageTags, \
        ArticlePageRecommendedSections, ArticlePageRelatedSections, \
        SectionPage, BannerPage

    if original_page and copied_page:
        if copied_page.get_descendants().count() >= \
                original_page.get_descendants().count():
            for article in ArticlePage.objects.descendant_of(
                    copied_page.get_site().root_page):

                # replace old tag with new tag in tag relations
                tag_relations = ArticlePageTags.objects.filter(page=article)
                for relation in tag_relations:
                    if relation.tag:
                        new_tag = Tag.objects.descendant_of(
                            copied_page.get_site().root_page).filter(
                                slug=relation.tag.slug).first()
                        relation.tag = new_tag
                        relation.save()

                # replace old recommended articles with new articles
                recommended_article_relations = \
                    ArticlePageRecommendedSections.objects.filter(page=article)
                for relation in recommended_article_relations:
                    if relation.recommended_article:
                        new_recommended_article = \
                            ArticlePage.objects.descendant_of(
                                copied_page.get_site().root_page).filter(
                                slug=relation.recommended_article.slug).first()
                        relation.recommended_article = new_recommended_article
                        relation.save()

                # replace old related sections with new sections
                related_section_relations = \
                    ArticlePageRelatedSections.objects.filter(page=article)
                for relation in related_section_relations:
                    if relation.section:
                        new_related_section = \
                            SectionPage.objects.descendant_of(
                                copied_page.get_site().root_page).filter(
                                slug=relation.section.slug).first()
                        relation.section = new_related_section
                        relation.save()

                # replace old article banner relations with new articles
            for banner in BannerPage.objects.descendant_of(
                    copied_page.get_site().root_page):
                if banner.banner_link_page:
                    old_page = Page.objects.filter(
                        pk=banner.banner_link_page.pk).first()
                    if old_page:
                        new_article = Page.objects.descendant_of(
                            copied_page.get_site().root_page).filter(
                            slug=old_page.slug).first()
                        banner.banner_link_page = new_article
                        banner.save()


def get_locale_code(language_code=None):
    return (language_code or settings.LANGUAGE_CODE).replace('_', '-')


RE_NUMERICAL_SUFFIX = re.compile(r'^[\w-]*-(\d+)+$')


def generate_slug(text, tail_number=0):
    from wagtail.core.models import Page
    """
    Returns a new unique slug. Object must provide a SlugField called slug.
    URL friendly slugs are generated using django.template.defaultfilters'
    slugify. Numbers are added to the end of slugs for uniqueness.

    based on implementation in jmbo.utils
    https://github.com/praekelt/jmbo/blob/develop/jmbo/utils/__init__.py
    """

    # Empty slugs are ugly (eg. '-1' may be generated) so force non-empty
    if not text:
        text = 'no-title'

    # use django slugify filter to slugify
    slug = cautious_slugify(text)[:255]

    values_list = Page.objects.filter(
        slug__startswith=slug
    ).values_list('id', 'slug')

    # Find highest suffix
    max = -1
    for tu in values_list:
        if tu[1] == slug:
            if max == -1:
                # Set max to indicate a collision
                max = 0

        # Update max if suffix is greater
        match = RE_NUMERICAL_SUFFIX.match(tu[1])
        if match is not None:
            i = int(match.group(1))
            if i > max:
                max = i

    if max >= 0:
        # There were collisions
        return "%s-%s" % (slug, max + 1)
    else:
        # No collisions
        return slug


def update_media_file(upload_file):
    '''
    Update the Current Media Folder.

    Returns list of files copied across or
    raises an exception.
    '''
    temp_directory = tempfile.mkdtemp()
    temp_file = tempfile.TemporaryFile()
    # assumes the zip file contains a directory called media
    temp_media_file = os.path.join(temp_directory, 'media')
    try:
        for chunk in upload_file.chunks():
            temp_file.write(chunk)

        with zipfile.ZipFile(temp_file, 'r') as z:
            z.extractall(temp_directory)

        if os.path.exists(temp_media_file):
            return distutils.dir_util.copy_tree(
                temp_media_file,
                settings.MEDIA_ROOT)
        else:
            raise Exception("Error: There is no directory called "
                            "'media' in the root of the zipped file")
    except Exception as e:
        raise e
    finally:
        temp_file.close()
        if os.path.exists(temp_directory):
            shutil.rmtree(temp_directory)


def get_image_hash(image):
    '''
    Returns an MD5 hash of the image file

    Handles images stored locally and on AWS

    I know this code is ugly.
    Please don't ask.
    The rabbit hole is deep.
    '''
    md5 = hashlib.md5()
    try:
        for chunk in image.file.chunks():
            md5.update(chunk)
        return md5.hexdigest()
    # this should only occur in tests
    except ValueError:
        # see link below for why we try not to use .open()
        # https://docs.djangoproject.com/en/1.9/ref/files/uploads/#django.core.files.uploadedfile.UploadedFile.chunks  # noqa
        image.file.open()

        for chunk in image.file.chunks():
            md5.update(chunk)
        return md5.hexdigest()
    finally:
        image.file.close()


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
        # TODO: remove dependence on KEYS_TO_INCLUDE
        if k not in KEYS_TO_EXCLUDE:
            if type(v) not in [type({}), type([])]:
                flat_fields.update({k: v})
            else:
                nested_fields.update({k: v})

    return flat_fields, nested_fields


def add_json_dump(field, nested_fields, page):
    if ((field in nested_fields) and
            nested_fields[field]):
        setattr(page, field, json.dumps(nested_fields[field]))


def add_stream_fields(nested_fields, page):
    if (('body' in nested_fields) and nested_fields['body']):
        article_body = nested_fields['body']

        # iterate through stream field, checking for page
        page_flag = False
        for stream_field in article_body:
            if 'type' in stream_field and stream_field['type']:
                # pass
                if (stream_field['type'] == 'page' or
                        stream_field['type'] == 'image'):
                    page_flag = True
                    break

        # if page link exists, do not attach body, instead return it
        if page_flag:
            return nested_fields['body']
        else:
            setattr(page, 'body', json.dumps(nested_fields['body']))
    return None


def add_list_of_things(field, nested_fields, page):
    if (field in nested_fields) and nested_fields[field]:
        attr = getattr(page, field)
        for item in nested_fields[field]:
            attr.add(item)


def attach_image(field, nested_fields, page, record_keeper=None):
    '''
    Returns a function that attaches an image to page if it exists

    Currenlty assumes that images have already been imported and info
    has been stored in record_keeper
    '''
    if (field in nested_fields) and nested_fields[field]:
        foreign_image_id = nested_fields[field]["id"]
        # Handle the following
        # record keeper may not exist
        # record keeper may not have image ref
        if record_keeper:
            try:
                local_image_id = record_keeper.get_local_image(
                    foreign_image_id)
                local_image = Image.objects.get(id=local_image_id)
                setattr(page, field, local_image)
            except ObjectDoesNotExist:
                raise ObjectDoesNotExist(
                    ("executing attach_image: local image referenced"
                     "in record_keeper does not actually exist."),
                    None)
            except Exception:
                raise
        else:
            raise Exception(
                ("Attempted to attach image without record_keeper. "
                 "This functionality is not yet implemented"))
