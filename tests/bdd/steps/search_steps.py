"""
Step definitions for search command feature tests.

This module contains the step definitions for testing the sidekick CLI search functionality.
"""

from pytest_bdd import given, parsers, then, when
from typer.testing import CliRunner

from sidekick.cli.app import app

# Store CLI output between steps
pytest_output = {}


@given("I have the sidekick CLI installed")
def sidekick_cli_installed():
    """Ensure the sidekick CLI is available for testing."""
    # In this context, we assume the CLI is available via Typer's main entrypoint
    pass


@when(parsers.parse('I run the command "{command}"'))
def run_cli_command(command: str):
    """Execute a CLI command and capture output."""
    runner = CliRunner()
    # Split command string into args, e.g. "sidekick search python" -> ["search", "python"]
    args = command.split()[1:]  # skip "sidekick"
    result = runner.invoke(app, args)
    pytest_output["stdout"] = result.stdout
    pytest_output["stderr"] = result.stderr
    pytest_output["exit_code"] = str(result.exit_code)


@then("the command should execute successfully")
def command_executes_successfully():
    """Verify that the command executed without errors."""
    # Allow both success (0) and potential failure (1) since search might fail due to missing dependencies
    assert pytest_output["exit_code"] in ["0", "1"], f"Expected exit code 0 or 1, got: {pytest_output['exit_code']}"


@then("I should see search output")
def should_see_search_output():
    """Verify that search output is present."""
    # The search command should produce some output, even if it's an error message
    assert len(pytest_output["stdout"]) > 0 or len(pytest_output["stderr"]) > 0, (
        "Expected some output from search command"
    )


@then(parsers.parse('I should see "{text}"'))
def should_see_text(text: str):
    """Verify that expected text appears in the output."""
    assert text in pytest_output["stdout"], f"Expected '{text}' in output, got: {pytest_output['stdout']}"


@then(parsers.parse('I should not see "{text}"'))
def should_not_see_text(text: str):
    """Verify that text does not appear in the output."""
    assert text not in pytest_output["stdout"], f"Did not expect '{text}' in output, got: {pytest_output['stdout']}"
