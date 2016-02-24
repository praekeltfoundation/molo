from django.utils.translation import get_language_from_request
from molo.core.utils import get_locale_code
from molo.core.models import SiteLanguage


def locale(request):
    locale_code = get_locale_code(get_language_from_request(request))
    languages = SiteLanguage.objects.filter(is_active=True)
    return {
        'locale_code': locale_code,
        'languages': languages,
        'selected_language': SiteLanguage.objects.filter(
            locale=locale_code).first()}
