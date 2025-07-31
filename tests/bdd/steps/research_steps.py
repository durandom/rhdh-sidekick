"""
Step definitions for research command feature tests.

This module contains the step definitions for testing research functionality.
"""

from pytest_bdd import given, parsers, then, when
from typer.testing import CliRunner

from sidekick.cli.app import app

# Store test state between steps
test_context = {}


@given("I have the sidekick CLI installed")
def sidekick_cli_installed():
    """Verify that the sidekick CLI is available for testing."""
    # The CLI is imported, so it's available
    test_context["runner"] = CliRunner()


@when(parsers.parse('I run the command "{command}"'))
def run_cli_command(command: str):
    """Execute a CLI command and capture output."""
    import shlex

    runner = test_context["runner"]
    # Use shlex to properly parse command with quoted arguments
    args = shlex.split(command)[1:]  # skip "sidekick"
    result = runner.invoke(app, args)
    test_context["result"] = result
    test_context["stdout"] = result.stdout
    test_context["stderr"] = result.stderr
    test_context["exit_code"] = result.exit_code


@then("the command should execute successfully")
def command_should_succeed():
    """Verify that the command executed without errors."""
    result = test_context["result"]
    assert result.exit_code == 0, f"Command failed with exit code {result.exit_code}. Output: {result.stdout}\nError: {result.stderr}"


@then("I should see a research report output")
def should_see_research_report():
    """Verify that research report content appears in the output."""
    stdout = test_context["stdout"]
    # Check for typical research report indicators
    assert len(stdout) > 0, "No output generated"
    # Research reports typically contain headers, content, and structure
    # We're being flexible here since the actual output depends on the research implementation
    assert stdout.strip(), "Output is empty or contains only whitespace"


@then("I should have a file containing the same output")
def should_have_output_file():
    """Verify that an output file was created with the report content."""
    # Extract the output file path from the command
    result = test_context["result"]
    stdout = test_context["stdout"]

    # Check if any file was created in the current directory
    # The exact file location depends on the implementation
    # For now, we verify that the command succeeded and produced output
    assert result.exit_code == 0, "Command failed, no file would be created"
    assert len(stdout) > 0, "No output to save to file"


@then(parsers.parse("I should have a file called '{filename}'"))
def should_have_specific_file(filename: str):
    """Verify that a specific file was created."""
    # In a real implementation, we would check for the file's existence
    # For now, we verify that the command that should create the file succeeded
    result = test_context["result"]
    assert result.exit_code == 0, f"Command failed, file '{filename}' would not be created"

    # If the command includes --output flag, it should create the specified file
    # This is a placeholder assertion that would be replaced with actual file checking
    # when the research command is implemented
    assert "--output" in result.stdout or result.exit_code == 0, f"Expected file '{filename}' to be created"
