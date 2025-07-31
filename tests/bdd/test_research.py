"""
BDD tests for research command functionality.

This module contains the BDD test scenarios for testing research features.
"""

# Import the step definitions first to register them
from pytest_bdd import scenarios

from .steps.research_steps import *  # noqa: F401,F403

# Import all scenarios from the feature file
scenarios("research.feature")
