from unittest import TestCase
import pkg_resources

from mock import patch

from click.testing import CliRunner


class TestCli(TestCase):

    @patch('cookiecutter.main.cookiecutter')
    def test_scaffold(self, mock_cookiecutter):
        from molo.core.scripts import cli
        package = pkg_resources.get_distribution('molo.core')

        runner = CliRunner()
        runner.invoke(cli.scaffold, ['foo'])
        # mock_cookiecutter.assert_called_with({})
        [call] = mock_cookiecutter.call_args_list
        args, kwargs = call
        self.assertEqual(kwargs, {
            'no_input': True,
            'extra_context': {
                'app_name': 'foo',
                'author': 'Praekelt Foundation',
                'author_email': 'dev@praekelt.com',
                'url': None,
                'license': 'BSD',
                'molo_version': package.version,
            }
        })
