from django.utils.translation import to_locale
from django.conf import settings


def get_locale_code(language_code=settings.LANGUAGE_CODE):
    locale_code, _, country_code = to_locale(language_code).partition('_')
    return locale_code
