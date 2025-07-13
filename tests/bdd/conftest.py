"""
Pytest configuration and fixtures for BDD tests.

This module provides common fixtures and configuration for BDD tests.
"""

from pathlib import Path

import pytest


@pytest.fixture
def cli_output() -> dict:
    """Fixture to capture CLI command output."""
    output_data = {"stdout": "", "stderr": "", "return_code": 0}
    return output_data


@pytest.fixture
def project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture
def sidekick_cli_path(project_root: Path) -> str:
    """Get the path to the sidekick CLI executable."""
    # In development, we'll use uv run to execute the CLI
    return "uv run sidekick"
