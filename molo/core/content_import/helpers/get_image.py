import requests

from urlparse import urljoin

from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from wagtail.wagtailimages import get_image_model

Image = get_image_model()


def get_image_file(host, uuid):
    thumbor_image = get_thumbor_image_file(host, uuid)
    if thumbor_image:
        image, _ = Image.objects.get_or_create(title=uuid, defaults={
            'file': thumbor_image
        })
        return image
    return None


def get_thumbor_image_file(host, uuid):
        url = urljoin(host, 'image/%s' % uuid)
        response = requests.get(url)
        if response.status_code == 200:
            return ImageFile(ContentFile(response.content), name=uuid)
        return None
