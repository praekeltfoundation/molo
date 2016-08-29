from django.test import TestCase
from molo.core import utils
from molo.core.tests.base import MoloTestCaseMixin
from molo.core.models import SiteLanguage
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
        self.english = SiteLanguage.objects.create(
            locale='en',
        )
        self.mk_main()

        self.mk_section(self.main, title='Your mind')
        self.assertEquals(generate_slug('Your mind'), 'your-mind-1')

        self.mk_section(self.main, title='Your mind')
        self.assertEquals(generate_slug('Your mind'), 'your-mind-2')

        self.assertEquals(generate_slug(None), 'no-title')
