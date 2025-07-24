"""
GitHub CLI commands.

This module provides CLI commands for interacting with GitHub repositories and issues.
"""

import asyncio

import typer
from loguru import logger
from rich.console import Console

from ..agents.github_agent import GitHubAgent

console = Console()


def get_streaming_enabled() -> bool:
    """Get the global streaming flag from the main app module."""
    try:
        from .app import _streaming_enabled

        return _streaming_enabled
    except ImportError:
        return True  # Default to streaming enabled


# Create the github sub-application
github_app = typer.Typer(
    name="github",
    help="Interact with GitHub repositories and issues",
    rich_markup_mode="rich",
)


@github_app.command()
def chat(
    message: str = typer.Argument(
        None,
        help="Initial message to send to the GitHub agent",
    ),
    repo: str = typer.Option(
        None,
        "--repo",
        "-r",
        help="Default repository to work with (format: owner/repo)",
    ),
) -> None:
    """
    Start an interactive chat session with the GitHub agent.

    This command initializes a GitHub agent and allows you to ask questions
    about repositories, pull requests, issues, and perform other GitHub-related
    tasks in an interactive loop.

    Example:
        sidekick github chat
        sidekick github chat "Show me open PRs"
        sidekick github chat --repo agno-agi/agno "List recent issues"
        sidekick github chat -r myorg/myrepo "What's the latest release?"
    """
    logger.debug(f"GitHub chat called with message={message}, repo={repo}")

    async def run_chat():
        try:
            # Create the GitHub agent factory
            github_agent_factory = GitHubAgent(repository=repo)

            # Get streaming preference
            streaming_enabled = get_streaming_enabled()

            console.print("[bold blue]Starting GitHub chat session...[/bold blue]")
            if repo:
                console.print(f"[dim]Default repository: {repo}[/dim]")

            # Create GitHub tools
            github_tools = github_agent_factory.create_github_tools()

            # Create the agent
            agent = github_agent_factory.create_agent(github_tools)

            # Use agent.acli_app for the interactive chat loop
            await agent.acli_app(message=message, stream=streaming_enabled)

        except Exception as e:
            logger.error(f"Failed to run GitHub chat: {e}")
            console.print(f"\n[red]Error:[/red] {e}")
            console.print("\n[yellow]Note:[/yellow] Make sure you have the required environment variable set:")
            console.print("  - GITHUB_ACCESS_TOKEN")

    # Run the async function
    asyncio.run(run_chat())


@github_app.command()
def info() -> None:
    """Show information about the GitHub integration."""
    console.print("[bold blue]GitHub Integration[/bold blue]")
    console.print("\nThis feature provides interactive access to GitHub repositories and issues:")
    console.print("  • Chat with an AI agent about GitHub repositories")
    console.print("  • Search for repositories")
    console.print("  • List repositories for users or organizations")
    console.print("  • Get detailed repository information")
    console.print("  • List and analyze pull requests")
    console.print("  • Get pull request details and file changes")
    console.print("  • Create issues (when explicitly requested)")

    console.print("\n[bold]Integration:[/bold]")
    console.print("  • Uses agno.tools.github for GitHub API access")

    console.print("\n[bold]Required Environment Variables:[/bold]")
    console.print("  • GITHUB_ACCESS_TOKEN - GitHub personal access token")

    console.print("\n[bold]Usage:[/bold]")
    console.print("  sidekick github chat                           # Start interactive chat")
    console.print("  sidekick github chat --repo owner/repo         # Chat with default repo")
    console.print('  sidekick github chat "Show me open PRs"        # Chat with initial question')
    console.print("  sidekick github info                           # Show this information")

    console.print("\n[bold]Interactive Features:[/bold]")
    console.print("  • Ask questions about any GitHub repository")
    console.print("  • Search for repositories using natural language")
    console.print("  • Get explanations about PR status and changes")
    console.print("  • Session-based conversation with context retention")
    console.print("  • Analyze repository activity and contributions")
    console.print("  • Create issues when explicitly requested")

    console.print("\n[bold]Example Queries:[/bold]")
    console.print('  • "Show me the latest pull requests"')
    console.print('  • "What are the open issues in this repository?"')
    console.print('  • "Search for Python repositories about machine learning"')
    console.print('  • "Get details about pull request #123"')
    console.print('  • "What changed in the latest PR?"')


if __name__ == "__main__":
    github_app()
