from babel import Locale
from babel.core import UnknownLocaleError

from unicore.content.models import Localisation


def get_locales(ws):
    locales = []
    errors = []

    for l in ws.S(Localisation).all():
        try:
            locales.append({
                'locale': l.locale,
                'name': Locale.parse(l.locale).english_name
            })
        except UnknownLocaleError:
            errors.append({
                'type': 'unknown_locale',
                'details': {'locale': l.locale}
            })

    return locales, errors
