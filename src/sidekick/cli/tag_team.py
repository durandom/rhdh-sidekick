"""
Tag Team CLI commands.

This module provides CLI commands for interacting with the Tag Team,
which coordinates Jira and GitHub operations through specialized agents.
"""

import asyncio

import typer
from loguru import logger
from rich.console import Console

from ..teams.tag_team import TagTeam

console = Console()


def get_streaming_enabled() -> bool:
    """Get the global streaming flag from the main app module."""
    try:
        from .app import _streaming_enabled

        return _streaming_enabled
    except ImportError:
        return True  # Default to streaming enabled


# Create the tag-team sub-application
tag_team_app = typer.Typer(
    name="tag-team",
    help="Coordinate Jira and GitHub operations with specialized agents",
    rich_markup_mode="rich",
)


@tag_team_app.command()
def chat(
    message: str = typer.Argument(
        None,
        help="Initial message to send to the Tag Team",
    ),
    repository: str = typer.Option(
        None,
        "--repo",
        "-r",
        help="Default GitHub repository (format: owner/repo)",
    ),
) -> None:
    """
    Start an interactive chat session with the Tag Team.

    The Tag Team coordinates between Jira and GitHub specialists to help with:
    - Linking Jira tickets to GitHub PRs
    - Analyzing ticket requirements and corresponding code changes
    - Cross-platform project tracking and management
    - Bug investigation across both platforms

    Example:
        sidekick tag-team chat
        sidekick tag-team chat "Find PRs related to ticket PROJ-123"
        sidekick tag-team chat --repo owner/repo "Show me recent activity"
    """
    logger.debug(f"Tag team chat called with message={message}, repository={repository}")

    async def run_chat():
        try:
            # Create the Tag Team
            tag_team = TagTeam(repository=repository)

            # Get streaming preference
            streaming_enabled = get_streaming_enabled()

            console.print("[bold blue]Starting Tag Team chat session...[/bold blue]")
            console.print("[dim]Coordinating Jira and GitHub specialists...[/dim]")

            # Use the team's async CLI app method (this will initialize automatically)
            await tag_team.acli_app(message=message, stream=streaming_enabled, markdown=True)

        except Exception as e:
            logger.error(f"Failed to run Tag Team chat: {e}")
            console.print(f"\n[red]Error:[/red] {e}")
            console.print("\n[yellow]Note:[/yellow] Make sure you have the required environment variables set:")
            console.print("  - JIRA_URL")
            console.print("  - JIRA_PERSONAL_TOKEN")
            console.print("  - GITHUB_ACCESS_TOKEN")

    # Run the async function
    asyncio.run(run_chat())


@tag_team_app.command()
def info() -> None:
    """Show information about the Tag Team integration."""
    console.print("[bold blue]Tag Team Integration[/bold blue]")
    console.print("\nThe Tag Team coordinates Jira and GitHub operations through specialized agents:")

    console.print("\n[bold]Team Members:[/bold]")
    console.print("  • [cyan]Jira Specialist[/cyan] - Manages tickets, searches issues, analyzes requirements")
    console.print("  • [green]GitHub Specialist[/green] - Handles repositories, PRs, and code analysis")

    console.print("\n[bold]Capabilities:[/bold]")
    console.print("  • Link Jira tickets to GitHub pull requests")
    console.print("  • Analyze ticket requirements and corresponding code changes")
    console.print("  • Cross-platform project tracking and management")
    console.print("  • Bug investigation across both Jira and GitHub")
    console.print("  • Feature development workflow coordination")
    console.print("  • Code review with business context from tickets")
    console.print("  • [cyan]Persistent chat history[/cyan] - remembers conversation context within sessions")
    console.print("  • [yellow]Shared session state[/yellow] - tracks analyzed tickets, PRs, and discovered links")
    console.print(
        "  • [magenta]Investigation tracking[/magenta] - maintains focus and builds context across interactions"
    )

    console.print("\n[bold]Integration:[/bold]")
    console.print("  • Uses MCP Atlassian server for full Jira API access")
    console.print("  • Uses Agno GitHub tools for repository operations")

    console.print("\n[bold]Required Environment Variables:[/bold]")
    console.print("  • JIRA_URL - Your Jira server URL")
    console.print("  • JIRA_PERSONAL_TOKEN - Jira API token")
    console.print("  • GITHUB_ACCESS_TOKEN - GitHub personal access token")

    console.print("\n[bold]Usage:[/bold]")
    console.print("  sidekick tag-team chat                              # Start interactive chat")
    console.print("  sidekick tag-team chat --repo owner/repo            # Chat with default repository")
    console.print('  sidekick tag-team chat "Find PRs for PROJ-123"      # Chat with initial question')
    console.print("  sidekick tag-team info                              # Show this information")

    console.print("\n[bold]Example Workflows:[/bold]")
    console.print('  • [dim]"Show me ticket PROJ-123 and any related PRs"[/dim]')
    console.print('  • [dim]"Find all open PRs for user/repo and check for linked tickets"[/dim]')
    console.print('  • [dim]"Analyze the implementation of feature ABC-456"[/dim]')
    console.print('  • [dim]"What tickets are blocking the current sprint?"[/dim]')


if __name__ == "__main__":
    tag_team_app()
