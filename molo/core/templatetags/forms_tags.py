from copy import copy
from django import template
from molo.core.models import FormPage, FormIndexPage
from molo.core.templatetags.core_tags import get_pages


register = template.Library()


@register.inclusion_tag('forms/forms_list.html', takes_context=True)
def forms_list(context):
    context = copy(context)
    locale_code = context.get('locale_code')
    main = context['request'].site.root_page
    page = FormIndexPage.objects.child_of(main).live().first()
    if page:
        forms = (
            FormPage.objects.child_of(page).filter(
                language__is_main_language=True).specific())
    else:
        forms = FormPage.objects.none()
    context.update({
        'forms': get_pages(context, forms, locale_code)
    })
    return context
