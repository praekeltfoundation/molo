import click
import pkg_resources

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
def scaffold(app_name):
    cookiecutter(
        pkg_resources.resource_filename(
            'molo', 'core/cookiecutter/scaffold'),
        no_input=app_name,
        extra_context={})

main.add_command(scaffold)
