# BDD Testing Guide

This guide explains how to write Behavior Driven Development (BDD) tests for the sidekick CLI application using pytest-bdd.

## Overview

BDD tests help us verify that our application behaves correctly from a user's perspective. They use natural language scenarios that describe expected behavior, making them readable by both technical and non-technical stakeholders.

## Project Structure

```
tests/bdd/
├── __init__.py
├── conftest.py                    # BDD-specific pytest fixtures
├── features/                      # Gherkin feature files
│   ├── __init__.py
│   └── cli_help.feature          # Example feature file
├── steps/                         # Step definitions (Python code)
│   ├── __init__.py
│   └── cli_help_steps.py         # Step implementations
└── test_cli_help.py              # Test file that connects features to steps
```

## Writing a New BDD Feature

### Step 1: Create the Feature File

Create a new `.feature` file in `tests/bdd/features/` using Gherkin syntax:

```gherkin
Feature: User Authentication
  As a user of the sidekick CLI
  I want to authenticate with my credentials
  So that I can access protected features

  Scenario: Successful login with valid credentials
    Given I have valid user credentials
    When I run the command "sidekick auth login --username test@example.com --password secret123"
    Then I should see "Login successful"
    And I should see "Welcome, test@example.com"

  Scenario: Failed login with invalid credentials
    Given I have invalid user credentials
    When I run the command "sidekick auth login --username wrong@example.com --password wrongpass"
    Then I should see "Login failed"
    And I should see "Invalid credentials"
```

### Step 2: Create Step Definitions

Create a new Python file in `tests/bdd/steps/` to implement the step definitions:

```python
# tests/bdd/steps/auth_steps.py
"""
Step definitions for authentication feature tests.

This module contains the step definitions for testing authentication functionality.
"""

from typer.testing import CliRunner
from pytest_bdd import given, when, then, parsers

from sidekick.cli.app import app

# Store test state between steps
test_context = {}

@given("I have valid user credentials")
def valid_credentials():
    """Set up valid test credentials."""
    test_context["username"] = "test@example.com"
    test_context["password"] = "secret123"
    # Mock or setup valid credentials in your system

@given("I have invalid user credentials")
def invalid_credentials():
    """Set up invalid test credentials."""
    test_context["username"] = "wrong@example.com"
    test_context["password"] = "wrongpass"

@when(parsers.parse('I run the command "{command}"'))
def run_cli_command(command: str):
    """Execute a CLI command and capture output."""
    runner = CliRunner()
    # Split command string into args
    args = command.split()[1:]  # skip "sidekick"
    result = runner.invoke(app, args)
    test_context["stdout"] = result.stdout
    test_context["stderr"] = result.stderr
    test_context["exit_code"] = result.exit_code

@then(parsers.parse('I should see "{text}"'))
def should_see_text(text: str):
    """Verify that expected text appears in the output."""
    assert text in test_context["stdout"], f"Expected '{text}' in output, got: {test_context['stdout']}"

@then(parsers.parse('I should not see "{text}"'))
def should_not_see_text(text: str):
    """Verify that text does not appear in the output."""
    assert text not in test_context["stdout"], f"Did not expect '{text}' in output, got: {test_context['stdout']}"
```

### Step 3: Create the Test File

Create a test file that connects the feature to the step definitions:

```python
# tests/bdd/test_auth.py
"""
BDD tests for authentication functionality.

This module contains the BDD test scenarios for testing authentication features.
"""

# Import the step definitions first to register them
from .steps.auth_steps import *  # noqa: F401,F403

from pytest_bdd import scenarios

# Import all scenarios from the feature file
scenarios("auth.feature")
```

### Step 4: Run the Tests

Execute your BDD tests:

```bash
# Run all BDD tests
uv run pytest tests/bdd/ -v

# Run specific feature tests
uv run pytest tests/bdd/test_auth.py -v

# Run with BDD marker
uv run pytest -m bdd -v
```

## Best Practices

### Feature File Guidelines

1. **Use clear, business-focused language**: Write scenarios that stakeholders can understand
2. **Follow the Given-When-Then structure**:
   - **Given**: Set up the initial state/context
   - **When**: Perform the action being tested
   - **Then**: Verify the expected outcome
3. **Keep scenarios focused**: Each scenario should test one specific behavior
4. **Use descriptive scenario names**: Make it clear what behavior is being tested

### Step Definition Guidelines

1. **Keep steps reusable**: Write generic steps that can be used across multiple scenarios
2. **Use parsers for parameterization**: Use `parsers.parse()` for dynamic values
3. **Maintain test isolation**: Each scenario should be independent
4. **Use descriptive docstrings**: Document what each step does

### Common Step Patterns

#### CLI Command Execution
```python
@when(parsers.parse('I run the command "{command}"'))
def run_cli_command(command: str):
    runner = CliRunner()
    args = command.split()[1:]  # Remove 'sidekick' prefix
    result = runner.invoke(app, args)
    test_context["result"] = result
```

#### File System Operations
```python
@given(parsers.parse('I have a file "{filename}" with content "{content}"'))
def create_file_with_content(filename: str, content: str, tmp_path):
    file_path = tmp_path / filename
    file_path.write_text(content)
    test_context["file_path"] = file_path

@then(parsers.parse('the file "{filename}" should exist'))
def file_should_exist(filename: str, tmp_path):
    file_path = tmp_path / filename
    assert file_path.exists(), f"File {filename} does not exist"
```

#### Output Verification
```python
@then(parsers.parse('I should see "{text}"'))
def should_see_text(text: str):
    result = test_context["result"]
    assert text in result.stdout

@then(parsers.parse('the exit code should be {code:d}'))
def check_exit_code(code: int):
    result = test_context["result"]
    assert result.exit_code == code
```

#### Environment Setup
```python
@given(parsers.parse('the environment variable "{var}" is set to "{value}"'))
def set_environment_variable(var: str, value: str, monkeypatch):
    monkeypatch.setenv(var, value)
```

## Advanced Features

### Scenario Outlines (Data-Driven Tests)

Use scenario outlines to test multiple data sets:

```gherkin
Feature: Input Validation

  Scenario Outline: Validate email addresses
    Given I have an email address "<email>"
    When I run the command "sidekick validate email <email>"
    Then I should see "<result>"

    Examples:
      | email              | result  |
      | test@example.com   | Valid   |
      | invalid-email      | Invalid |
      | user@domain.co.uk  | Valid   |
```

### Background Steps

Use background steps for common setup:

```gherkin
Feature: Configuration Management

  Background:
    Given I have a clean configuration directory
    And I am in the project root directory

  Scenario: Create new configuration
    When I run the command "sidekick config init"
    Then I should see "Configuration initialized"
```

### Tags

Use tags to organize and filter tests:

```gherkin
@integration @slow
Feature: Database Operations

  @smoke
  Scenario: Basic connection test
    # This scenario will run with: pytest -m "smoke"
```

## Configuration

The project is configured for BDD testing in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = [
    "bdd: Behavior Driven Development tests",
]
bdd_features_base_dir = "tests/bdd/features"
```

## Debugging BDD Tests

### Common Issues

1. **Step Definition Not Found**: Ensure step definitions are imported in the test file
2. **Feature File Not Found**: Check the path in `scenarios()` call
3. **Ambiguous Steps**: Make step patterns specific enough to avoid conflicts

### Debugging Tips

1. **Use verbose output**: Run with `-v` flag to see detailed step execution
2. **Print intermediate values**: Add print statements in step definitions
3. **Use pytest fixtures**: Leverage pytest's powerful fixture system
4. **Isolate failing scenarios**: Run specific scenarios to isolate issues

### Example Debug Session

```bash
# Run with maximum verbosity
uv run pytest tests/bdd/test_auth.py::test_successful_login_with_valid_credentials -vvv

# Run with step-by-step output
uv run pytest tests/bdd/ -v --tb=short
```

## Integration with CI/CD

BDD tests integrate seamlessly with the existing test suite:

```bash
# Run all tests including BDD
uv run pytest

# Run only BDD tests
uv run pytest -m bdd

# Generate coverage report including BDD tests
uv run pytest --cov=src --cov-report=html
```

## Examples and Templates

### Template Feature File

```gherkin
Feature: [Feature Name]
  As a [user type]
  I want [goal]
  So that [benefit]

  Scenario: [Scenario Name]
    Given [initial context]
    When [action is performed]
    Then [expected outcome]
    And [additional verification]
```

### Template Step Definition File

```python
"""
Step definitions for [feature name] tests.

This module contains the step definitions for testing [feature description].
"""

from pytest_bdd import given, when, then, parsers
from typer.testing import CliRunner

from sidekick.cli.app import app

# Test context storage
test_context = {}

@given("[step description]")
def setup_step():
    """Set up test preconditions."""
    pass

@when(parsers.parse('[action with "{parameter}"]'))
def action_step(parameter: str):
    """Perform the main action being tested."""
    pass

@then(parsers.parse('[verification with "{expected}"]'))
def verification_step(expected: str):
    """Verify the expected outcome."""
    pass
```

This guide provides everything you need to write effective BDD tests for the sidekick CLI application. The key is to start simple and gradually build more complex scenarios as you become comfortable with the BDD approach.
