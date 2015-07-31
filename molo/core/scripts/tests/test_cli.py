from unittest import TestCase
import pkg_resources

from mock import patch

from click.testing import CliRunner


class TestCli(TestCase):

    @patch('molo.core.cookiecutter.cookiecutter')
    def test_scaffold(self, mock_cookiecutter):
        from molo.core.scripts import cli
        package = pkg_resources.get_distribution('molo.core')

        runner = CliRunner()
        runner.invoke(cli.scaffold, ['foo'])
        [call] = mock_cookiecutter.call_args_list
        args, kwargs = call
        self.assertTrue(kwargs['extra_context'].pop('secret_key'))
        self.assertEqual(kwargs, {
            'no_input': True,
            'extra_context': {
                'app_name': 'foo',
                'directory': 'foo',
                'author': 'Praekelt Foundation',
                'author_email': 'dev@praekelt.com',
                'url': None,
                'license': 'BSD',
                'molo_version': package.version,
                'require': (),
                'include': (),
            }
        })

    @patch('molo.core.cookiecutter.cookiecutter')
    def test_scaffold_with_custom_dir(self, mock_cookiecutter):
        from molo.core.scripts import cli
        package = pkg_resources.get_distribution('molo.core')

        runner = CliRunner()
        runner.invoke(cli.scaffold, ['foo', 'bar'])
        [call] = mock_cookiecutter.call_args_list
        args, kwargs = call
        self.assertTrue(kwargs['extra_context'].pop('secret_key'))
        self.assertEqual(kwargs, {
            'no_input': True,
            'extra_context': {
                'app_name': 'foo',
                'directory': 'bar',
                'author': 'Praekelt Foundation',
                'author_email': 'dev@praekelt.com',
                'url': None,
                'license': 'BSD',
                'molo_version': package.version,
                'require': (),
                'include': (),
            }
        })

    @patch('molo.core.cookiecutter.cookiecutter')
    def test_scaffold_with_requirements(self, mock_cookiecutter):
        from molo.core.scripts import cli
        package = pkg_resources.get_distribution('molo.core')

        runner = CliRunner()
        runner.invoke(cli.scaffold, ['foo', '--require', 'bar'])
        [call] = mock_cookiecutter.call_args_list
        args, kwargs = call
        self.assertTrue(kwargs['extra_context'].pop('secret_key'))
        self.assertEqual(kwargs, {
            'no_input': True,
            'extra_context': {
                'app_name': 'foo',
                'directory': 'foo',
                'author': 'Praekelt Foundation',
                'author_email': 'dev@praekelt.com',
                'url': None,
                'license': 'BSD',
                'molo_version': package.version,
                'require': ('bar',),
                'include': (),
            }
        })

    @patch('molo.core.cookiecutter.cookiecutter')
    def test_scaffold_with_includes(self, mock_cookiecutter):
        from molo.core.scripts import cli
        package = pkg_resources.get_distribution('molo.core')

        runner = CliRunner()
        runner.invoke(cli.scaffold, ['foo', '--include', 'bar', 'baz'])
        [call] = mock_cookiecutter.call_args_list
        args, kwargs = call
        self.assertTrue(kwargs['extra_context'].pop('secret_key'))
        self.assertEqual(kwargs, {
            'no_input': True,
            'extra_context': {
                'app_name': 'foo',
                'directory': 'foo',
                'author': 'Praekelt Foundation',
                'author_email': 'dev@praekelt.com',
                'url': None,
                'license': 'BSD',
                'molo_version': package.version,
                'require': (),
                'include': (('bar', 'baz'),),
            }
        })
