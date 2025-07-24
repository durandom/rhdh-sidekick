"""
Jira CLI commands.

This module provides CLI commands for interacting with Jira tickets and issues.
"""

import asyncio

import typer
from loguru import logger
from rich.console import Console

from ..agents.jira_agent import JiraAgent

console = Console()


def get_streaming_enabled() -> bool:
    """Get the global streaming flag from the main app module."""
    try:
        from .app import _streaming_enabled

        return _streaming_enabled
    except ImportError:
        return True  # Default to streaming enabled


# Create the jira sub-application
jira_app = typer.Typer(
    name="jira",
    help="Interact with Jira tickets and issues",
    rich_markup_mode="rich",
)


@jira_app.command()
def chat(
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
        sidekick jira chat
        sidekick jira chat "Show me ticket PROJ-123"
        sidekick jira chat "Find all open bugs"
    """
    logger.debug(f"Jira chat called with message={message}")

    async def run_chat():
        try:
            # Create the Jira agent factory
            jira_agent_factory = JiraAgent()

            # Get streaming preference
            streaming_enabled = get_streaming_enabled()

            console.print("[bold blue]Starting Jira chat session...[/bold blue]")

            # Create MCP tools and agent using the factory pattern
            mcp_tools = jira_agent_factory.create_mcp_tools()

            # Use MCP tools as async context manager
            async with mcp_tools:
                # Create the agent within the MCP context
                agent = jira_agent_factory.create_agent(mcp_tools)

                # Use agent.acli_app for the interactive chat loop
                await agent.acli_app(message=message, stream=streaming_enabled)

        except Exception as e:
            logger.error(f"Failed to run Jira chat: {e}")
            console.print(f"\n[red]Error:[/red] {e}")
            console.print("\n[yellow]Note:[/yellow] Make sure you have the required environment variables set:")
            console.print("  - JIRA_URL")
            console.print("  - JIRA_PERSONAL_TOKEN")
            console.print("  - GITHUB_ACCESS_TOKEN (optional)")

    # Run the async function
    asyncio.run(run_chat())


@jira_app.command()
def info() -> None:
    """Show information about the Jira integration."""
    console.print("[bold blue]Jira Integration[/bold blue]")
    console.print("\nThis feature provides interactive access to Jira tickets and issues:")
    console.print("  • Chat with an AI agent about Jira tickets")
    console.print("  • Fetch detailed ticket information")
    console.print("  • Search for tickets based on criteria")
    console.print("  • Analyze ticket content and relationships")
    console.print("  • Extract GitHub PR links from tickets")

    console.print("\n[bold]Integration:[/bold]")
    console.print("  • Uses MCP Atlassian server for full Jira API access")

    console.print("\n[bold]Required Environment Variables:[/bold]")
    console.print("  • JIRA_URL - Your Jira server URL")
    console.print("  • JIRA_PERSONAL_TOKEN - Jira API token")
    console.print("  • GITHUB_ACCESS_TOKEN - GitHub personal access token (optional)")

    console.print("\n[bold]Usage:[/bold]")
    console.print("  sidekick jira chat                    # Start interactive chat")
    console.print('  sidekick jira chat "Show me PROJ-123"  # Chat with initial question')
    console.print("  sidekick jira info                    # Show this information")

    console.print("\n[bold]Interactive Features:[/bold]")
    console.print("  • Ask questions about any Jira ticket")
    console.print("  • Search for tickets using natural language")
    console.print("  • Get explanations about ticket status and progress")
    console.print("  • Session-based conversation with context retention")
    console.print("  • Extract and analyze ticket relationships")


if __name__ == "__main__":
    jira_app()
