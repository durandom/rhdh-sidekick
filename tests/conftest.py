"""
Pytest configuration and fixtures for sidekick tests.

This module provides common fixtures and configuration for all tests.
"""

from pathlib import Path

import pytest
from loguru import logger

from sidekick.cli.app import setup_logging
from sidekick.settings import LoggingConfig


@pytest.fixture(scope="session", autouse=True)
def configure_test_logging():
    """Configure logging for test runs."""
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Clear the log file before starting tests
    log_file = logs_dir / "test-sidekick.log"
    if log_file.exists():
        log_file.unlink()

    # Configure test logging with file output
    test_config = LoggingConfig(
        level="DEBUG",
        format="pretty",
        file=log_file,
        pytest_mode=True,
        trace_enabled=True,
    )

    # Setup logging
    setup_logging(test_config)

    # Log test session start
    logger.info("=" * 50)
    logger.info("Starting sidekick test session")
    logger.info("=" * 50)

    yield

    # Log test session end
    logger.info("=" * 50)
    logger.info("sidekick test session completed")
    logger.info("=" * 50)


@pytest.fixture
def log_capture():
    """Capture log messages for testing."""

    # Create a custom log capture for loguru
    captured_logs = []

    def capture_handler(record):
        captured_logs.append(record)

    # Add capture handler
    handler_id = logger.add(capture_handler, level="TRACE")

    yield captured_logs

    # Remove capture handler
    logger.remove(handler_id)


def pytest_runtest_setup(item):
    """Log test execution start."""
    logger.info(f"🧪 Running test: {item.nodeid}")


def pytest_runtest_teardown(item, nextitem):
    """Log test execution completion."""
    logger.info(f"✅ Completed test: {item.nodeid}")


def pytest_runtest_logreport(report):
    """Log test results."""
    if report.when == "call":
        if report.passed:
            logger.info(f"✅ PASSED: {report.nodeid}")
        elif report.failed:
            logger.error(f"❌ FAILED: {report.nodeid}")
        elif report.skipped:
            logger.warning(f"⏭️ SKIPPED: {report.nodeid}")


@pytest.fixture
def reset_logging():
    """Reset logging configuration after test."""
    # Store original handlers (using type ignore for private access)
    original_handlers = logger._core.handlers.copy()  # type: ignore[attr-defined]

    yield

    # Restore original handlers
    logger.remove()
    for _handler_id, handler in original_handlers.items():
        logger.add(
            handler._sink,
            level=handler._levelno,
            format=handler._formatter._fmt,
            filter=handler._filter,
        )
