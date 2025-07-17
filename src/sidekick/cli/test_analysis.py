"""
Test Analysis CLI commands.

This module provides CLI commands for analyzing test failures from Prow CI logs.
"""

from pathlib import Path

import typer
from agno.agent import RunResponse
from agno.team import TeamRunResponse
from agno.utils.pprint import pprint_run_response
from loguru import logger
from rich.console import Console
from rich.prompt import Prompt

from ..agents.test_analysis_agent import TestAnalysisAgent
from ..teams.test_analysis_team import TestAnalysisTeam
from ..utils.test_analysis import TestArtifactDownloader

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
    cache_dir: str = typer.Option(
        "downloads",
        "--cache-dir",
        "-c",
        help="Use existing downloaded artifacts from this directory (from previous download command)",
    ),
    agent: bool = typer.Option(
        False,
        "--agent",
        "-a",
        help="Use the single agent instead of the team for analysis",
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

    The --cache-dir option allows you to reuse artifacts downloaded with the
    'download' command, which speeds up analysis and avoids re-downloading.

    Examples:
        # Analyze with automatic download
        sidekick test-analysis analyze "https://prow.ci.openshift.org/view/gs/test-platform-results/logs/pull/123/test-run-456"

        # Analyze using cached artifacts
        sidekick test-analysis download "https://prow.ci.openshift.org/view/gs/test-platform-results/logs/pull/123/test-run-456"
        sidekick test-analysis analyze \
            "https://prow.ci.openshift.org/view/gs/test-platform-results/logs/pull/123/test-run-456" \
            --cache-dir downloads/logs_pull_123_test-run-456
    """
    logger.debug(f"Test analysis called with prow_link={prow_link}")

    try:
        work_dir = Path(cache_dir) if cache_dir else None

        analyzer: TestAnalysisAgent | TestAnalysisTeam
        if agent:
            # Use the single agent
            analyzer = TestAnalysisAgent(work_dir=work_dir)
            console.print("[bold blue]Analyzing test failures using single agent...[/bold blue]")
        else:
            # Use the team (default behavior)
            analyzer = TestAnalysisTeam(prow_link=prow_link, work_dir=work_dir)
            console.print("[bold blue]Analyzing test failures using team...[/bold blue]")

        console.print(f"[dim]Link: {prow_link}[/dim]")

        if cache_dir:
            console.print(f"[dim]Using cached artifacts from: {cache_dir}[/dim]")

        response: RunResponse | TeamRunResponse
        if agent:
            assert isinstance(analyzer, TestAnalysisAgent)
            response = analyzer.analyze_test_failure(prow_link)
        else:
            assert isinstance(analyzer, TestAnalysisTeam)
            response = analyzer.analyze_test_failure()

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

            # Ask the analyzer (team or agent)
            response = analyzer.ask(current_query)

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
    console.print("[bold blue]Test Analysis Team[/bold blue]")
    console.print("\nThis feature uses a coordinate mode team to analyze test failures:")
    console.print("  • [bold]Team Leader[/bold]: Coordinates analysis and synthesizes findings")
    console.print("  • [bold]Screenshot Analyzer[/bold]: Analyzes visual evidence from test screenshots")
    console.print("  • [bold]Log Analyzer[/bold]: Processes JUnit XML, build logs, and pod logs")
    console.print("\n[bold]Analysis Process:[/bold]")
    console.print("  • Parses JUnit XML files for test failure details")
    console.print("  • Analyzes screenshots for visual confirmation")
    console.print("  • Reviews build logs for CI/deployment issues")
    console.print("  • Examines pod logs for container problems")
    console.print("  • Provides comprehensive root cause analysis using coordinated AI")
    console.print("  • Offers actionable recommendations for fixes")
    console.print("  • Supports interactive follow-up questions")

    console.print("\n[bold]Integration:[/bold]")
    console.print("  • Uses Google Cloud Storage for test artifacts")
    console.print("  • Uses Gemini AI for screenshot and log analysis")
    console.print("  • Supports Prow CI log format")

    console.print("\n[bold]Required Environment Variables:[/bold]")
    console.print("  • GOOGLE_APPLICATION_CREDENTIALS - Path to GCS service account key")
    console.print("  • GOOGLE_API_KEY - Google AI/Gemini API key")


@test_analysis_app.command()
def download(
    prow_link: str = typer.Argument(
        ...,
        help="Prow CI link to download artifacts from (e.g., https://prow.ci.openshift.org/view/gs/test-platform-results/logs/pull/123/test-run-456)",
    ),
    output_dir: str = typer.Option(
        "downloads",
        "--output-dir",
        "-o",
        help="Base directory to download artifacts to (default: downloads)",
    ),
) -> None:
    """
    Download all test artifacts from a Prow CI link for offline analysis.

    This command downloads all test artifacts including:
    - JUnit XML files with test results
    - Screenshots from failed tests
    - Build logs from CI/deployment
    - Pod logs from container issues

    The downloaded artifacts are organized in a structured directory layout
    and can be reused for multiple analysis runs without re-downloading.

    By default, artifacts are saved to downloads/{sanitized-url}/.
    For example, a URL like "logs/pull/123/test-run-456" becomes "downloads/logs_pull_123_test-run-456/".

    Examples:
        # Download to default location (downloads/{sanitized-url}/)
        sidekick test-analysis download "https://prow.ci.openshift.org/view/gs/test-platform-results/logs/pull/123/test-run-456"

        # Download to custom base directory (custom-dir/{sanitized-url}/)
        sidekick test-analysis download \
            "https://prow.ci.openshift.org/view/gs/test-platform-results/logs/pull/123/test-run-456" \
            -o /tmp/test-artifacts
    """
    logger.debug(f"Download called with prow_link={prow_link}, output_dir={output_dir}")

    try:
        # Initialize downloader - it handles everything
        downloader = TestArtifactDownloader(prow_link, output_dir)

        console.print(f"[bold blue]Downloading test artifacts from:[/bold blue] {downloader.base_dir}")
        console.print(f"[dim]Using output directory: {downloader.work_dir}[/dim]")

        # Download all artifacts
        console.print("[bold green]Starting artifact download...[/bold green]")
        artifacts = downloader.download_all_artifacts()

        # Display summary
        console.print("\n[bold green]Download completed![/bold green]")
        console.print(f"[dim]Download location: {downloader.work_dir}[/dim]")

        console.print("\n[bold]Downloaded artifacts:[/bold]")
        console.print(f"  • JUnit XML files: {len(artifacts['junit_files'])}")
        console.print(f"  • Build logs: {len(artifacts['build_logs'])}")
        console.print(f"  • Pod logs: {len(artifacts['pod_logs'])}")
        console.print(f"  • Screenshots: {len(artifacts['screenshots'])}")
        console.print(f"  • Other files: {len(artifacts['other_files'])}")

        if artifacts["failed_downloads"]:
            console.print(f"  • Failed downloads: {len(artifacts['failed_downloads'])}")
            console.print(f"    [dim]{artifacts['failed_downloads']}[/dim]")

        console.print("\n[bold]Directory structure:[/bold]")
        console.print(f"  {downloader.work_dir}/")
        console.print("  └── [all files organized by original directory structure]")

        console.print("\n[bold cyan]Tip:[/bold cyan] You can now run analysis using these cached artifacts.")
        console.print("The analyze command will automatically detect and reuse downloaded files.")

    except ValueError as e:
        logger.error(f"Invalid prow link: {e}")
        console.print(f"\n[red]Error:[/red] {e}")
        console.print("\n[yellow]Expected format:[/yellow]")
        console.print("  https://prow.ci.openshift.org/view/gs/test-platform-results/logs/...")
    except Exception as e:
        logger.error(f"Failed to download test artifacts: {e}")
        console.print(f"\n[red]Error:[/red] {e}")
        console.print("\n[yellow]Note:[/yellow] Make sure you have the required environment variables set:")
        console.print("  - GOOGLE_APPLICATION_CREDENTIALS (for GCS access)")
        console.print("\n[yellow]Also ensure:[/yellow]")
        console.print("  - You have access to the test-platform-results GCS bucket")

    console.print("\n[bold]Supported Prow Link Format:[/bold]")
    console.print("  https://prow.ci.openshift.org/view/gs/test-platform-results/logs/pull/123/test-run-456")

    console.print("\n[bold]Usage:[/bold]")
    console.print("  sidekick test-analysis analyze <PROW_LINK>")
    console.print("  sidekick test-analysis download <PROW_LINK> [--output-dir BASE_DIR]")
    console.print("  sidekick test-analysis analyze <PROW_LINK> --cache-dir downloads/{sanitized-url}")

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

    console.print("\n[bold]Caching Features:[/bold]")
    console.print("  • Download artifacts once with 'download' command")
    console.print("  • Reuse cached artifacts with --cache-dir option")
    console.print("  • Automatic cache checking to avoid re-downloading")
    console.print("  • Organized in downloads/{sanitized-url}/ structure")
    console.print("  • Predictable directory names for easy scripting")

    console.print("\n[bold]Example Analysis Output:[/bold]")
    console.print("  1. Test Case: [Test Name]")
    console.print("     a. Test Purpose: [What it was testing]")
    console.print("     b. Failure Message: [Error from JUnit XML]")
    console.print("     c. Root Cause Analysis: [Detailed analysis]")
    console.print("     d. Actionable Recommendations: [Specific fixes]")


if __name__ == "__main__":
    test_analysis_app()
