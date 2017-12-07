import json
from six import b
from django.contrib.sites.models import Site
from django.test import TestCase, Client

from molo.core.tests.base import MoloTestCaseMixin
from molo.core.models import SiteLanguageRelation, Main, Languages, MoloMedia
from django.core.files.base import ContentFile


class GemContextProcessorTest(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.client = Client()
        main = Main.objects.all().first()
        self.english = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(main.get_site()),
            locale='en',
            is_active=True)
        self.yourmind = self.mk_section(
            self.section_index, title='Your mind')
        self.article = self.mk_article(self.yourmind)

    def test_detect_freebasics(self):
        fake_file = ContentFile(b("media"))
        fake_file.name = 'media.mp3'
        self.media = MoloMedia.objects.create(
            title="Test Media", file=fake_file, duration=100, type="audio")
        self.article.body = json.dumps([{
            'type': 'media',
            'value': self.media.id,
        }])
        self.article.save_revision().publish()

        response = self.client.get('/sections-main-1/your-mind/test-page-0/')
        self.assertContains(response, 'Download Audio')

        client = Client(HTTP_VIA='Internet.org')
        response = client.get('/sections-main-1/your-mind/test-page-0/')
        self.assertNotContains(response, 'Download Audio')

        client = Client(HTTP_X_IORG_FBS='true',)
        response = client.get('/sections-main-1/your-mind/test-page-0/')

        self.assertNotContains(response, 'Download Audio')

        client = Client(
            HTTP_USER_AGENT='Mozilla/5.0 (Linux; Android 5.1;'
            ' VFD 100 Build/LMY47I; wv) AppleWebKit/537.36'
            ' (KHTML, like Gecko) Version/4.0 Chrome/50.0.2661.86'
            ' Mobile Safari/537[FBAN/InternetOrgApp; FBAV/7.0;]')
        response = client.get('/sections-main-1/your-mind/test-page-0/')

        self.assertNotContains(response, 'Download Audio')

        client = Client(
            HTTP_VIA='Internet.org',
            HTTP_X_IORG_FBS='true',
            HTTP_USER_AGENT='Mozilla/5.0 (Linux; Android 5.1;'
            ' VFD 100 Build/LMY47I; wv) AppleWebKit/537.36'
            ' (KHTML, like Gecko) Version/4.0 Chrome/50.0.2661.86'
            ' Mobile Safari/537[FBAN/InternetOrgApp; FBAV/7.0;]')
        response = client.get('/sections-main-1/your-mind/test-page-0/')

        self.assertNotContains(response, 'Download Audio')
