"""
Generic chat CLI command.

This module provides a unified chat interface for all agent types.
"""

import asyncio

import typer
from loguru import logger
from rich.console import Console

from ..agents import SearchAgent
from ..agents.base import BaseAgentFactory
from ..agents.github_agent import GitHubAgent
from ..agents.jira_agent import JiraAgent
from ..teams.tag_team import TagTeam

console = Console()


def get_streaming_enabled() -> bool:
    """Get the global streaming flag from the main app module."""
    try:
        from .app import _streaming_enabled

        return _streaming_enabled
    except ImportError:
        return True  # Default to streaming enabled


# Create the chat sub-application
chat_app = typer.Typer(
    name="chat",
    help="Interactive chat with AI agents",
    rich_markup_mode="rich",
)


async def run_agent_chat(
    agent_factory: BaseAgentFactory,
    message: str | None,
    streaming_enabled: bool,
    **kwargs,
) -> None:
    """Generic chat runner for any agent factory.

    Args:
        agent_factory: Agent factory instance
        message: Initial message
        streaming_enabled: Whether to enable streaming
        **kwargs: Additional keyword arguments passed to agent creation
    """
    # Display agent name
    agent_name = agent_factory.get_display_name()
    console.print(f"[bold blue]Starting {agent_name} chat session...[/bold blue]")

    # Display any extra info (e.g., default repository for GitHub)
    for info in agent_factory.get_extra_info():
        console.print(info)

    # Use the standard initialization pattern for all agents
    agent = await agent_factory.initialize_agent()

    try:
        # Run the interactive chat loop
        await agent.acli_app(message=message, stream=streaming_enabled)
    finally:
        # Cleanup any resources
        await agent_factory.cleanup()


@chat_app.command()
def search(
    message: str = typer.Argument(
        None,
        help="Initial message to send to the search agent",
    ),
) -> None:
    """
    Start an interactive chat session with the search agent.

    This command initializes a search agent and allows you to ask questions
    using AI-powered RAG (Retrieval-Augmented Generation) in an interactive
    chat session.

    Example:
        sidekick chat search
        sidekick chat search "Find documentation about API endpoints"
        sidekick chat search "Show me examples of error handling"
    """
    logger.debug(f"Chat search called with message={message}")

    async def run_chat():
        try:
            streaming_enabled = get_streaming_enabled()
            agent_factory = SearchAgent()
            await run_agent_chat(agent_factory, message, streaming_enabled)
        except Exception as e:
            logger.error(f"Failed to run search chat: {e}")
            console.print(f"\n[red]Error:[/red] {e}")
            console.print("\n[yellow]Note:[/yellow] Make sure the search agent is properly configured.")

    asyncio.run(run_chat())


@chat_app.command()
def jira(
    message: str = typer.Argument(
        None,
        help="Initial message to send to the Jira agent",
    ),
) -> None:
    """
    Start an interactive chat session with the Jira agent.

    This command initializes a Jira agent and allows you to ask questions
    about tickets, search for issues, and perform other Jira-related tasks
    in an interactive loop.

    Example:
        sidekick chat jira
        sidekick chat jira "Show me ticket PROJ-123"
        sidekick chat jira "Find all open bugs"
    """
    logger.debug(f"Chat jira called with message={message}")

    async def run_chat():
        try:
            streaming_enabled = get_streaming_enabled()
            agent_factory = JiraAgent()
            await run_agent_chat(agent_factory, message, streaming_enabled)
        except Exception as e:
            logger.error(f"Failed to run Jira chat: {e}")
            console.print(f"\n[red]Error:[/red] {e}")
            console.print("\n[yellow]Note:[/yellow] Make sure you have the required environment variables set:")
            for env_var in agent_factory.get_required_env_vars():
                console.print(f"  - {env_var}")

    asyncio.run(run_chat())


@chat_app.command()
def github(
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
        sidekick chat github
        sidekick chat github "Show me open PRs"
        sidekick chat github --repo agno-agi/agno "List recent issues"
        sidekick chat github -r myorg/myrepo "What's the latest release?"
    """
    logger.debug(f"Chat github called with message={message}, repo={repo}")

    async def run_chat():
        try:
            streaming_enabled = get_streaming_enabled()
            agent_factory = GitHubAgent(repository=repo)
            await run_agent_chat(agent_factory, message, streaming_enabled)
        except Exception as e:
            logger.error(f"Failed to run GitHub chat: {e}")
            console.print(f"\n[red]Error:[/red] {e}")
            console.print("\n[yellow]Note:[/yellow] Make sure you have the required environment variable set:")
            for env_var in agent_factory.get_required_env_vars():
                console.print(f"  - {env_var}")

    asyncio.run(run_chat())


@chat_app.command()
def team(
    message: str = typer.Argument(
        None,
        help="Initial message to send to the Tag Team",
    ),
    repo: str = typer.Option(
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
        sidekick chat team
        sidekick chat team "Find PRs related to ticket PROJ-123"
        sidekick chat team --repo owner/repo "Show me recent activity"
    """
    logger.debug(f"Tag team chat called with message={message}, repo={repo}")

    async def run_chat():
        try:
            # Get streaming preference
            streaming_enabled = get_streaming_enabled()

            console.print("[bold blue]Starting Tag Team chat session...[/bold blue]")
            console.print("[dim]Coordinating Jira and GitHub specialists...[/dim]")

            # Use the Tag Team as async context manager to properly setup MCP tools
            async with TagTeam(repository=repo) as tag_team:
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


@chat_app.command()
def info() -> None:
    """Show information about the chat functionality."""
    console.print("[bold blue]Interactive AI Chat[/bold blue]")
    console.print("\nThis feature provides unified access to different AI agents:")

    console.print("\n[bold]Available Agents:[/bold]")
    console.print("  • [cyan]search[/cyan] - AI-powered search using RAG")
    console.print("  • [cyan]jira[/cyan] - Jira ticket and issue management")
    console.print("  • [cyan]github[/cyan] - GitHub repository and PR management")
    console.print("  • [cyan]team[/cyan] - Coordinated Jira & GitHub operations")

    console.print("\n[bold]Usage:[/bold]")
    console.print("  sidekick chat search                          # Start search agent")
    console.print("  sidekick chat jira                            # Start Jira agent")
    console.print("  sidekick chat github                          # Start GitHub agent")
    console.print("  sidekick chat team                            # Start Tag Team")
    console.print("  sidekick chat github --repo owner/repo        # GitHub with default repo")
    console.print("  sidekick chat team --repo owner/repo          # Tag Team with default repo")
    console.print('  sidekick chat search "your query"            # Agent with initial message')

    console.print("\n[bold]Features:[/bold]")
    console.print("  • Interactive chat sessions with context retention")
    console.print("  • Real-time streaming responses")
    console.print("  • Natural language queries")
    console.print("  • Session-based conversation flow")

    console.print("\n[bold]Environment Variables:[/bold]")
    console.print("  • JIRA_URL, JIRA_PERSONAL_TOKEN - For Jira agent")
    console.print("  • GITHUB_ACCESS_TOKEN - For GitHub agent")
    console.print("  • Both Jira and GitHub variables - For Tag Team")


if __name__ == "__main__":
    chat_app()
