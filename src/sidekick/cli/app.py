"""
Main CLI application with command groups.

This module defines the main CLI application and registers all command groups.
"""

import contextlib
import os
import sys
from pathlib import Path

import typer
from agno.utils.pprint import pprint_run_response
from dotenv import load_dotenv
from loguru import logger
from rich.console import Console
from rich.prompt import Prompt

from ..agents import SearchAgent
from ..settings import LoggingConfig, settings
from .jira import jira_app
from .release_notes import release_notes_app
from .test_analysis import test_analysis_app

load_dotenv(verbose=True)  # take environment variables


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


app = typer.Typer(
    help="sidekick",
    add_completion=False,
    rich_markup_mode="rich",
)

# Register sub-applications
app.add_typer(release_notes_app)
app.add_typer(jira_app)
app.add_typer(test_analysis_app)

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
        os.environ["AGNO_DEBUG"] = "true"

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


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query string"),
) -> None:
    """Search for items matching the query using AI-powered RAG."""
    logger.debug(f"Search command called with query={query}")

    # Use AI agent for search
    agent = SearchAgent()

    # Initial search
    current_query = query
    while current_query.strip():
        logger.debug(f"Executing search with query: {current_query}")

        # Execute search
        response = agent.search(current_query)

        # Print response
        pprint_run_response(response, markdown=True, show_time=True)

        # Ask for next query
        console.print("\n[bold cyan]Enter your next search query (or press Enter to exit):[/bold cyan]")
        current_query = Prompt.ask("Search query", default="").strip()

        if not current_query:
            console.print("[dim]Exiting search session...[/dim]")
            break


if __name__ == "__main__":
    app()
