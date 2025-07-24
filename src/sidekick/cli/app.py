"""
Main CLI application with command groups.

This module defines the main CLI application and registers all command groups.
"""

import base64
import contextlib
import os
import sys
from pathlib import Path

import typer
from dotenv import load_dotenv
from loguru import logger
from openinference.instrumentation.agno import AgnoInstrumentor
from opentelemetry import trace as trace_api
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from rich.console import Console

from ..settings import LoggingConfig, settings
from .gdrive import gdrive_app
from .github import github_app
from .jira import jira_app
from .knowledge import knowledge_app
from .release_notes import release_notes_app
from .search import search_app
from .tag_team import tag_team_app
from .test_analysis import test_analysis_app

load_dotenv(verbose=True)  # take environment variables


def setup_langfuse() -> None:
    """Configure Langfuse tracing with OpenTelemetry."""
    try:
        # Set environment variables for Langfuse
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        host = os.getenv("LANGFUSE_HOST")

        if not all([public_key, secret_key, host]):
            logger.warning(
                "Langfuse configuration incomplete. Missing LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, or LANGFUSE_HOST"
            )
            return

        # At this point, we know all values are not None
        assert public_key is not None
        assert secret_key is not None
        assert host is not None

        langfuse_auth = base64.b64encode(f"{public_key}:{secret_key}".encode()).decode()

        os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = host
        os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {langfuse_auth}"

        # Configure the tracer provider
        tracer_provider = TracerProvider()
        tracer_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter()))
        trace_api.set_tracer_provider(tracer_provider=tracer_provider)

        # Start instrumenting agno
        AgnoInstrumentor().instrument()

        logger.info("Langfuse tracing enabled")

    except Exception as e:
        logger.error(f"Failed to setup Langfuse: {e}")


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
app.add_typer(gdrive_app)
app.add_typer(github_app)
app.add_typer(knowledge_app)
app.add_typer(release_notes_app)
app.add_typer(search_app)
app.add_typer(jira_app)
app.add_typer(tag_team_app)
app.add_typer(test_analysis_app)

# Add global options and commands
console = Console()

# Global streaming flag
_streaming_enabled = True


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
    langfuse: bool = typer.Option(
        False,
        "--langfuse",
        help="Enable Langfuse tracing (requires LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST)",
    ),
    no_streaming: bool = typer.Option(
        False,
        "--no-streaming",
        help="Disable streaming response output (streaming is enabled by default)",
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

    # Setup Langfuse if requested
    if langfuse:
        setup_langfuse()

    # Store streaming flag globally
    global _streaming_enabled
    _streaming_enabled = not no_streaming


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
