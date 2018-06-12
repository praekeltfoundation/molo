from __future__ import print_function

from django.conf import settings
from django.template import Template, TemplateSyntaxError

from glob import glob

from os import walk
from os.path import join

from sys import stderr


def log_error(*args, **kwargs):
    print(*args, file=stderr, **kwargs)


def run():
    exit_code = 0

    html_templates = []
    template_directories = [
        walk_result[0] for walk_result in
        walk(settings.PROJECT_ROOT)]

    for directory in template_directories:
        html_templates += glob(join(directory, '*.html'))

    for filename in html_templates:
        printable_filename = filename.replace(settings.PROJECT_ROOT, '')
        items_loaded = []
        errors = []
        template_file = open(filename).read()

        # Ensure that the template renders
        try:
            Template(template_file)
        except TemplateSyntaxError as e:
            errors.append('TemplateSyntaxError while parsing template')
            errors.append(e)

        lines = template_file.split("\n")

        for line in lines:
            if "{% load " in line:
                items_loaded += [
                    item for item in line.split(' ') if item not in [
                        '{%', 'load', '', '%}']]

        if len(items_loaded) != len(set(items_loaded)):
            errors.append('Duplicate template tags loaded')
            exit_code = 1

        for load in items_loaded:
            try:
                padded_load = ' {0} '.format(load)
                new_template_file = template_file.replace(padded_load, '')
                Template(new_template_file)
                errors.append('Can remove {0} without error'.format(load))
                exit_code = 1
            except TemplateSyntaxError:
                pass

        if errors:
            log_error('')
            log_error(printable_filename)
            for error in errors:
                log_error('  {0}'.format(error))

    exit(exit_code)
