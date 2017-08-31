from django.test import TestCase

from wagtail.wagtailimages.tests.utils import Image, get_test_image_file

from molo.core.models import ImageInfo
from molo.core.tests.base import MoloTestCaseMixin


class TestImportableMixin(MoloTestCaseMixin, TestCase):
    def setUp(self):
        self.mk_main()

    def test_saving_image_creates_image_info(self):
        self.assertEquals(Image.objects.count(), 0)
        self.assertEquals(ImageInfo.objects.count(), 0)
        # creates the image which includes saving the image
        image = Image.objects.create(
            title="Test image",
            file=get_test_image_file(),
        )

        # post save of image should create the image info
        self.assertEquals(Image.objects.count(), 1)
        self.assertEquals(ImageInfo.objects.count(), 1)

        # check image hash in image info is correct
        image_info = ImageInfo.objects.first()
        self.assertEquals(image_info.image_hash, '0000000000000000')
        self.assertEquals(image_info.image, image)
