import os.path
import pkg_resources

import click


@click.group()
def main():
    pass


@click.command()
@click.argument('app_name')
@click.argument('directory', default='')
@click.option('--author',
              help='The author\'s name',
              default='Praekelt Foundation')
@click.option('--author-email',
              help='The author\'s email address',
              default='dev@praekelt.com')
@click.option('--url',
              help='The URL for this application.')
@click.option('--license',
              help='The License to release the package under.',
              default='BSD')
@click.option('--require',
              help=('Define an extra package that needs to be included '
                    'in the requirements.txt'),
              multiple=True)
@click.option('--include',
              help=('Which libraries to include and add to INSTALLED_APPS. '
                    'Expected format (<python-module-name> <regex-for-urls>)'),
              nargs=2, multiple=True)
def scaffold(**kwargs):
    from molo.core.cookiecutter import cookiecutter
    from django.utils.crypto import get_random_string

    extra_context = kwargs.copy()
    # NOTE: we're going to create a directory for whatever value app_name
    #       is unless directory is specified.
    if not extra_context['directory']:
        extra_context['directory'] = extra_context['app_name']
    molo_package = pkg_resources.get_distribution('molo.core')
    extra_context['molo_version'] = molo_package.version

    # Create a random SECRET_KEY to put it in the main settings.
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    extra_context['secret_key'] = get_random_string(50, chars)

    cookiecutter(
        pkg_resources.resource_filename(
            'molo.core', os.path.join('cookiecutter', 'scaffold')),
        no_input=True,
        extra_context=extra_context)

main.add_command(scaffold)
