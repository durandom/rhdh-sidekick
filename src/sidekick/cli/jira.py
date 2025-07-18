"""
Jira CLI commands.

This module provides CLI commands for interacting with Jira tickets and issues.
"""

import asyncio

import typer
from agno.utils.pprint import pprint_run_response
from loguru import logger
from rich.console import Console
from rich.prompt import Prompt

from ..agents.jira_agent import JiraAgent

console = Console()

# Create the jira sub-application
jira_app = typer.Typer(
    name="jira",
    help="Interact with Jira tickets and issues",
    rich_markup_mode="rich",
)


@jira_app.command()
def chat(
    initial_question: str = typer.Argument(
        None,
        help="Initial question to ask the Jira agent",
    ),
    use_mcp: bool = typer.Option(
        False,
        "--use-mcp/--no-mcp",
        help="Use MCP Atlassian server or custom Jira tools (default)",
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
        sidekick jira chat --no-mcp "Find all open bugs"
    """
    logger.debug(f"Jira chat called with initial_question={initial_question}, use_mcp={use_mcp}")

    async def run_chat():
        try:
            # Initialize the Jira agent
            agent = JiraAgent(use_mcp=use_mcp)
            await agent.initialize()

            # Create a new session
            session_id = agent.create_session()
            console.print(f"[bold blue]Started Jira chat session[/bold blue] (ID: {session_id[:8]}...)")

            # Handle initial question if provided
            current_query = initial_question or ""

            if current_query:
                console.print(f"[bold green]Initial question:[/bold green] {current_query}")
                response = await agent.ask(current_query, session_id)
                pprint_run_response(response, markdown=True, show_time=True)

            # Start the interactive loop
            while True:
                console.print(
                    "\n[bold cyan]Ask a question about Jira tickets or issues (or press Enter to exit):[/bold cyan]"
                )
                current_query = Prompt.ask("Jira query", default="").strip()

                if not current_query:
                    console.print("[dim]Exiting Jira chat session...[/dim]")
                    break

                logger.debug(f"Processing Jira query: {current_query}")

                # Ask the agent
                response = await agent.ask(current_query, session_id)

                # Display the response
                pprint_run_response(response, markdown=True, show_time=True)

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
def ticket(
    ticket_id: str = typer.Argument(
        ...,
        help="Jira ticket ID (e.g., PROJ-123)",
    ),
    use_mcp: bool = typer.Option(
        False,
        "--use-mcp/--no-mcp",
        help="Use MCP Atlassian server or custom Jira tools (default)",
    ),
) -> None:
    """
    Fetch and display information about a specific Jira ticket.

    This command fetches detailed information about a Jira ticket including
    its summary, description, status, and any associated GitHub pull requests.

    Example:
        sidekick jira ticket PROJ-123
        sidekick jira ticket PROJ-456 --no-mcp
    """
    logger.debug(f"Jira ticket called with ticket_id={ticket_id}, use_mcp={use_mcp}")

    async def fetch_ticket():
        try:
            # Initialize the Jira agent
            agent = JiraAgent(use_mcp=use_mcp)
            await agent.initialize()

            # Fetch the ticket
            console.print(f"[bold blue]Fetching Jira ticket {ticket_id}...[/bold blue]")
            response = await agent.fetch_ticket(ticket_id)

            # Display the response
            pprint_run_response(response, markdown=True, show_time=True)

        except Exception as e:
            logger.error(f"Failed to fetch Jira ticket: {e}")
            console.print(f"\n[red]Error:[/red] {e}")
            console.print("\n[yellow]Note:[/yellow] Make sure you have the required environment variables set:")
            console.print("  - JIRA_URL")
            console.print("  - JIRA_PERSONAL_TOKEN")

    # Run the async function
    asyncio.run(fetch_ticket())


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

    console.print("\n[bold]Integration Options:[/bold]")
    console.print("  • Custom Jira tools (default) - Basic ticket operations")
    console.print("  • MCP Atlassian server - Full Jira API access")

    console.print("\n[bold]Required Environment Variables:[/bold]")
    console.print("  • JIRA_URL - Your Jira server URL")
    console.print("  • JIRA_PERSONAL_TOKEN - Jira API token")
    console.print("  • GITHUB_ACCESS_TOKEN - GitHub personal access token (optional)")

    console.print("\n[bold]Usage:[/bold]")
    console.print("  sidekick jira chat                    # Start interactive chat")
    console.print('  sidekick jira chat "Show me PROJ-123"  # Chat with initial question')
    console.print("  sidekick jira ticket PROJ-123         # Fetch specific ticket")
    console.print("  sidekick jira info                    # Show this information")

    console.print("\n[bold]Interactive Features:[/bold]")
    console.print("  • Ask questions about any Jira ticket")
    console.print("  • Search for tickets using natural language")
    console.print("  • Get explanations about ticket status and progress")
    console.print("  • Session-based conversation with context retention")
    console.print("  • Extract and analyze ticket relationships")


if __name__ == "__main__":
    jira_app()
