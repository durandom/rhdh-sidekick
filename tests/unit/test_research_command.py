"""Unit tests for research command."""

from unittest.mock import patch

from typer.testing import CliRunner

from sidekick.cli.app import app


class TestResearchCommand:
    """Test cases for the research command."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_research_command_requires_query(self):
        """Test that research command requires a query argument."""
        result = self.runner.invoke(app, ["research"])
        assert result.exit_code == 2  # Missing required argument
        assert "Missing argument 'QUERY'" in result.output

    def test_research_command_help(self):
        """Test that research command shows help correctly."""
        result = self.runner.invoke(app, ["research", "--help"])
        assert result.exit_code == 0
        assert "AI-powered research using multi-agent workflow" in result.stdout
        assert "Research query or topic" in result.stdout

    def test_research_command_requires_api_key(self):
        """Test that research command requires an API key."""
        result = self.runner.invoke(app, ["research", "test query"])
        assert result.exit_code == 1
        assert "Anthropic API key is required" in result.stdout

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
    @patch("sidekick.cli.research.asyncio.run")
    def test_research_command_with_api_key(self, mock_asyncio_run):
        """Test that research command runs with API key."""
        mock_asyncio_run.return_value = None

        result = self.runner.invoke(app, ["research", "test query"])

        # The command should attempt to run the workflow
        mock_asyncio_run.assert_called_once()
        # Should show success message
        assert "Research completed successfully" in result.stdout or result.exit_code == 0

    def test_research_command_validates_thresholds(self):
        """Test that research command validates threshold parameters."""
        # Test invalid save threshold
        result = self.runner.invoke(app, ["research", "--save-threshold", "15", "test query"])
        assert result.exit_code == 1
        assert "save-threshold must be between 0 and 10" in result.stdout

        # Test invalid review threshold
        result = self.runner.invoke(app, ["research", "--review-threshold", "-5", "test query"])
        assert result.exit_code == 1
        assert "review-threshold must be between 0 and 10" in result.stdout

        # Test review threshold higher than save threshold
        result = self.runner.invoke(app, ["research", "--save-threshold", "5", "--review-threshold", "8", "test query"])
        assert result.exit_code == 1
        assert "review-threshold cannot be higher than save-threshold" in result.stdout

    def test_research_command_validates_format(self):
        """Test that research command validates format parameter."""
        result = self.runner.invoke(app, ["research", "--format", "invalid", "test query"])
        assert result.exit_code == 1
        assert "format must be one of: markdown, json, html" in result.stdout
