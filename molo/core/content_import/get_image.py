import requests

from urlparse import urljoin

from django.core.files.base import ContentFile

from wagtail.wagtailimages.tests.utils import Image


def get_image(host, uuid):
    image = Image.objects.create(
        title='test.png',
        file=get_image_file(host, uuid),
    )
    return image


def get_image_file(host, uuid):
    file_obj, content_type = get_thumbor_image_file(host, uuid)


def get_thumbor_image_file(host, uuid):
        url = urljoin(host, 'image/%s' % uuid)
        response = requests.get(url)
        if response.status_code == 200:
            return (
                ContentFile(response.content),
                response.headers['Content-Type'])
        return None, None
