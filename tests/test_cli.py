import pytest
import re

from notifiers import __version__
from click.testing import CliRunner


@pytest.mark.usefixtures('mock_provider')
class TestCLI:
    """CLI tests"""

    @pytest.mark.parametrize('command, exit_code, error', [
        ('', 2, 'invalid choice'),
        ('mock', 1, 'Error')
    ])
    def test_bad_notify(self, command, exit_code, error):
        """Test invalid notification usage"""
        from notifiers_cli.core import notify
        runner = CliRunner()

        result = runner.invoke(notify, [command])
        assert result.exit_code == exit_code
        assert error in result.output

    def test_notify_sanity(self):
        """Test valid notification usage"""
        from notifiers_cli.core import notify
        runner = CliRunner()
        result = runner.invoke(notify, ['mock', 'required=foo', 'message=bar'])
        assert result.exit_code == 0
        assert not result.output

    def test_providers(self, ):
        """Test providers command"""
        from notifiers_cli.core import providers
        runner = CliRunner()
        result = runner.invoke(providers, [])
        assert result.exit_code == 0
        assert 'mock' in result.output

    def test_metadata(self):
        """Test metadata command"""
        from notifiers_cli.core import metadata
        runner = CliRunner()
        result = runner.invoke(metadata, ['mock'])
        assert result.exit_code == 0
        assert "base_url: https://api.mock.com" in result.output
        assert "site_url: https://www.mock.com" in result.output
        assert "provider_name: mock_provide" in result.output

    def test_required(self):
        """Test metadata command"""
        from notifiers_cli.core import required
        runner = CliRunner()
        result = runner.invoke(required, ['mock'])
        assert result.exit_code == 0
        assert 'required' in result.output

    def test_arguments(self):
        """Test metadata command"""
        from notifiers_cli.core import arguments
        runner = CliRunner()
        result = runner.invoke(arguments, ['mock'])
        assert result.exit_code == 0
        assert 'required' in result.output
        assert 'not_required' in result.output
        assert 'message' in result.output

    def test_no_defaults(self):
        """Test defaults command"""
        from notifiers_cli.core import defaults
        runner = CliRunner()
        result = runner.invoke(defaults, ['pushover'])
        assert result.exit_code == 0
        assert 'pushover has no defaults set' in result.output

    def test_defaults(self):
        """Test defaults command"""
        from notifiers_cli.core import defaults
        runner = CliRunner()
        result = runner.invoke(defaults, ['mock'])
        assert result.exit_code == 0
        assert 'option_with_default: foo' in result.output

    def test_piping_input(self):
        """Test piping in message"""
        from notifiers_cli.core import notify
        runner = CliRunner()
        result = runner.invoke(notify, ['mock', 'required=foo'], input='bar')
        assert result.exit_code == 0
        assert not result.output

    def test_default_provider(self, monkeypatch):
        """Test default provider environ"""
        monkeypatch.setenv('NOTIFIERS_DEFAULT_PROVIDER', 'mock')
        monkeypatch.setenv('NOTIFIERS_MOCK_PROVIDER_REQUIRED', 'foo')
        from notifiers_cli.core import notify
        runner = CliRunner()
        result = runner.invoke(notify, [], input='foo')
        assert result.exit_code == 0
        assert not result.output

    def test_version_command(self):
        from notifiers_cli.core import notifiers
        runner = CliRunner()
        result = runner.invoke(notifiers, ['--version'])
        assert result.exit_code == 0
        version_re = re.search('(\d+\.\d+\.\d+)', result.output)
        assert version_re
        assert version_re.group(1) == __version__
