"""Analyst Agent implementation."""

import json

from loguru import logger

from .base import BaseResearchAgent
from .models import AnalysisResult, GradedInformation


class AnalystAgent(BaseResearchAgent):
    """Agent responsible for analyzing and structuring research findings."""

    def __init__(self):
        """Initialize the Analyst Agent."""
        instructions = """You are an Analyst responsible for processing and structuring research findings.

Your responsibilities:
1. Identify key findings from the graded information
2. Discover patterns and trends across multiple sources
3. Extract meaningful insights and conclusions
4. Identify contradictions between sources
5. Highlight knowledge gaps that need further research
6. Create a comprehensive summary of all findings

When analyzing:
- Look for common themes across sources
- Identify unique perspectives or novel insights
- Note any conflicting information
- Synthesize information into coherent findings
- Prioritize the most important discoveries

Output your analysis as a JSON object with:
- key_findings: Array of main discoveries
- patterns: Array of identified patterns or trends
- insights: Array of deeper insights and conclusions
- contradictions: Array of conflicting information
- gaps: Array of areas needing more research
- summary: Executive summary paragraph
"""

        super().__init__(
            name="Analyst",
            instructions=instructions,
        )

    async def process(self, graded_info: list[GradedInformation]) -> AnalysisResult:
        """Analyze graded information to extract findings and insights.

        Args:
            graded_info: List of graded information

        Returns:
            Analysis results
        """
        logger.info(f"Analyzing {len(graded_info)} pieces of graded information")

        # Sort by overall score to focus on most relevant
        sorted_info = sorted(graded_info, key=lambda x: x.overall_score, reverse=True)

        # Prepare information for analysis
        info_summary = []
        for item in sorted_info:
            info_summary.append(
                {
                    "title": item.information.title,
                    "score": item.overall_score,
                    "key_insights": item.importance.key_insights,
                    "content": item.information.snippet,
                }
            )

        prompt = f"""Analyze the following research findings:

{json.dumps(info_summary, indent=2)}

Please provide a comprehensive analysis identifying patterns, insights, and gaps."""

        messages = [self._create_message(prompt)]

        try:
            response = await self._run_agent(messages)

            # Check if response content is empty
            if not response.content or not response.content.strip():
                logger.warning("Received empty response from analyst agent")
                raise ValueError("Empty response content")

            analysis_data = json.loads(response.content)

            analysis = AnalysisResult(
                key_findings=analysis_data.get("key_findings", []),
                patterns=analysis_data.get("patterns", []),
                insights=analysis_data.get("insights", []),
                contradictions=analysis_data.get("contradictions", []),
                gaps=analysis_data.get("gaps", []),
                summary=analysis_data.get("summary", ""),
            )

            logger.debug(f"Analysis complete: {len(analysis.key_findings)} findings, {len(analysis.patterns)} patterns identified")
            return analysis

        except Exception as e:
            logger.error(f"Failed to analyze information: {e}")
            # Return basic analysis
            return self._create_basic_analysis(graded_info)

    def _create_basic_analysis(self, graded_info: list[GradedInformation]) -> AnalysisResult:
        """Create basic analysis when agent fails.

        Args:
            graded_info: List of graded information

        Returns:
            Basic analysis results
        """
        # Extract all key insights
        all_insights = []
        for item in graded_info:
            all_insights.extend(item.importance.key_insights)

        # Get topic from first item
        topic = graded_info[0].importance.topic if graded_info else "the research topic"

        return AnalysisResult(
            key_findings=[
                f"Found {len(graded_info)} relevant sources about {topic}",
                f"Identified {len(all_insights)} key insights across all sources",
            ],
            patterns=["Multiple sources discuss similar themes"],
            insights=all_insights[:5],  # Top 5 insights
            contradictions=[],
            gaps=["Further analysis needed for comprehensive results"],
            summary=f"Research on {topic} yielded {len(graded_info)} sources with various insights.",
        )
