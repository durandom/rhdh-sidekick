"""
Search CLI commands.

This module provides CLI commands for AI-powered search functionality.
"""

import asyncio

import typer
from loguru import logger
from rich.console import Console

from ..agents import SearchAgent

console = Console()


def get_streaming_enabled() -> bool:
    """Get the global streaming flag from the main app module."""
    try:
        from .app import _streaming_enabled

        return _streaming_enabled
    except ImportError:
        return True  # Default to streaming enabled


# Create the search sub-application
search_app = typer.Typer(
    name="search",
    help="AI-powered search functionality",
    rich_markup_mode="rich",
)


@search_app.command()
def chat(
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
        sidekick search chat
        sidekick search chat "Find documentation about API endpoints"
        sidekick search chat "Show me examples of error handling"
    """
    logger.debug(f"Search chat called with message={message}")

    async def run_chat():
        try:
            # Create the search agent factory
            search_agent_factory = SearchAgent()

            # Get streaming preference
            streaming_enabled = get_streaming_enabled()

            console.print("[bold blue]Starting search chat session...[/bold blue]")

            # Initialize the agent asynchronously and get the underlying Agno Agent
            await search_agent_factory.ainitialize()
            agent = search_agent_factory._agent

            if agent is None:
                raise RuntimeError("Failed to initialize search agent")

            # Use agent.acli_app for the interactive chat loop
            await agent.acli_app(message=message, stream=streaming_enabled)

        except Exception as e:
            logger.error(f"Failed to run search chat: {e}")
            console.print(f"\n[red]Error:[/red] {e}")
            console.print("\n[yellow]Note:[/yellow] Make sure the search agent is properly configured.")

    # Run the async function
    asyncio.run(run_chat())


@search_app.command()
def info() -> None:
    """Show information about the search functionality."""
    console.print("[bold blue]AI-Powered Search[/bold blue]")
    console.print("\nThis feature provides AI-powered search using RAG (Retrieval-Augmented Generation):")
    console.print("  • Interactive chat sessions with AI-powered search")
    console.print("  • Streaming responses by default for real-time output")
    console.print("  • Context-aware search using AI agents")
    console.print("  • Session-based conversation with context retention")

    console.print("\n[bold]Usage:[/bold]")
    console.print("  sidekick search chat                          # Start interactive chat")
    console.print('  sidekick search chat "your query"            # Chat with initial question')
    console.print("  sidekick search info                          # Show this information")

    console.print("\n[bold]Interactive Features:[/bold]")
    console.print("  • Ask questions using natural language")
    console.print("  • Real-time streaming responses")
    console.print("  • Context-aware conversation flow")
    console.print("  • Debug logging for troubleshooting")

    console.print("\n[bold]Example Queries:[/bold]")
    console.print('  • "Find documentation about API endpoints"')
    console.print('  • "Show me examples of error handling"')
    console.print('  • "What are the latest features in this project?"')
    console.print('  • "Explain how authentication works"')


if __name__ == "__main__":
    search_app()
