from collections import OrderedDict

from rest_framework import serializers

from wagtail.api.v2.serializers import PageSerializer
from wagtail.images.api.v2.serializers import ImageSerializer

from molo.core.models import TranslatablePageMixinNotRoutable, ImageInfo


class PageChildrenField(serializers.Field):
    """
    Serializes the "children" field.

    Example:
    "children": {
        "count": 1,
        "listing_url": "/api/v1/pages/?child_of=2"
    }
    """
    def get_attribute(self, instance):
        return instance

    def to_representation(self, page):
        if page.get_children():
            items = []
            for item in page.get_children():
                items.append(item.id)
            return OrderedDict([
                ("items", items),
            ])


class MainLanguageChildrenField(serializers.Field):
    """
    Serializes the "children" field with only children that belong
    to the main language.

    Example:
    "children": [12, 34]
    """
    def get_attribute(self, instance):
        return instance

    def to_representation(self, page):
        if page.get_children():
            return [child_page.id for child_page
                    in page.get_children()
                    if not hasattr(child_page.specific, 'source_page')]


class PageTranslationsField(serializers.Field):
    """
    Serializes the "translations" field.

    If the Page is translatable, it will return all of the translated
    versions of the page, including the main lanugage page. It will
    exclude the original page id from the list.

    Edge case: a translated version of a page may subsequenly have its
    language deleted, leaving the page. In this case, the locale field
    will display None.

    Example:
    "translations": [
        {
            "locale": "ve",
            "id": 24
        },
        {
            "locale": "fr",
            "id": 25
        }
    ]

    """
    def get_attribute(self, instance):
        return instance

    def to_representation(self, page):
        if isinstance(page.specific, TranslatablePageMixinNotRoutable):
            main_page = page.specific.get_main_language_page().specific
            items = []

            if page.specific == main_page:
                pages = [page_relation.translated_page.specific
                         for page_relation in main_page.translations.all()]
            else:
                pages = ([main_page] +
                         [page_relation.translated_page.specific
                         for page_relation in main_page.translations.all()
                         if page_relation.translated_page.id != page.id])

            for translated_page in pages:
                locale = None
                try:
                    locale = translated_page.languages.get().language.locale
                except:
                    pass

                items.append({
                    "id": translated_page.id,
                    "locale": locale
                })
            return items
        else:
            return None


class MoloPageSerializer(PageSerializer):
    children = PageChildrenField(read_only=True)
    translations = PageTranslationsField(read_only=True)
    main_language_children = MainLanguageChildrenField(read_only=True)


class ImageUrlField(serializers.Field):
    """
    Provides an accesible URL for image file
    """
    def get_attribute(self, instance):
        return instance

    def to_representation(self, image):
        rendition = image.get_rendition('original')
        return rendition.url


class ImageFileHashField(serializers.Field):
    """
    Provides an accesible URL for image file
    """
    def get_attribute(self, instance):
        return instance

    def to_representation(self, image):
        if not hasattr(image, 'image_info'):
            ImageInfo.objects.create(image=image)

        image.refresh_from_db()

        return image.image_info.image_hash


class MoloImageSerializer(ImageSerializer):
    image_url = ImageUrlField(read_only=True)
    image_hash = ImageFileHashField(read_only=True)
