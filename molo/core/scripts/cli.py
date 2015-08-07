import os.path
import shutil
import pkg_resources

import click


def get_package(package_name):
    try:
        pkg = pkg_resources.get_distribution(package_name)
    except pkg_resources.DistributionNotFound:
        raise click.UsageError('%s is not installed.' % (package_name,))

    if not pkg_resources.resource_isdir(pkg.key, 'templates'):
        raise click.UsageError(
            '%s does not have a templates directory.' % (pkg.key,))
    return pkg


def get_template_dirs(package_name):
    return pkg_resources.resource_listdir(package_name, 'templates')


@click.command()
@click.argument('source_package')
@click.argument('target_package')
def unpack_templates(**kwargs):
    source_pkg = get_package(kwargs['source_package'])
    target_pkg = get_package(kwargs['target_package'])

    for directory in get_template_dirs(source_pkg.key):
        try:
            shutil.copytree(
                pkg_resources.resource_filename(
                    source_pkg.key, os.path.join('templates', directory)),
                pkg_resources.resource_filename(
                    target_pkg.key, os.path.join('templates', directory))
            )
        except (OSError,), e:
            raise click.ClickException(str(e))


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


@click.group()
def main():
    pass

main.add_command(scaffold, name='scaffold')
main.add_command(unpack_templates, name='unpack-templates')
