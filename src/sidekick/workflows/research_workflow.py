"""Research Workflow implementation using coordinated agents."""

from pathlib import Path

from loguru import logger

from ..agents.research import (AnalystAgent, GradedInformation, GradingAgent, InformationGathererAgent, QualityReviewerAgent,
                               ReportGeneratorAgent, ResearchCoordinatorAgent, ResearchQuery, ResearchResult, ReviewResult)


async def save_relevant_knowledge(graded_data: list[GradedInformation], save_threshold: float) -> list[GradedInformation]:
    """Save high-scoring knowledge to knowledge base.

    Args:
        graded_data: List of graded information
        save_threshold: Minimum score to save

    Returns:
        List of saved knowledge items
    """
    saved_items = []

    logger.info(f"Evaluating {len(graded_data)} items for knowledge base storage")

    for item in graded_data:
        if item.overall_score >= save_threshold:
            saved_items.append(item)
            logger.debug(f"Marked for saving: {item.information.title}")

            # Save to research knowledge directory
            await _save_research_item_to_file(item)

    logger.info(f"Saved {len(saved_items)} items to knowledge base")
    return saved_items


async def _save_research_item_to_file(item: GradedInformation) -> None:
    """Save a research item to the knowledge directory as a markdown file.

    Args:
        item: Graded information to save
    """
    try:
        # Create research knowledge directory
        research_knowledge_dir = Path("knowledge/research")
        research_knowledge_dir.mkdir(parents=True, exist_ok=True)

        # Generate safe filename
        safe_title = "".join(c for c in item.information.title if c.isalnum() or c in (" ", "-", "_")).rstrip()
        safe_title = safe_title.replace(" ", "_")[:50]  # Limit length
        filename = f"{safe_title}_{item.information.source_type.value}.md"

        file_path = research_knowledge_dir / filename

        # Generate markdown content
        content = f"""# {item.information.title}

**Source:** {item.information.source_url or "N/A"}
**Type:** {item.information.source_type.value}
**Relevance Score:** {item.importance.relevance_score}/10
**Quality Score:** {item.importance.quality_score}/10
**Novelty Score:** {item.importance.novelty_score}/10
**Overall Score:** {item.overall_score}/10

## Importance Statement

{item.importance.importance_reason}

## Key Insights

{chr(10).join(f"- {insight}" for insight in item.importance.key_insights)}

## Content

{item.information.content}

## Metadata

{chr(10).join(f"- **{k}:** {v}" for k, v in item.information.metadata.items())}

---

*Saved from research on: {item.information.gathered_at.strftime("%Y-%m-%d %H:%M:%S")}*
*Tags: {", ".join(item.importance.recommended_tags)}*
"""

        # Write to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.debug(f"Saved research item to: {file_path}")

    except Exception as e:
        logger.error(f"Failed to save research item to file: {e}")
        # Don't raise - this shouldn't break the research workflow


def should_continue_research(review: ReviewResult, current_round: int, max_rounds: int) -> bool:
    """Determine if research should continue based on completeness.

    Args:
        review: Review result
        current_round: Current research round
        max_rounds: Maximum allowed rounds

    Returns:
        True if research should continue, False otherwise
    """
    is_incomplete = not review.is_complete
    under_limit = current_round < max_rounds

    should_continue = is_incomplete and under_limit

    logger.info(
        f"Research continuation check: Round {current_round}/{max_rounds}, Complete: {not is_incomplete}, Continue: {should_continue}"
    )

    return should_continue


class ResearchWorkflow:
    """Coordinated research workflow using multiple agents."""

    def __init__(self, model_id: str = "claude-3-5-sonnet-20241022"):
        """Initialize the research workflow.

        Args:
            model_id: Claude model ID to use for agents
        """
        self.model_id = model_id

        # Initialize agents
        self.coordinator_agent = ResearchCoordinatorAgent()
        self.gatherer_agent = InformationGathererAgent()
        self.grader_agent = GradingAgent()
        self.analyst_agent = AnalystAgent()
        self.reviewer_agent = QualityReviewerAgent()
        self.generator_agent = ReportGeneratorAgent()

    async def run(
        self,
        research_query: ResearchQuery,
        verbose: bool = False,
    ) -> ResearchResult:
        """Execute the research workflow.

        Args:
            research_query: Research query and parameters
            verbose: Whether to show detailed execution logs

        Returns:
            Complete research results
        """
        logger.info(f"Starting research workflow for: {research_query.query}")

        try:
            # Step 1: Create initial research plan
            if verbose:
                logger.info("Step 1: Creating research plan")

            research_plan = await self.coordinator_agent.process(research_query)
            current_round = 0
            all_graded_data: list[GradedInformation] = []

            # Step 2: Iterative research loop
            while current_round < research_query.max_rounds:
                current_round += 1

                if verbose:
                    logger.info(f"Step 2.{current_round}: Research iteration {current_round}")

                # Gather information
                if verbose:
                    logger.info("  - Gathering information")
                gathered_info = await self.gatherer_agent.process(research_plan)

                # Grade information
                if verbose:
                    logger.info("  - Grading information quality")
                graded_data = await self.grader_agent.process(gathered_info, research_query)
                all_graded_data.extend(graded_data)

                # Save relevant knowledge
                if verbose:
                    logger.info("  - Saving relevant knowledge")
                saved_knowledge = await save_relevant_knowledge(graded_data, research_query.save_threshold)

                # Analyze findings
                if verbose:
                    logger.info("  - Analyzing findings")
                analysis = await self.analyst_agent.process(all_graded_data)

                # Review for completeness
                if verbose:
                    logger.info("  - Reviewing quality and completeness")
                review = await self.reviewer_agent.process(research_plan, analysis)

                # Check if we should continue
                if not should_continue_research(review, current_round, research_query.max_rounds):
                    break

                # Update research plan if continuing
                if verbose:
                    logger.info("  - Updating research plan")
                feedback = {
                    "missing_areas": review.missing_areas,
                    "improvement_suggestions": review.improvement_suggestions,
                }
                research_plan = await self.coordinator_agent.update_plan(research_plan, feedback)

            # Step 3: Generate final report
            if verbose:
                logger.info("Step 3: Generating final report")

            report = await self.generator_agent.process(research_query, all_graded_data, analysis, review)

            # Create final result
            research_result = ResearchResult(
                query=research_query,
                plan=research_plan,
                findings=all_graded_data,
                analysis=analysis,
                review=review,
                report=report,
                saved_knowledge=saved_knowledge,
                iterations_completed=current_round,
            )

            logger.info(f"Research workflow completed: {len(all_graded_data)} findings, {len(saved_knowledge)} saved to knowledge base")

            return research_result

        except Exception as e:
            logger.error(f"Research workflow failed: {e}")
            raise


# Global workflow instance
_research_workflow: ResearchWorkflow | None = None


def get_research_workflow(model_id: str = "claude-3-5-sonnet-20241022") -> ResearchWorkflow:
    """Get or create the global research workflow instance.

    Args:
        model_id: Claude model ID to use

    Returns:
        ResearchWorkflow instance
    """
    global _research_workflow
    if _research_workflow is None:
        _research_workflow = ResearchWorkflow(model_id=model_id)
    return _research_workflow


async def run_research_workflow(
    research_query: ResearchQuery,
    format: str = "markdown",
    output_file: Path | None = None,
    verbose: bool = False,
    model_id: str = "claude-3-5-sonnet-20241022",
) -> ResearchResult:
    """Run the complete research workflow and optionally save the report.

    Args:
        research_query: Research query and parameters
        format: Output format for the report
        output_file: Optional file path to save the report
        verbose: Whether to show detailed execution logs
        model_id: Claude model ID to use

    Returns:
        Complete research results
    """
    # Get workflow instance
    workflow = get_research_workflow(model_id)

    # Run the workflow
    result = await workflow.run(research_query, verbose=verbose)

    # Save report if requested
    if output_file:
        # Update report format
        result.report.format = format

        # Save to file
        generator = ReportGeneratorAgent()
        saved_path = await generator.save_report_to_file(
            report=result.report,
            output_dir=output_file.parent if output_file.parent != Path(".") else None,
            filename_prefix=output_file.stem if output_file.stem else "research_report",
        )

        logger.info(f"Report saved to: {saved_path}")

    # Display report to console if no output file
    elif not output_file and not verbose:
        from rich.console import Console
        from rich.markdown import Markdown

        console = Console()

        if format == "markdown":
            # Generate markdown content
            generator = ReportGeneratorAgent()
            markdown_content = generator._generate_markdown_report(result.report)
            console.print(Markdown(markdown_content))
        else:
            # Show basic report info
            console.print(f"[bold green]Research Report: {result.report.title}[/bold green]")
            console.print(f"\n{result.report.executive_summary}")

            for section in result.report.sections:
                console.print(f"\n[bold]{section['title']}[/bold]")
                console.print(section["content"])

    return result
