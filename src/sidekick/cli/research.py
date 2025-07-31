"""Research command implementation."""

import asyncio
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..agents.research import ResearchDepth

console = Console()

# Create the research application
research_app = typer.Typer(
    name="research",
    help="AI-powered research using multi-agent workflow",
    rich_markup_mode="rich",
    invoke_without_command=True,
    no_args_is_help=False,
)


@research_app.callback(invoke_without_command=True)
def research(
    query: str = typer.Argument(..., help="Research query or topic"),
    depth: ResearchDepth = typer.Option(ResearchDepth.STANDARD, "--depth", help="Research depth level"),
    format: str = typer.Option("markdown", "--format", help="Output format"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Save report to file"),
    max_rounds: int = typer.Option(3, "--max-rounds", help="Maximum research iterations"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed agent processes"),
    api_key: str | None = typer.Option(None, "--api-key", help="Anthropic API key (or use ANTHROPIC_API_KEY env var)"),
    no_web: bool = typer.Option(False, "--no-web", help="Disable web search"),
    no_local: bool = typer.Option(False, "--no-local", help="Disable local knowledge search"),
    no_arxiv: bool = typer.Option(False, "--no-arxiv", help="Disable arXiv search"),
    save_threshold: float = typer.Option(8.0, "--save-threshold", help="Minimum score to save to knowledge base (0-10)"),
    review_threshold: float = typer.Option(6.0, "--review-threshold", help="Minimum score for flagging for review (0-10)"),
):
    """Run AI-powered research on a topic using multi-agent workflow."""

    # Validate API key
    import os

    final_api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
    if not final_api_key:
        console.print(
            "[red]Error: Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable or use --api-key option.[/red]"
        )
        raise typer.Exit(1)

    # Validate thresholds
    if not (0 <= save_threshold <= 10):
        console.print("[red]Error: save-threshold must be between 0 and 10[/red]")
        raise typer.Exit(1)

    if not (0 <= review_threshold <= 10):
        console.print("[red]Error: review-threshold must be between 0 and 10[/red]")
        raise typer.Exit(1)

    if review_threshold > save_threshold:
        console.print("[red]Error: review-threshold cannot be higher than save-threshold[/red]")
        raise typer.Exit(1)

    # Validate format
    if format not in ["markdown", "json", "html"]:
        console.print("[red]Error: format must be one of: markdown, json, html[/red]")
        raise typer.Exit(1)

    # Set API key in environment
    os.environ["ANTHROPIC_API_KEY"] = final_api_key

    # Run the research
    try:
        asyncio.run(
            _run_research_workflow(
                query=query,
                depth=depth,
                format=format,
                output=output,
                max_rounds=max_rounds,
                verbose=verbose,
                no_web=no_web,
                no_local=no_local,
                no_arxiv=no_arxiv,
                save_threshold=save_threshold,
                review_threshold=review_threshold,
            )
        )

        if output:
            console.print(f"[green]✅ Research completed successfully! Report saved to: {output}[/green]")
        else:
            console.print("[green]✅ Research completed successfully![/green]")

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Research interrupted by user[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]❌ Research failed: {e}[/red]")
        if verbose:
            import traceback

            console.print(f"[red]Error details:\n{traceback.format_exc()}[/red]")
        raise typer.Exit(1)


async def _run_research_workflow(
    query: str,
    depth: ResearchDepth,
    format: str,
    output: Path | None,
    max_rounds: int,
    verbose: bool,
    no_web: bool,
    no_local: bool,
    no_arxiv: bool,
    save_threshold: float,
    review_threshold: float,
):
    """Run the research workflow."""
    from ..agents.research import ResearchQuery
    from ..workflows.research_workflow import run_research_workflow

    # Create research query
    research_query = ResearchQuery(
        query=query,
        depth=depth,
        max_rounds=max_rounds,
        save_threshold=save_threshold,
        review_threshold=review_threshold,
        no_web=no_web,
        no_local=no_local,
        no_arxiv=no_arxiv,
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=not verbose,
    ) as progress:
        if not verbose:
            task = progress.add_task("🔍 Running research workflow...", total=None)

        # Run the workflow
        result = await run_research_workflow(
            research_query,
            format=format,
            output_file=output,
            verbose=verbose,
        )

        if not verbose:
            progress.update(task, completed=True, description="✅ Research completed")

    return result


if __name__ == "__main__":
    research_app()
