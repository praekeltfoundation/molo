import os.path
import pkg_resources

import click

from cookiecutter.main import cookiecutter


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
    cookiecutter(
        pkg_resources.resource_filename(
            'molo', os.path.join('core', 'cookiecutter', 'scaffold')),
        no_input=True,
        extra_context=kwargs)

main.add_command(scaffold)
