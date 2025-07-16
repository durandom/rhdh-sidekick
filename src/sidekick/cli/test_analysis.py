"""
Test Analysis CLI commands.

This module provides CLI commands for analyzing test failures from Prow CI logs.
"""

import typer
from agno.utils.pprint import pprint_run_response
from loguru import logger
from rich.console import Console
from rich.prompt import Prompt

from ..agents.test_analysis_agent import TestAnalysisAgent

console = Console()

# Create the test analysis sub-application
test_analysis_app = typer.Typer(
    name="test-analysis",
    help="Analyze test failures from Prow CI logs",
    rich_markup_mode="rich",
)


@test_analysis_app.command()
def analyze(
    prow_link: str = typer.Argument(
        ...,
        help="Prow CI link to analyze (e.g., https://prow.ci.openshift.org/view/gs/test-platform-results/logs/pull/123/test-run-456)",
    ),
) -> None:
    """
    Analyze test failures from a Prow CI link with interactive follow-up.

    This command analyzes test failures from Prow CI logs including:
    - JUnit XML parsing for test failure details
    - Screenshot analysis for visual confirmation
    - Build log analysis for CI/deployment issues
    - Pod log analysis for container problems

    After generating the initial analysis, you can ask follow-up questions
    or request additional information.

    Example:
        sidekick test-analysis analyze "https://prow.ci.openshift.org/view/gs/test-platform-results/logs/pull/123/test-run-456"
    """
    logger.debug(f"Test analysis called with prow_link={prow_link}")

    try:
        # Initialize the test analysis agent
        agent = TestAnalysisAgent()

        # Analyze test failures
        console.print("[bold blue]Analyzing test failures from prow link...[/bold blue]")
        console.print(f"[dim]Link: {prow_link}[/dim]")

        response = agent.analyze_test_failure(prow_link)

        # Display the response
        pprint_run_response(response, markdown=True, show_time=True)

        # Start the ask loop
        current_query = ""
        while True:
            console.print(
                "\n[bold cyan]Enter your follow-up question or request for additional analysis "
                "(or press Enter to exit):[/bold cyan]"
            )
            current_query = Prompt.ask("Follow-up query", default="").strip()

            if not current_query:
                console.print("[dim]Exiting test analysis session...[/dim]")
                break

            logger.debug(f"Processing follow-up query: {current_query}")

            # Ask the agent
            response = agent.ask(current_query)

            # Display the response
            pprint_run_response(response, markdown=True, show_time=True)

    except Exception as e:
        logger.error(f"Failed to analyze test failures: {e}")
        console.print(f"\n[red]Error:[/red] {e}")
        console.print("\n[yellow]Note:[/yellow] Make sure you have the required environment variables set:")
        console.print("  - GOOGLE_APPLICATION_CREDENTIALS (for GCS access)")
        console.print("  - GOOGLE_API_KEY (for Gemini AI)")
        console.print("\n[yellow]Also ensure:[/yellow]")
        console.print("  - The prow link is in the correct format")
        console.print("  - You have access to the test-platform-results GCS bucket")


@test_analysis_app.command()
def info() -> None:
    """Show information about the test analysis feature."""
    console.print("[bold blue]Test Analysis Tool[/bold blue]")
    console.print("\nThis feature automates the analysis of test failures by:")
    console.print("  • Parsing JUnit XML files for test failure details")
    console.print("  • Analyzing screenshots for visual confirmation")
    console.print("  • Reviewing build logs for CI/deployment issues")
    console.print("  • Examining pod logs for container problems")
    console.print("  • Providing comprehensive root cause analysis using AI")
    console.print("  • Offering actionable recommendations for fixes")
    console.print("  • Supporting interactive follow-up questions")

    console.print("\n[bold]Integration:[/bold]")
    console.print("  • Uses Google Cloud Storage for test artifacts")
    console.print("  • Uses Gemini AI for screenshot and log analysis")
    console.print("  • Supports Prow CI log format")

    console.print("\n[bold]Required Environment Variables:[/bold]")
    console.print("  • GOOGLE_APPLICATION_CREDENTIALS - Path to GCS service account key")
    console.print("  • GOOGLE_API_KEY - Google AI/Gemini API key")

    console.print("\n[bold]Supported Prow Link Format:[/bold]")
    console.print("  https://prow.ci.openshift.org/view/gs/test-platform-results/logs/pull/123/test-run-456")

    console.print("\n[bold]Usage:[/bold]")
    console.print("  sidekick test-analysis analyze <PROW_LINK>")

    console.print("\n[bold]Analysis Features:[/bold]")
    console.print("  • Automatic extraction of base directory from prow links")
    console.print("  • Systematic analysis of e2e test directories")
    console.print("  • JUnit XML parsing for failed test suites")
    console.print("  • AI-powered screenshot analysis")
    console.print("  • Build log and pod log analysis")
    console.print("  • Structured output with root cause and recommendations")

    console.print("\n[bold]Interactive Features:[/bold]")
    console.print("  • Ask follow-up questions about specific failures")
    console.print("  • Request deeper analysis of particular components")
    console.print("  • Get clarification on recommendations")
    console.print("  • Session-based conversation with context retention")

    console.print("\n[bold]Example Analysis Output:[/bold]")
    console.print("  1. Test Case: [Test Name]")
    console.print("     a. Test Purpose: [What it was testing]")
    console.print("     b. Failure Message: [Error from JUnit XML]")
    console.print("     c. Root Cause Analysis: [Detailed analysis]")
    console.print("     d. Actionable Recommendations: [Specific fixes]")


if __name__ == "__main__":
    test_analysis_app()
