from django.utils.translation import get_language_from_request
from django.core.cache import cache
from molo.core.utils import get_locale_code
from molo.core.models import Languages


def locale(request):
    locale_code = get_locale_code(get_language_from_request(request))
    cache_key_langs = "ctx_proc_languages_for_{}".format(request.site)

    languages = cache.get(cache_key_langs)
    if not languages:
        languages = Languages.for_site(request.site).languages.filter(
            is_active=True)
        cache.set(cache_key_langs, languages, 300)

    selected_language = languages.filter(locale=locale_code).first()

    return {
        'locale_code': locale_code,
        'languages': languages,
        'selected_language': selected_language}
