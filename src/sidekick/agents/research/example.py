"""Example usage of the refactored research team."""

import asyncio
from pathlib import Path

from .coordinator import ResearchTeam
from .generator import ReportGeneratorAgent
from .models import ResearchReport


async def run_research_team(topic: str, output_dir: Path = None):
    """Run the research team on a topic and save the report.

    Args:
        topic: Research topic
        output_dir: Directory to save reports
    """
    # Create research team
    team = ResearchTeam(
        arxiv_download_dir=Path("tmp/arxiv_pdfs"),
        enable_all_agents=True,
        model_id="claude-3-5-sonnet-20241022",
    )

    # Run research
    print(f"🔍 Starting research on: {topic}")

    # Collect response
    full_response = ""
    final_response = None

    response_stream = await team.run_research(topic, stream=True)

    async for response in response_stream:
        if hasattr(response, "content") and response.content:
            full_response += response.content
        final_response = response

    # Use the final response content if available
    if final_response and hasattr(final_response, "content") and final_response.content:
        report_text = final_response.content
    else:
        report_text = full_response

    # Create a report object
    report = ResearchReport(
        title=f"Research Report: {topic}",
        query=topic,
        executive_summary=report_text[:500] + "...",  # First 500 chars as summary
        sections=[
            {
                "title": "Full Research Findings",
                "content": report_text,
            }
        ],
        sources=[],  # Would be populated from the team's findings
        metadata={
            "generated_by": "sidekick research team",
            "team_mode": "collaborative",
        },
    )

    # Save report
    report_gen = ReportGeneratorAgent()
    report_path = await report_gen.save_report_to_file(
        report=report,
        output_dir=output_dir,
    )

    print(f"✅ Report saved to: {report_path}")
    return report_path


def main():
    """Example main function."""
    # Example topic
    topic = "How did Robinson Crusoe manage to bake bread?"

    # Run the research
    asyncio.run(run_research_team(topic))


if __name__ == "__main__":
    main()
