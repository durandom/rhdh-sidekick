"""
sidekick - Modern Python CLI Application Template

A modern Python CLI application template built with best practices including
Typer for CLI, Rich for beautiful output, and Pydantic for data validation.
"""

import sys

from loguru import logger
from rich.console import Console

from .cli.app import setup_logging

# Import settings and configure logging
from .settings import settings

__version__ = "0.1.0"

# Configure console for rich output
console = Console()


def main() -> None:
    """Main entry point for the CLI application template."""
    # Initial logging setup (will be reconfigured by CLI callback)
    setup_logging(settings.logging)

    # Import the main CLI app
    from .cli.app import app

    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        logger.exception("Unexpected error occurred")
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
