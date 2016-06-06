from django import template

register = template.Library()


@register.filter
def format_import_error(error):
    if error.get('type') == 'wrong_main_language_exist_in_wagtail':
        message = (
            "The main language for the account is `%(lang)s`, "
            "while the selected main language for this site "
            "is `%(selected_lang)s`" % {
                'lang': error['details']['lang'],
                'selected_lang': error['details']['selected_lang']})

    elif error.get('type') == 'no_primary_category':
        message = (
            "%(lang)s: No primary category found for page `%(article)s`" % {
                'lang': error['details']['lang'],
                'article': error['details']['article']
            })

    elif error.get('type') == 'no_source_found_for_category':
        message = "%(lang)s: No source found for category `%(category)s`" % {
            'lang': error['details']['lang'],
            'category': error['details']['category']
        }

    elif error.get('type') == 'no_source_found_for_page':
        message = "%(lang)s: No source found for page `%(article)s`" % {
            'lang': error['details']['lang'],
            'article': error['details']['article']
        }

    elif error.get('type') == 'category_source_not_exists':
        message = (
            "%(lang)s: The source for category `%(category)s` "
            "does not exist" % {
                'lang': error['details']['lang'],
                'category': error['details']['category']
            })

    elif error.get('type') == 'page_source_not_exists':
        message = (
            "%(lang)s: The source for page `%(page)s` does not exist" % {
                'lang': error['details']['lang'],
                'page': error['details']['page']
            })

    elif error.get('type') == 'language_not_in_repo':
        message = (
            "Repository %(repo)s does not have content for %(lang)s" % {
                'lang': error['details']['lang'],
                'repo': error['details']['repo']
            })
    else:
        message = error.get('type')

    return message
