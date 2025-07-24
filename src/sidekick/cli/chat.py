"""
Generic chat CLI command.

This module provides a unified chat interface for all agent types.
"""

import asyncio

import typer
from loguru import logger
from rich.console import Console

from ..agents import SearchAgent
from ..agents.github_agent import GitHubAgent
from ..agents.jira_agent import JiraAgent

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


async def run_search_agent(message: str | None, streaming_enabled: bool) -> None:
    """Run the search agent."""
    search_agent_factory = SearchAgent()

    console.print("[bold blue]Starting search chat session...[/bold blue]")

    # Initialize the agent asynchronously and get the underlying Agno Agent
    await search_agent_factory.ainitialize()
    agent = search_agent_factory._agent

    if agent is None:
        raise RuntimeError("Failed to initialize search agent")

    # Use agent.acli_app for the interactive chat loop
    await agent.acli_app(message=message, stream=streaming_enabled)


async def run_jira_agent(message: str | None, streaming_enabled: bool) -> None:
    """Run the Jira agent."""
    jira_agent_factory = JiraAgent()

    console.print("[bold blue]Starting Jira chat session...[/bold blue]")

    # Create MCP tools and agent using the factory pattern
    mcp_tools = jira_agent_factory.create_mcp_tools()

    # Use MCP tools as async context manager
    async with mcp_tools:
        # Create the agent within the MCP context
        agent = jira_agent_factory.create_agent(mcp_tools)

        # Use agent.acli_app for the interactive chat loop
        await agent.acli_app(message=message, stream=streaming_enabled)


async def run_github_agent(message: str | None, streaming_enabled: bool, repo: str | None = None) -> None:
    """Run the GitHub agent."""
    github_agent_factory = GitHubAgent(repository=repo)

    console.print("[bold blue]Starting GitHub chat session...[/bold blue]")
    if repo:
        console.print(f"[dim]Default repository: {repo}[/dim]")

    # Create GitHub tools
    github_tools = github_agent_factory.create_github_tools()

    # Create the agent
    agent = github_agent_factory.create_agent(github_tools)

    # Use agent.acli_app for the interactive chat loop
    await agent.acli_app(message=message, stream=streaming_enabled)


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
            await run_search_agent(message, streaming_enabled)
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
            await run_jira_agent(message, streaming_enabled)
        except Exception as e:
            logger.error(f"Failed to run Jira chat: {e}")
            console.print(f"\n[red]Error:[/red] {e}")
            console.print("\n[yellow]Note:[/yellow] Make sure you have the required environment variables set:")
            console.print("  - JIRA_URL")
            console.print("  - JIRA_PERSONAL_TOKEN")
            console.print("  - GITHUB_ACCESS_TOKEN (optional)")

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
            await run_github_agent(message, streaming_enabled, repo)
        except Exception as e:
            logger.error(f"Failed to run GitHub chat: {e}")
            console.print(f"\n[red]Error:[/red] {e}")
            console.print("\n[yellow]Note:[/yellow] Make sure you have the required environment variable set:")
            console.print("  - GITHUB_ACCESS_TOKEN")

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

    console.print("\n[bold]Usage:[/bold]")
    console.print("  sidekick chat search                          # Start search agent")
    console.print("  sidekick chat jira                            # Start Jira agent")
    console.print("  sidekick chat github                          # Start GitHub agent")
    console.print("  sidekick chat github --repo owner/repo        # GitHub with default repo")
    console.print('  sidekick chat search "your query"            # Agent with initial message')

    console.print("\n[bold]Features:[/bold]")
    console.print("  • Interactive chat sessions with context retention")
    console.print("  • Real-time streaming responses")
    console.print("  • Natural language queries")
    console.print("  • Session-based conversation flow")

    console.print("\n[bold]Environment Variables:[/bold]")
    console.print("  • JIRA_URL, JIRA_PERSONAL_TOKEN - For Jira agent")
    console.print("  • GITHUB_ACCESS_TOKEN - For GitHub agent")


if __name__ == "__main__":
    chat_app()
