from collections import OrderedDict

from rest_framework.fields import Field
from wagtail.wagtailcore.models import Site
from wagtail.wagtailimages.models import SourceImageIOError

from molo.core.content_import.api.compat import ImageSerializer


def get_main_site_root_url():
    for site_id, root_path, root_url in Site.get_site_root_paths():
        if root_path == '/home/':
            return root_url


class ImageRenditionField(Field):
    """
    A field that generates a rendition with the specified filter spec, and serialises
    details of that rendition.

    Example:
    "thumbnail": {
        "url": "http://rca.ac.uk/media/images/myimage.max-165x165.jpg",
        "width": 165,
        "height": 100
    }

    If there is an error with the source image. The dict will only contain a single
    key, "error", indicating this error:

    "thumbnail": {
        "error": "SourceImageIOError"
    }
    """
    def __init__(self, filter_spec, *args, **kwargs):
        self.filter_spec = filter_spec
        super(ImageRenditionField, self).__init__(*args, **kwargs)

    def get_attribute(self, instance):
        return instance

    def to_representation(self, image):
        try:
            file = image.get_rendition(self.filter_spec)
            root_url = get_main_site_root_url()

            return OrderedDict([
                ('url', root_url + file.url),
                # ('width', file.width),
                # ('height', file.height),
            ])
        except SourceImageIOError:
            return OrderedDict([
                ('error', 'SourceImageIOError'),
            ])


class MoloImageSerializer(ImageSerializer):
    file = ImageRenditionField('original', read_only=True)
    original = ImageRenditionField('max-165x165', read_only=True)
