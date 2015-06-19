from django.utils.translation import to_locale
from django.conf import settings


def get_locale_code(language_code=None):
    # Simple implementation that uses the ISO 639-1 (2 char codes)
    # discarding the country code
    language_code = language_code or settings.LANGUAGE_CODE
    locale_code, _, country_code = to_locale(language_code).partition('_')
    return locale_code
