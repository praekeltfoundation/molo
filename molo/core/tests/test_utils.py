from django.test import TestCase
from molo.core import utils


class TestUtils(TestCase):

    def test_get_locale_code(self):
        self.assertEquals(utils.get_locale_code(), 'en')
        self.assertEquals(utils.get_locale_code('en-GB'), 'en')
        self.assertEquals(utils.get_locale_code('en_GB'), 'en')
        self.assertEquals(utils.get_locale_code('fr_FR'), 'fr')
        self.assertEquals(utils.get_locale_code('zu-ZA'), 'zu')
        self.assertEquals(utils.get_locale_code('en'), 'en')
