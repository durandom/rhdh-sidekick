"""
Example commands to demonstrate CLI patterns.

This module shows how to create command groups and individual commands
using the command registry pattern.
"""

import typer
from loguru import logger
from rich.console import Console
from rich.table import Table

from .cli.base import CommandGroup, command_registry
from .settings import settings

console = Console()


class ExampleCommands(CommandGroup):
    """Example command group demonstrating CLI patterns."""

    def create_app(self) -> typer.Typer:
        """Create the example commands app."""
        app = typer.Typer(help="Example commands demonstrating CLI patterns")

        @app.command()
        def hello(
            name: str = typer.Option("World", "--name", "-n", help="Name to greet"),
            count: int = typer.Option(1, "--count", "-c", help="Number of greetings"),
        ) -> None:
            """Say hello with customizable greeting."""
            logger.debug(f"Hello command called with name={name}, count={count}")

            for i in range(count):
                greeting = f"Hello, {name}!"
                if count > 1:
                    greeting += f" ({i + 1}/{count})"
                console.print(f"[bold green]{greeting}[/bold green]")

        @app.command()
        def config() -> None:
            """Show current configuration."""
            logger.debug("Config command called")

            table = Table(title="Current Configuration")
            table.add_column("Setting", style="cyan", no_wrap=True)
            table.add_column("Value", style="magenta")

            table.add_row("App Name", settings.app_name)
            table.add_row("Environment", settings.environment)
            table.add_row("Debug Mode", str(settings.debug))
            table.add_row("Log Level", settings.log_level)
            table.add_row("Log Format", settings.log_format)
            table.add_row("Log File", str(settings.log_file) if settings.log_file else "None")
            table.add_row("Color Output", str(settings.color_output))

            console.print(table)

        @app.command()
        def demo_error() -> None:
            """Demonstrate error handling and logging."""
            logger.info("Demonstrating error handling")
            try:
                # Simulate an operation that might fail
                1 / 0  # noqa: B018
            except ZeroDivisionError as e:
                logger.error(f"Division by zero error: {e}")
                console.print("[red]Error: Cannot divide by zero![/red]")
                raise typer.Exit(1) from e

        return app


# Register the example commands
command_registry.register("example", ExampleCommands)
