"""Report Generator Agent implementation."""

import json
from datetime import datetime
from pathlib import Path

from loguru import logger

from .base import BaseResearchAgent
from .models import AnalysisResult, GradedInformation, ResearchQuery, ResearchReport, ReviewResult


class ReportGeneratorAgent(BaseResearchAgent):
    """Agent responsible for generating the final research report."""

    def __init__(self):
        """Initialize the Report Generator Agent."""
        instructions = """You are a Report Generator responsible for creating comprehensive research reports.

Your responsibilities:
1. Synthesize all findings into a coherent report
2. Structure the report with clear sections
3. Include proper citations and references
4. Create an executive summary
5. Format according to user preferences (markdown/json/html)

Report structure:
1. Title and metadata
2. Executive Summary (2-3 paragraphs)
3. Introduction
4. Key Findings (organized by theme)
5. Analysis and Insights
6. Conclusions
7. References

When generating reports:
- Use clear, professional language
- Organize information logically
- Highlight important discoveries
- Include all relevant sources
- Make the report actionable

Output the report structure as a JSON object with:
- title: Report title
- executive_summary: 2-3 paragraph summary
- sections: Array of {title, content} objects
- sources: Array of {title, url, type} objects
"""

        super().__init__(
            name="Report Generator",
            instructions=instructions,
        )

    async def process(
        self,
        query: ResearchQuery,
        graded_info: list[GradedInformation],
        analysis: AnalysisResult,
        review: ReviewResult,
        format: str = "markdown",
    ) -> ResearchReport:
        """Generate the final research report.

        Args:
            query: Original research query
            graded_info: All graded information
            analysis: Analysis results
            review: Review results
            format: Output format (markdown/json/html)

        Returns:
            Research report
        """
        logger.info(f"Generating {format} report for: {query.query}")

        # Prepare data for report generation
        high_quality_sources = [item for item in graded_info if item.overall_score >= 7.0]

        prompt = f"""Generate a comprehensive research report for:

Query: {query.query}

Analysis Summary:
{analysis.summary}

Key Findings:
{json.dumps(analysis.key_findings, indent=2)}

Insights:
{json.dumps(analysis.insights, indent=2)}

Quality Review:
- Quality Score: {review.quality_score}/10
- Completeness: {review.completeness_score}/10

Top Sources ({len(high_quality_sources)}):
{self._format_sources(high_quality_sources)}

Please create a well-structured report in {format} format."""

        messages = [self._create_message(prompt)]

        try:
            response = await self._run_agent(messages)
            report_data = json.loads(response.content)

            # Create sources list
            sources = []
            for item in graded_info:
                if item.overall_score >= 6.0:  # Include reasonably good sources
                    sources.append(
                        {
                            "title": item.information.title,
                            "url": item.information.source_url or "N/A",
                            "type": item.information.source_type.value,
                            "score": f"{item.overall_score:.1f}",
                        }
                    )

            report = ResearchReport(
                title=report_data.get("title", f"Research Report: {query.query}"),
                query=query.query,
                executive_summary=report_data.get("executive_summary", analysis.summary),
                sections=report_data.get("sections", self._create_default_sections(analysis)),
                sources=sources,
                metadata={
                    "generated_by": "sidekick research",
                    "quality_score": str(review.quality_score),
                    "completeness_score": str(review.completeness_score),
                },
                generated_at=datetime.now(),
                format=format,
            )

            logger.debug(f"Generated report with {len(report.sections)} sections")
            return report

        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            # Return basic report
            return self._create_basic_report(query, analysis, graded_info, format)

    def _format_sources(self, sources: list[GradedInformation]) -> str:
        """Format sources for the prompt.

        Args:
            sources: List of graded information

        Returns:
            Formatted string
        """
        formatted = []
        for item in sources[:5]:  # Top 5 sources
            formatted.append(f"- {item.information.title} (Score: {item.overall_score:.1f}, Type: {item.information.source_type.value})")
        return "\n".join(formatted)

    def _create_default_sections(self, analysis: AnalysisResult) -> list[dict[str, str]]:
        """Create default report sections.

        Args:
            analysis: Analysis results

        Returns:
            List of sections
        """
        return [
            {
                "title": "Introduction",
                "content": "This report presents the findings from our comprehensive research.",
            },
            {
                "title": "Key Findings",
                "content": "\n".join(f"• {finding}" for finding in analysis.key_findings),
            },
            {
                "title": "Analysis and Insights",
                "content": "\n".join(f"• {insight}" for insight in analysis.insights),
            },
            {
                "title": "Conclusions",
                "content": analysis.summary,
            },
        ]

    def _create_basic_report(
        self,
        query: ResearchQuery,
        analysis: AnalysisResult,
        graded_info: list[GradedInformation],
        format: str,
    ) -> ResearchReport:
        """Create a basic report when agent fails.

        Args:
            query: Research query
            analysis: Analysis results
            graded_info: Graded information
            format: Output format

        Returns:
            Basic research report
        """
        sources = []
        for item in graded_info[:10]:  # Top 10 sources
            sources.append(
                {
                    "title": item.information.title,
                    "url": item.information.source_url or "N/A",
                    "type": item.information.source_type.value,
                    "score": f"{item.overall_score:.1f}",
                }
            )

        return ResearchReport(
            title=f"Research Report: {query.query}",
            query=query.query,
            executive_summary=analysis.summary or f"Research conducted on {query.query}",
            sections=self._create_default_sections(analysis),
            sources=sources,
            metadata={"generated_by": "sidekick research"},
            generated_at=datetime.now(),
            format=format,
        )

    async def save_report_to_file(
        self,
        report: ResearchReport,
        output_dir: Path | None = None,
        filename_prefix: str = "research_report",
    ) -> Path:
        """Save a research report to a markdown file.

        Args:
            report: Research report to save
            output_dir: Directory to save the report (default: ./reports)
            filename_prefix: Prefix for the filename

        Returns:
            Path to the saved report file
        """
        # Create output directory if not specified
        if output_dir is None:
            output_dir = Path("reports")
        output_dir.mkdir(exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = report.query.replace("?", "").replace(" ", "_").replace("'", "")[:50]
        filename = f"{filename_prefix}_{safe_topic}_{timestamp}.md"
        report_path = output_dir / filename

        # Generate markdown content
        content = self._generate_markdown_report(report)

        # Save to file
        logger.info(f"Saving report to: {report_path}")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(content)

        return report_path

    def _generate_markdown_report(self, report: ResearchReport) -> str:
        """Generate markdown content from a research report.

        Args:
            report: Research report

        Returns:
            Markdown formatted report content
        """
        lines = []

        # Header
        lines.append(f"# {report.title}")
        lines.append("")
        lines.append(f"Generated on: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Executive Summary
        lines.append("## Executive Summary")
        lines.append("")
        lines.append(report.executive_summary)
        lines.append("")

        # Main sections
        for section in report.sections:
            lines.append(f"## {section['title']}")
            lines.append("")
            lines.append(section["content"])
            lines.append("")

        # References
        if report.sources:
            lines.append("## References")
            lines.append("")
            for source in report.sources:
                score = source.get("score", "N/A")
                url = source.get("url", "N/A")
                source_type = source.get("type", "unknown")
                lines.append(f"- **{source['title']}** (Score: {score}, Type: {source_type})")
                lines.append(f"  URL: {url}")
                lines.append("")

        # Footer
        lines.append("---")
        lines.append("")
        lines.append("*This report was automatically generated by the sidekick research team.*")

        return "\n".join(lines)
