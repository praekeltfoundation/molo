from django.conf import settings
from django.template import Template, TemplateSyntaxError


def lint_template(template_string):
    '''
    Takes Django template file path
    Returns array of error strings
    '''
    items_loaded = []
    errors = []

    # Ensure that the template renders
    try:
        Template(template_string)
    except TemplateSyntaxError as e:
        errors.append(
            'TemplateSyntaxError while parsing template\n\t{}'.format(str(e)))

    lines = template_string.split("\n")

    for line in lines:
        if "{% load " in line:
            items_loaded += [
                item for item in line.split(' ') if item not in [
                    '{%', 'load', '', '%}']]

    if len(items_loaded) != len(set(items_loaded)):
        errors.append('Duplicate template tags loaded')

    for load in items_loaded:
        try:
            padded_load = ' {0} '.format(load)
            new_template_file = template_string.replace(padded_load, '')
            Template(new_template_file)
            errors.append('Can remove {0} without error'.format(load))
        except TemplateSyntaxError:
            pass

    return errors


def lint_template_file(filename):
    printable_filename = filename.replace(settings.PROJECT_ROOT, '')
    template_string = open(filename).read()
    errors = lint_template(template_string)

    if errors:
        error_string = "ERROR: {}\n".format(printable_filename)
        for error in errors:
            error_string += '  {}\n'.format(error)

        return error_string
    return None
