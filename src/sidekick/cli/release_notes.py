"""
Release Notes CLI commands.

This module provides CLI commands for generating release notes from Jira tickets.
"""

import typer
from agno.utils.pprint import pprint_run_response
from loguru import logger
from rich.console import Console
from rich.prompt import Prompt

from ..agents.release_notes_agent import ReleaseNotesAgent

console = Console()

# Create the release notes sub-application
release_notes_app = typer.Typer(
    name="release-notes",
    help="Generate release notes from Jira tickets",
    rich_markup_mode="rich",
)


@release_notes_app.command()
def generate(
    ticket_id: str = typer.Argument(
        ...,
        help="Jira ticket ID (e.g., PROJ-123)",
    ),
    output_format: str = typer.Option(
        "markdown",
        "--format",
        "-f",
        help="Output format (markdown, text)",
    ),
) -> None:
    """
    Generate release notes from a Jira ticket with interactive follow-up.

    This command fetches information from a Jira ticket and its associated
    GitHub pull requests to generate comprehensive release notes. After
    generating the initial release notes, you can ask follow-up questions
    or request modifications.

    Example:
        sidekick release-notes generate PROJ-123
        sidekick release-notes generate PROJ-456 --format text
    """
    logger.debug(f"Generate release notes called with ticket_id={ticket_id}, format={output_format}")

    try:
        # Initialize the release notes agent
        agent = ReleaseNotesAgent()

        # Generate initial release notes
        console.print(f"[bold blue]Generating release notes for {ticket_id}...[/bold blue]")
        response = agent.generate_release_notes(ticket_id, output_format=output_format)

        # Display the response
        pprint_run_response(response, markdown=True, show_time=True)

        # Start the ask loop
        current_query = ""
        while True:
            console.print(
                "\n[bold cyan]Enter your follow-up question or modification request "
                "(or press Enter to exit):[/bold cyan]"
            )
            current_query = Prompt.ask("Follow-up query", default="").strip()

            if not current_query:
                console.print("[dim]Exiting release notes session...[/dim]")
                break

            logger.debug(f"Processing follow-up query: {current_query}")

            # Ask the agent
            response = agent.ask(current_query)

            # Display the response
            pprint_run_response(response, markdown=True, show_time=True)

    except Exception as e:
        logger.error(f"Failed to generate release notes: {e}")
        console.print(f"\n[red]Error:[/red] {e}")
        console.print("\n[yellow]Note:[/yellow] Make sure you have the required environment variables set:")
        console.print("  - JIRA_SERVER_URL")
        console.print("  - JIRA_USERNAME")
        console.print("  - JIRA_TOKEN")
        console.print("  - GITHUB_ACCESS_TOKEN")


@release_notes_app.command()
def info() -> None:
    """Show information about the release notes feature."""
    console.print("[bold blue]Release Notes Generator[/bold blue]")
    console.print("\nThis feature automates the creation of release notes by:")
    console.print("  • Fetching ticket details from Jira")
    console.print("  • Extracting GitHub pull request links")
    console.print("  • Gathering PR details and changes")
    console.print("  • Generating formatted release notes using AI")
    console.print("  • Providing an interactive ask loop for follow-up questions")

    console.print("\n[bold]Integration:[/bold]")
    console.print("  • Uses agno.tools.jira.JiraTools for Jira integration")

    console.print("\n[bold]Required Environment Variables:[/bold]")
    console.print("  • JIRA_SERVER_URL - Your Jira server URL")
    console.print("  • JIRA_USERNAME - Jira username")
    console.print("  • JIRA_TOKEN - Jira API token")
    console.print("  • GITHUB_ACCESS_TOKEN - GitHub personal access token")

    console.print("\n[bold]Usage:[/bold]")
    console.print("  sidekick release-notes generate <TICKET_ID>")
    console.print("  sidekick release-notes generate PROJ-123 --format markdown")

    console.print("\n[bold]Interactive Features:[/bold]")
    console.print("  • Ask follow-up questions about the release notes")
    console.print("  • Request modifications to the format or content")
    console.print("  • Get explanations about specific changes")
    console.print("  • Session-based conversation with context retention")


if __name__ == "__main__":
    release_notes_app()
