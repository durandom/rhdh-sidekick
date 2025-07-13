"""
Step definitions for CLI help output feature tests.

This module contains the step definitions for testing the sidekick CLI help functionality.
"""

from pytest_bdd import given, parsers, then, when
from typer.testing import CliRunner

from sidekick.cli.app import app

# Store CLI output between steps
pytest_output = {}


@given("I have the sidekick CLI installed")
def sidekick_cli_installed():
    # In this context, we assume the CLI is available via Typer's main entrypoint
    pass


@when(parsers.parse('I run the command "{command}"'))
def run_cli_command(command: str):
    runner = CliRunner()
    # Split command string into args, e.g. "sidekick --help" -> ["--help"]
    args = command.split()[1:]  # skip "sidekick"
    result = runner.invoke(app, args)
    pytest_output["stdout"] = result.stdout
    pytest_output["exit_code"] = str(result.exit_code)


@then(parsers.parse('I should see "{text}"'))
def should_see_text(text: str):
    assert text in pytest_output["stdout"], f"Expected '{text}' in output, got: {pytest_output['stdout']}"
