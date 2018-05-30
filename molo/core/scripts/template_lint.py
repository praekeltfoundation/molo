from __future__ import print_function

from django.conf import settings

from glob import glob

from os import walk
from os.path import join

from sys import stderr
from molo.core.scripts.utils import lint_template_file


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

    errors = [lint_template_file(filename) for filename in html_templates]
    if any(errors):
        log_error(*[error for error in errors if error])
        exit_code = 1

    exit(exit_code)
