"""
Unit tests for CLI commands.

This module tests the actual CLI commands defined in the application.
"""

from typer.testing import CliRunner

from sidekick.cli.app import app


class TestCLICommands:
    """Test cases for CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_version_command(self):
        """Test version command displays version information."""
        result = self.runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "sidekick" in result.stdout
        assert "0.1.0" in result.stdout

    def test_info_command(self):
        """Test info command displays application information."""
        result = self.runner.invoke(app, ["info"])
        assert result.exit_code == 0
        assert "sidekick" in result.stdout
        assert "Typer" in result.stdout
        assert "Rich" in result.stdout
        assert "Pydantic" in result.stdout

    def test_help_messages(self):
        """Test that commands provide helpful help text."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "sidekick" in result.stdout

        result = self.runner.invoke(app, ["version", "--help"])
        assert result.exit_code == 0
        assert "Show version information" in result.stdout

        result = self.runner.invoke(app, ["info", "--help"])
        assert result.exit_code == 0
        assert "Show application information" in result.stdout

        result = self.runner.invoke(app, ["search", "--help"])
        assert result.exit_code == 0
        assert "Search query string" in result.stdout

    def test_verbose_options(self):
        """Test verbose logging options."""
        result = self.runner.invoke(app, ["-v", "version"])
        assert result.exit_code == 0

        result = self.runner.invoke(app, ["-vv", "version"])
        assert result.exit_code == 0

    def test_log_level_option(self):
        """Test log level option."""
        result = self.runner.invoke(app, ["--log-level", "DEBUG", "version"])
        assert result.exit_code == 0
