"""
BDD tests for CLI help functionality.

This module contains the BDD test scenarios for testing CLI help output.
"""

# Import the step definitions first to register them
from pytest_bdd import scenarios

from .steps.cli_help_steps import *  # noqa: F401,F403

# Import all scenarios from the feature file
scenarios("cli_help.feature")
