from django.core.files.base import ContentFile
from django.test import TestCase, Client
from six import b

from molo.core.tests.base import MoloTestCaseMixin
from molo.core.models import MoloMedia, SiteLanguageRelation, Main, Languages


class MultimediaViewTest(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)
        self.client = Client()

    def add_media(self, media_type):
        fake_file = ContentFile(b("media"))
        fake_file.name = 'media.mp3'
        self.media = MoloMedia.objects.create(
            title="Test Media", file=fake_file, duration=100,
            type=media_type, feature_in_homepage=True)

    def test_audio_media(self):
        self.add_media('audio')
        response = self.client.get('/')
        self.assertContains(
            response,
            '<div><audio controls><source src="{0}"'
            'type="audio/mpeg">Click here to download'
            '<a href="{0}">{1}</a></audio></div>'
            .format(self.media.file.url, self.media.title),
            html=True)

    def test_video_media(self):
        self.add_media('video')
        response = self.client.get('/')
        self.assertContains(
            response,
            '<video width="320" height="240" controls>'
            '<source src=' + self.media.file.url + ' type="video/mp4">'
            'Your browser does not support the video tag.'
            '</video>', html=True)
