import os.path
import pkg_resources

import click


@click.group()
def main():
    pass


@click.command()
@click.argument('app_name')
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
def scaffold(**kwargs):
    from cookiecutter.main import cookiecutter
    extra_context = kwargs.copy()
    molo_package = pkg_resources.get_distribution('molo.core')
    extra_context['molo_version'] = molo_package.version
    cookiecutter(
        pkg_resources.resource_filename(
            'molo.core', os.path.join('cookiecutter', 'scaffold')),
        no_input=True,
        extra_context=extra_context)

main.add_command(scaffold)
