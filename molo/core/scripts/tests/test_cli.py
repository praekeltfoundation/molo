from unittest import TestCase
import pkg_resources

from mock import patch

from click import UsageError
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

    @patch('molo.core.scripts.cli.get_package')
    @patch('molo.core.scripts.cli.get_template_dirs')
    @patch('shutil.copytree')
    def test_unpack(self, mock_copytree, mock_get_template_dirs,
                    mock_get_package):
        package = pkg_resources.get_distribution('molo.core')
        mock_get_package.return_value = package
        mock_get_template_dirs.return_value = ['foo']
        mock_copytree.return_value = True

        from molo.core.scripts import cli
        runner = CliRunner()
        runner.invoke(cli.unpack_templates, ['app1', 'app2'])

        mock_copytree.assert_called_with(
            pkg_resources.resource_filename('molo.core', 'templates/foo'),
            pkg_resources.resource_filename('molo.core', 'templates/foo'))

    def test_get_package(self):
        from molo.core.scripts.cli import get_package
        self.assertRaisesRegexp(
            UsageError, 'molo.foo is not installed.', get_package, 'molo.foo')
