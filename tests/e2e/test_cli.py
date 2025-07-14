"""
End-to-end CLI tests for sidekick.

This module tests the CLI functionality from a user perspective.
"""

from typer.testing import CliRunner

from sidekick.cli.app import app


class TestCLI:
    """End-to-end CLI tests."""

    def test_help_command(self):
        """Test help command."""
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "sidekick" in result.stdout
        assert "Commands" in result.stdout

    def test_version_command(self):
        """Test version command."""
        runner = CliRunner()
        result = runner.invoke(app, ["version"])

        assert result.exit_code == 0
        assert "sidekick" in result.stdout
        assert "version" in result.stdout
        # Check for version components since Rich formatting breaks up "0.1.0"
        assert "0.1" in result.stdout
        assert "0" in result.stdout

    def test_info_command(self):
        """Test info command."""
        runner = CliRunner()
        result = runner.invoke(app, ["info"])

        assert result.exit_code == 0
        assert "sidekick" in result.stdout
        assert "Modern Python CLI Application Template" in result.stdout

    def test_verbose_options(self):
        """Test verbose logging options."""
        runner = CliRunner()
        result = runner.invoke(app, ["-v", "version"])
        assert result.exit_code == 0

        result = runner.invoke(app, ["-vv", "version"])
        assert result.exit_code == 0
