"""
Base classes and utilities for CLI commands.

This module provides common functionality for CLI commands including
logging setup, error handling, and base command classes.
"""

import contextlib
import sys
from abc import ABC, abstractmethod

import typer
from loguru import logger

from ..settings import LoggingConfig


def setup_logging(config: LoggingConfig) -> None:
    """Configure logging based on settings with enhanced functionality."""
    # Remove default handler
    logger.remove()

    # Add custom TRACE level if enabled and not already exists
    if config.trace_enabled:
        # TRACE level already exists, which is fine
        with contextlib.suppress(ValueError):
            logger.level("TRACE", no=5, color="<dim>", icon="🔍")

    # Determine effective log level
    level = config.level.upper()
    if level == "TRACE" and not config.trace_enabled:
        level = "DEBUG"  # Fallback if TRACE not enabled

    # Configure format based on settings
    if config.format == "json":
        format_str = (
            '{"time":"{time:YYYY-MM-DD HH:mm:ss}", "level":"{level}", '
            '"name":"{name}", "function":"{function}", "line":{line}, '
            '"message":"{message}"}'
        )
    else:
        # Enhanced pretty format with better spacing
        format_str = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>"
        )

    # Add console handler (stderr by default)
    logger.add(
        sys.stderr,
        format=format_str,
        level=level,
        colorize=config.format == "pretty",
        backtrace=True,
        diagnose=True,
    )

    # Add file handler if specified or in pytest mode
    if config.file:
        # Create logs directory if it doesn't exist
        log_path = config.file
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            log_path,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level=level,
            rotation="10 MB",
            retention="1 week",
            backtrace=True,
            diagnose=True,
        )

        # Log the file location for pytest mode
        if config.pytest_mode:
            logger.info(f"Pytest mode: Logging to {log_path}")

    # Log configuration info
    logger.debug(
        f"Logging configured: level={level}, format={config.format}, "
        f"file={config.file}, pytest_mode={config.pytest_mode}"
    )


class CommandGroup(ABC):
    """Abstract base class for CLI command groups."""

    @abstractmethod
    def create_app(self) -> typer.Typer:
        """Create the Typer app for this command group."""
        pass


class CommandRegistry:
    """Registry for managing CLI command groups."""

    def __init__(self) -> None:
        self._commands: dict[str, type[CommandGroup]] = {}

    def register(self, name: str, command_class: type[CommandGroup]) -> None:
        """Register a command group."""
        self._commands[name] = command_class

    def create_main_app(self) -> typer.Typer:
        """Create main app with all registered commands."""
        app = typer.Typer(
            help="sidekick - Modern Python CLI application template",
            add_completion=False,
            rich_markup_mode="rich",
        )

        for name, command_class in self._commands.items():
            command_instance = command_class()
            command_app = command_instance.create_app()
            app.add_typer(command_app, name=name)

        return app


# Global command registry
command_registry = CommandRegistry()
