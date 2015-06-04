from django.test import TestCase
from molo.core import utils


class TestUtils(TestCase):

    def test_get_locale_code(self):
        assert utils.get_locale_code() == 'en'
        assert utils.get_locale_code('en-GB') == 'en'
        assert utils.get_locale_code('en_GB') == 'en'
        assert utils.get_locale_code('fr_FR') == 'fr'
        assert utils.get_locale_code('zu-ZA') == 'zu'
        assert utils.get_locale_code('en') == 'en'
