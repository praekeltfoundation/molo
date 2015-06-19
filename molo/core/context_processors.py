from django.utils.translation import get_language_from_request
from molo.core.utils import get_locale_code
from molo.core.models import LanguagePage


def locale(request):
    locale_code = get_locale_code(get_language_from_request(request))
    languages = LanguagePage.objects.live()
    language_page = LanguagePage.objects.live().filter(
        code=locale_code).first()
    return {
        'locale_code': locale_code,
        'languages': languages,
        'language_page': language_page}
