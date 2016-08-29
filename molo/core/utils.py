import re
from django.conf import settings
from wagtail.wagtailcore.utils import cautious_slugify


def get_locale_code(language_code=None):
    return (language_code or settings.LANGUAGE_CODE).replace('_', '-')

RE_NUMERICAL_SUFFIX = re.compile(r'^[\w-]*-(\d+)+$')


def generate_slug(text, tail_number=0):
    from wagtail.wagtailcore.models import Page
    """
    Returns a new unique slug. Object must provide a SlugField called slug.
    URL friendly slugs are generated using django.template.defaultfilters'
    slugify. Numbers are added to the end of slugs for uniqueness.

    based on implementation in jmbo.utils
    https://github.com/praekelt/jmbo/blob/develop/jmbo/utils/__init__.py
    """

    # Empty slugs are ugly (eg. '-1' may be generated) so force non-empty
    if not text:
        text = 'no-title'

    # use django slugify filter to slugify
    slug = cautious_slugify(text)[:255]

    values_list = Page.objects.filter(
        slug__startswith=slug
    ).values_list('id', 'slug')

    # Find highest suffix
    max = -1
    for tu in values_list:
        if tu[1] == slug:
            if max == -1:
                # Set max to indicate a collision
                max = 0

        # Update max if suffix is greater
        match = RE_NUMERICAL_SUFFIX.match(tu[1])
        if match is not None:
            i = int(match.group(1))
            if i > max:
                max = i

    if max >= 0:
        # There were collisions
        return "%s-%s" % (slug, max + 1)
    else:
        # No collisions
        return slug
