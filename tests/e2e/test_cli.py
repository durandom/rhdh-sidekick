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
        assert "sidekick - Modern Python CLI application template" in result.stdout

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

    def test_example_commands_available(self):
        """Test that example commands are available."""
        runner = CliRunner()
        result = runner.invoke(app, ["example", "--help"])

        assert result.exit_code == 0
        assert "Example commands demonstrating CLI patterns" in result.stdout

    def test_example_hello_command(self):
        """Test example hello command works end-to-end."""
        runner = CliRunner()
        result = runner.invoke(app, ["example", "hello", "--name", "Template"])

        assert result.exit_code == 0
        assert "Hello, Template!" in result.stdout

    def test_info_command(self):
        """Test info command."""
        runner = CliRunner()
        result = runner.invoke(app, ["info"])

        assert result.exit_code == 0
        assert "sidekick" in result.stdout
        assert "Modern Python CLI Application Template" in result.stdout
