"""
Main CLI application with command groups.

This module defines the main CLI application and registers all command groups.
"""

from pathlib import Path

import typer
from rich.console import Console

# Import command modules to register them
from .. import commands  # noqa: F401
from ..settings import settings
from .base import command_registry, setup_logging

# Create main app
app = command_registry.create_main_app()

# Add global options and commands
console = Console()


@app.callback()
def main(
    verbose: int = typer.Option(
        0,
        "-v",
        "--verbose",
        count=True,
        help="Increase verbosity (-v=DEBUG, -vv=TRACE)",
    ),
    log_level: str | None = typer.Option(
        None,
        "--log-level",
        help="Set log level explicitly (TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    ),
    log_file: Path | None = typer.Option(
        None,
        "--log-file",
        help="Log to file (default: logs/sidekick.log in pytest mode)",
    ),
    log_format: str | None = typer.Option(
        None,
        "--log-format",
        help="Log format (pretty, json)",
    ),
) -> None:
    """sidekick - Modern Python CLI application template."""
    # Map verbose count to log levels
    level_map = {0: "INFO", 1: "DEBUG", 2: "TRACE"}

    # CLI options take precedence over environment variables
    if log_level:
        settings.log_level = log_level.upper()
    elif verbose > 0:
        settings.log_level = level_map.get(verbose, "TRACE")

    if log_file:
        settings.log_file = log_file

    if log_format:
        settings.log_format = log_format

    # Update settings and re-sync logging config
    # The sync_logging_config validator will be called automatically when we update settings
    settings.logging.level = settings.log_level
    settings.logging.format = settings.log_format
    if settings.log_file:
        settings.logging.file = settings.log_file

    setup_logging(settings.logging)


@app.command()
def version() -> None:
    """Show version information."""
    console.print("[bold blue]sidekick[/bold blue] version [bold green]0.1.0[/bold green]")


@app.command()
def info() -> None:
    """Show application information."""
    console.print("[bold blue]sidekick[/bold blue] - Modern Python CLI Application Template")
    console.print("Built with [bold]Typer[/bold], [bold]Rich[/bold], and [bold]Pydantic[/bold]")
    console.print("Type [bold]--help[/bold] for available commands")


if __name__ == "__main__":
    app()
