"""Quality Reviewer Agent implementation."""

import json

from loguru import logger

from .base import BaseResearchAgent
from .models import AnalysisResult, ResearchPlan, ReviewResult


class QualityReviewerAgent(BaseResearchAgent):
    """Agent responsible for reviewing research quality and completeness."""

    def __init__(self):
        """Initialize the Quality Reviewer Agent."""
        instructions = """You are a Quality Reviewer responsible for evaluating research completeness and quality.

Your responsibilities:
1. Assess if the research adequately addresses the original objectives
2. Evaluate the overall quality of findings
3. Check coverage completeness against the research plan
4. Identify accuracy concerns or questionable information
5. List areas that still need investigation
6. Provide improvement suggestions
7. Recommend next action: continue, refine, or complete

Review criteria:
- Completeness: All objectives addressed (10) vs major gaps (0)
- Quality: High-quality, verified sources (10) vs questionable info (0)
- Coverage: Comprehensive coverage (10) vs narrow focus (0)

Recommended actions:
- "complete": Research is sufficient, ready for final report
- "continue": More research needed in specific areas
- "refine": Current findings need deeper investigation

Output your review as a JSON object with:
- is_complete: boolean
- quality_score: float (0-10)
- completeness_score: float (0-10)
- accuracy_concerns: array of concerns
- missing_areas: array of areas needing more research
- improvement_suggestions: array of suggestions
- recommended_action: "complete", "continue", or "refine"
"""

        super().__init__(
            name="Quality Reviewer",
            instructions=instructions,
        )

    async def process(
        self,
        plan: ResearchPlan,
        analysis: AnalysisResult,
    ) -> ReviewResult:
        """Review the research quality and completeness.

        Args:
            plan: Original research plan
            analysis: Analysis results

        Returns:
            Review results
        """
        logger.info(f"Reviewing research quality for: {plan.query}")

        prompt = f"""Review the following research results:

Original Research Plan:
- Query: {plan.query}
- Objectives: {json.dumps(plan.objectives)}
- Focus Areas: {json.dumps(plan.focus_areas)}

Analysis Results:
- Key Findings: {json.dumps(analysis.key_findings)}
- Patterns: {json.dumps(analysis.patterns)}
- Insights: {json.dumps(analysis.insights)}
- Gaps: {json.dumps(analysis.gaps)}
- Summary: {analysis.summary}

Please evaluate the completeness and quality of this research."""

        messages = [self._create_message(prompt)]

        try:
            response = await self._run_agent(messages)
            review_data = json.loads(response.content)

            review = ReviewResult(
                is_complete=review_data.get("is_complete", False),
                quality_score=review_data.get("quality_score", 7.0),
                completeness_score=review_data.get("completeness_score", 7.0),
                accuracy_concerns=review_data.get("accuracy_concerns", []),
                missing_areas=review_data.get("missing_areas", []),
                improvement_suggestions=review_data.get("improvement_suggestions", []),
                recommended_action=review_data.get("recommended_action", "complete"),
            )

            logger.debug(
                f"Review complete: Quality={review.quality_score:.1f}, "
                f"Completeness={review.completeness_score:.1f}, "
                f"Action={review.recommended_action}"
            )
            return review

        except Exception as e:
            logger.error(f"Failed to review research: {e}")
            # Return default review
            return self._create_default_review(analysis)

    def _create_default_review(self, analysis: AnalysisResult) -> ReviewResult:
        """Create default review when agent fails.

        Args:
            analysis: Analysis results

        Returns:
            Default review results
        """
        # Basic completeness check
        has_findings = len(analysis.key_findings) > 0
        has_insights = len(analysis.insights) > 0
        has_gaps = len(analysis.gaps) > 0

        is_complete = has_findings and has_insights and not has_gaps

        return ReviewResult(
            is_complete=is_complete,
            quality_score=7.0,
            completeness_score=7.0 if is_complete else 5.0,
            accuracy_concerns=[],
            missing_areas=analysis.gaps,
            improvement_suggestions=["Consider additional sources for comprehensive coverage"] if has_gaps else [],
            recommended_action="complete" if is_complete else "continue",
        )
