from django.utils.translation import get_language_from_request
from molo.core.utils import get_locale_code
from molo.core.models import LanguagePage


def locale(request):
    language = get_language_from_request(request)
    languages = LanguagePage.objects.live()
    return {
        'locale_code': get_locale_code(language),
        'languages': languages}
