"""
Unit tests for example commands.

This module demonstrates how to test CLI commands and command groups.
"""

from typer.testing import CliRunner

from sidekick.commands import ExampleCommands


class TestExampleCommands:
    """Test cases for ExampleCommands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.commands = ExampleCommands()
        self.app = self.commands.create_app()

    def test_hello_default(self):
        """Test hello command with default parameters."""
        result = self.runner.invoke(self.app, ["hello"])
        assert result.exit_code == 0
        assert "Hello, World!" in result.stdout

    def test_hello_with_name(self):
        """Test hello command with custom name."""
        result = self.runner.invoke(self.app, ["hello", "--name", "Alice"])
        assert result.exit_code == 0
        assert "Hello, Alice!" in result.stdout

    def test_hello_with_count(self):
        """Test hello command with multiple greetings."""
        result = self.runner.invoke(self.app, ["hello", "--count", "3"])
        assert result.exit_code == 0
        assert result.stdout.count("Hello, World!") == 3
        assert "(1/3)" in result.stdout
        assert "(2/3)" in result.stdout
        assert "(3/3)" in result.stdout

    def test_config_command(self):
        """Test config command displays configuration."""
        result = self.runner.invoke(self.app, ["config"])
        assert result.exit_code == 0
        assert "Current Configuration" in result.stdout
        assert "sidekick" in result.stdout

    def test_demo_error_command(self):
        """Test demo-error command handles errors properly."""
        result = self.runner.invoke(self.app, ["demo-error"])
        assert result.exit_code == 1
        assert "Cannot divide by zero" in result.stdout

    def test_help_messages(self):
        """Test that commands provide helpful help text."""
        result = self.runner.invoke(self.app, ["--help"])
        assert result.exit_code == 0
        assert "Example commands demonstrating CLI patterns" in result.stdout

        result = self.runner.invoke(self.app, ["hello", "--help"])
        assert result.exit_code == 0
        assert "Say hello with customizable greeting" in result.stdout
