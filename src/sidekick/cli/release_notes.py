"""
Release Notes CLI commands.

This module provides CLI commands for generating release notes from Jira tickets.
"""

import asyncio

import typer
from loguru import logger
from rich.console import Console

from ..workflows.release_notes import ReleaseNotesGenerator

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
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output",
    ),
    use_mcp: bool = typer.Option(
        False,
        "--use-mcp/--no-mcp",
        help="Use MCP Atlassian server or our custom JiraTools",
    ),
) -> None:
    """
    Generate release notes from a Jira ticket.

    This command fetches information from a Jira ticket and its associated
    GitHub pull requests to generate comprehensive release notes.

    Example:
        sidekick release-notes generate PROJ-123
        sidekick release-notes generate PROJ-456 --format text --verbose
        sidekick release-notes generate PROJ-789 --no-mcp
    """
    logger.debug(f"Generate release notes called with ticket_id={ticket_id}, format={output_format}, use_mcp={use_mcp}")

    async def _generate():
        try:
            # Initialize the release notes generator workflow
            generator = ReleaseNotesGenerator(use_mcp=use_mcp)

            # Generate release notes
            result = await generator.generate_release_notes(
                ticket_id=ticket_id,
                output_format=output_format,
            )

            # Display results
            console.print("[bold blue]Release Notes Generator[/bold blue]")
            console.print(f"[dim]Ticket ID:[/dim] {ticket_id}")
            console.print(f"[dim]Output Format:[/dim] {output_format}")
            console.print(f"[dim]Session ID:[/dim] {result['session_id']}")
            console.print(f"[dim]Integration:[/dim] {'MCP Atlassian' if use_mcp else 'JiraTools'}")

            # Display Jira issue information
            jira_issue = result["jira_issue"]
            console.print(f"\n[bold green]Jira Ticket:[/bold green] {jira_issue['key']}")
            console.print(f"[dim]Summary:[/dim] {jira_issue['summary']}")
            console.print(f"[dim]Status:[/dim] {jira_issue['status']}")
            console.print(f"[dim]Priority:[/dim] {jira_issue['priority']}")

            # Display PR links
            pr_links = result["pr_links"]
            if pr_links:
                console.print(f"\n[bold cyan]Pull Requests Found:[/bold cyan] {len(pr_links)}")
                for pr_link in pr_links:
                    console.print(f"  • {pr_link}")
            else:
                console.print("\n[dim]No pull request links found in ticket[/dim]")

            # Display generated release notes
            console.print("\n[bold yellow]Generated Release Notes:[/bold yellow]")
            console.print(result["release_notes"])

            if verbose:
                console.print("\n[cyan]Debug Information:[/cyan]")
                console.print(f"  - Workflow version: {result['metadata']['workflow_version']}")
                console.print(f"  - Agents used: {', '.join(result['metadata']['agents_used'])}")
                console.print(f"  - Use MCP: {result['metadata']['use_mcp']}")
                console.print(f"  - Status: {result['status']}")

        except Exception as e:
            logger.error(f"Failed to generate release notes: {e}")
            console.print(f"\n[red]Error:[/red] {e}")
            console.print("\n[yellow]Note:[/yellow] Make sure you have the required environment variables set:")
            console.print("  - JIRA_SERVER_URL")
            console.print("  - JIRA_USERNAME")
            console.print("  - JIRA_TOKEN")
            console.print("  - GITHUB_ACCESS_TOKEN")

            if use_mcp:
                console.print("\n[cyan]MCP Integration:[/cyan]")
                console.print("  - Make sure 'uvx mcp-atlassian' is available")
                console.print("  - Try running with --no-mcp to use traditional JiraTools")

    # Run the async function
    asyncio.run(_generate())


@release_notes_app.command()
def info() -> None:
    """Show information about the release notes feature."""
    console.print("[bold blue]Release Notes Generator[/bold blue]")
    console.print("\nThis feature automates the creation of release notes by:")
    console.print("  • Fetching ticket details from Jira")
    console.print("  • Extracting GitHub pull request links")
    console.print("  • Gathering PR details and changes")
    console.print("  • Generating formatted release notes using AI")

    console.print("\n[bold]Integration Options:[/bold]")
    console.print("  • MCP Atlassian Server (default) - Uses mcp-atlassian via uvx")
    console.print("  • Traditional JiraTools - Uses agno.tools.jira.JiraTools")

    console.print("\n[bold]Required Environment Variables:[/bold]")
    console.print("  • JIRA_SERVER_URL - Your Jira server URL")
    console.print("  • JIRA_USERNAME - Jira username")
    console.print("  • JIRA_TOKEN - Jira API token")
    console.print("  • GITHUB_ACCESS_TOKEN - GitHub personal access token")

    console.print("\n[bold]Usage:[/bold]")
    console.print("  sidekick release-notes generate <TICKET_ID>")
    console.print("  sidekick release-notes generate PROJ-123 --format markdown --verbose")
    console.print("  sidekick release-notes generate PROJ-456 --no-mcp  # Use traditional JiraTools")


if __name__ == "__main__":
    release_notes_app()
