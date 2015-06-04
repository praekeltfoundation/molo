from django.utils.translation import get_language_from_request
from molo.core.utils import get_locale_code


def locale(request):
    language = get_language_from_request(request)
    return {'locale_code': get_locale_code(language)}
