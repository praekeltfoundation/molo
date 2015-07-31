from __future__ import unicode_literals, absolute_import

import os
import logging

from cookiecutter.config import get_user_config
from cookiecutter.generate import generate_context, generate_files
from cookiecutter.main import expand_abbreviations
from cookiecutter.vcs import clone


def cookiecutter(template, checkout=None, no_input=False, extra_context=None):
    """
    Replacement for cookiecutter's own cookiecutter.

    The difference with cookiecutter's cookiecutter function
    is that this one doesn't automatically str() all the values
    passed along to the template.

    :param template: A directory containing a project template directory,
        or a URL to a git repository.
    :param checkout: The branch, tag or commit ID to checkout after clone.
    :param no_input: Prompt the user at command line for manual configuration?
    :param extra_context: A dictionary of context that overrides default
        and user configuration.
    """

    # Get user config from ~/.cookiecutterrc or equivalent
    # If no config file, sensible defaults from config.DEFAULT_CONFIG are used
    config_dict = get_user_config()

    template = expand_abbreviations(template, config_dict)

    # TODO: find a better way to tell if it's a repo URL
    if 'git@' in template or 'https://' in template:
        repo_dir = clone(
            repo_url=template,
            checkout=checkout,
            clone_to_dir=config_dict['cookiecutters_dir'],
            no_input=no_input
        )
    else:
        # If it's a local repo, no need to clone or copy to your
        # cookiecutters_dir
        repo_dir = template

    context_file = os.path.join(repo_dir, 'cookiecutter.json')
    logging.debug('context_file is {0}'.format(context_file))

    context = generate_context(
        context_file=context_file,
        default_context=config_dict['default_context'],
        extra_context=extra_context,
    )

    # Create project from local context and project template.
    generate_files(
        repo_dir=repo_dir,
        context=context
    )
