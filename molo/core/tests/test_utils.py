from django.test import TestCase
from molo.core import utils
from molo.core.tests.base import MoloTestCaseMixin
from molo.core.models import SiteLanguageRelation, Languages, Main
from molo.core.utils import generate_slug


class TestUtils(TestCase, MoloTestCaseMixin):

    def test_get_locale_code(self):
        self.assertEquals(utils.get_locale_code(), 'en')
        self.assertEquals(utils.get_locale_code('en-GB'), 'en-GB')
        self.assertEquals(utils.get_locale_code('en_GB'), 'en-GB')
        self.assertEquals(utils.get_locale_code('fr_FR'), 'fr-FR')
        self.assertEquals(utils.get_locale_code('zu-ZA'), 'zu-ZA')
        self.assertEquals(utils.get_locale_code('en'), 'en')

    def test_slugify(self):
        self.mk_main()
        main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)

        self.mk_section(self.main, title='Your mind')
        self.assertEquals(generate_slug('Your mind'), 'your-mind-1')

        self.mk_section(self.main, title='Your mind')
        self.assertEquals(generate_slug('Your mind'), 'your-mind-2')

        self.assertEquals(generate_slug(None), 'no-title')
