from os.path import join

from django.test import TestCase, override_settings
from django.conf import settings

from wagtail.images.tests.utils import Image, get_test_image_file

from molo.core.models import ImageInfo
from molo.core.tests.base import MoloTestCaseMixin
from molo.core.tests.constants import TEST_IMAGE_HASH


@override_settings(MEDIA_ROOT=join(settings.PROJECT_ROOT, 'media'))
@override_settings(
    DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
class TestImageInfoObject(MoloTestCaseMixin, TestCase):
    def setUp(self):
        self.mk_main()

    def test_saving_image_creates_image_info(self):
        self.assertEqual(Image.objects.count(), 0)
        self.assertEqual(ImageInfo.objects.count(), 0)
        # creates the image which includes saving the image
        image = Image.objects.create(
            title="Test image",
            file=get_test_image_file(),
        )

        # post save of image should create the image info
        self.assertEqual(Image.objects.count(), 1)
        self.assertEqual(ImageInfo.objects.count(), 1)

        # check image hash in image info is correct
        image_info = ImageInfo.objects.first()
        self.assertEqual(image_info.image_hash, TEST_IMAGE_HASH)
        self.assertEqual(image_info.image, image)

    def test_attaching_image_info(self):
        # creates the image which includes saving the image
        image = Image.objects.create(
            title="Test image",
            file=get_test_image_file(),
        )
        self.assertEqual(ImageInfo.objects.count(), 1)
        image.image_info.delete()

        # deleting image info should not delete the image
        self.assertEqual(ImageInfo.objects.count(), 0)
        self.assertEqual(Image.objects.count(), 1)

        # add image info to image with no image info
        image_info = ImageInfo.objects.create(image=image)

        self.assertEqual(ImageInfo.objects.count(), 1)

        image_info.refresh_from_db()
        # check image hash in image info is correct
        self.assertEqual(image_info.image_hash, TEST_IMAGE_HASH)
        self.assertEqual(image_info.image, image)

    def test_attaching_image_info_save_image_twice(self):
        # creates the image which includes saving the image
        image = Image.objects.create(
            title="Test image",
            file=get_test_image_file(),
        )
        self.assertEqual(ImageInfo.objects.count(), 1)
        image.save()
        # confirm that we're not creating an ImageInfo
        # object each time
        self.assertEqual(ImageInfo.objects.count(), 1)

    def test_image_info_deleted_with_image(self):
        image = Image.objects.create(
            title="Test image",
            file=get_test_image_file(),
        )
        self.assertEqual(Image.objects.count(), 1)
        self.assertEqual(ImageInfo.objects.count(), 1)

        image.delete()

        self.assertEqual(Image.objects.count(), 0)
        self.assertEqual(ImageInfo.objects.count(), 0)

    def test_image_info_updated_on_file_change(self):
        file_1 = get_test_image_file(colour='black', size=(100, 100))
        file_2 = get_test_image_file(colour='white', size=(80, 80))

        image = Image.objects.create(
            title="Test image",
            file=file_1,
        )

        id_ = image.id
        original_hash = image.image_info.image_hash

        image.file = file_2
        image.save()

        updated_image = Image.objects.get(id=id_)

        new_hash = updated_image.image_info.image_hash

        self.assertNotEqual(
            original_hash,
            new_hash
        )
