"""
BDD tests for search command functionality.

This module contains the BDD test scenarios for testing search command features.
"""

# Import the step definitions first to register them

from .steps.search_steps import *  # noqa: F401,F403

# Import all scenarios from the feature file
# this requires a connection to a model
# scenarios("search.feature")
