"""Grading Agent implementation."""

import json

from loguru import logger

from .base import BaseResearchAgent
from .models import GatheredInformation, GradedInformation, ImportanceStatement, ResearchQuery


class GradingAgent(BaseResearchAgent):
    """Agent responsible for grading the relevance and quality of information."""

    def __init__(self):
        """Initialize the Grading Agent."""
        instructions = """You are a Grading Agent responsible for evaluating the relevance and quality of gathered information.

Your responsibilities:
1. Grade each piece of information on three dimensions:
   - Relevance (0-10): How closely it relates to the research topic
   - Quality (0-10): Credibility, depth, and accuracy of the source
   - Novelty (0-10): Whether it provides new insights
2. Provide detailed importance statements explaining your ratings
3. Identify key insights from each source
4. Recommend tags for knowledge base storage
5. Determine if information should be saved or flagged for review

Grading criteria:
- Relevance: Direct relationship to topic (10) vs tangential mention (0)
- Quality: Peer-reviewed/authoritative (10) vs unreliable/shallow (0)
- Novelty: Groundbreaking insights (10) vs common knowledge (0)

For each piece of information, output a JSON object with:
- relevance_score: float (0-10)
- quality_score: float (0-10)
- novelty_score: float (0-10)
- importance_reason: string explaining the ratings
- key_insights: array of key takeaways
- recommended_tags: array of relevant tags
- overall_score: float (average of the three scores)
"""

        super().__init__(
            name="Grading Agent",
            instructions=instructions,
        )

    async def process(
        self,
        gathered_info: list[GatheredInformation],
        query: ResearchQuery,
    ) -> list[GradedInformation]:
        """Grade gathered information for relevance and quality.

        Args:
            gathered_info: List of gathered information
            query: Original research query

        Returns:
            List of graded information
        """
        logger.info(f"Grading {len(gathered_info)} pieces of information")

        graded_results = []

        for info in gathered_info:
            # Create prompt for grading this specific piece
            prompt = f"""Grade the following information for the research topic "{query.query}":

Title: {info.title}
Source Type: {info.source_type.value}
Content: {info.content}

Please evaluate this information and provide detailed grading."""

            messages = [self._create_message(prompt)]

            try:
                response = await self._run_agent(messages)

                # Parse JSON safely - handle extra content after JSON
                def safe_json_parse(content):
                    """Safely parse JSON from content that might have extra text."""
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError as e:
                        # Try to extract JSON from the beginning of the content
                        lines = content.strip().split("\n")
                        for i in range(len(lines), 0, -1):
                            try:
                                partial_content = "\n".join(lines[:i])
                                return json.loads(partial_content)
                            except json.JSONDecodeError:
                                continue
                        # If all else fails, try to find JSON-like content
                        import re

                        json_match = re.search(r"\{.*?\}", content, re.DOTALL)
                        if json_match:
                            return json.loads(json_match.group())
                        raise e

                grade_data = safe_json_parse(response.content)

                # Create importance statement
                importance = ImportanceStatement(
                    topic=query.query,
                    relevance_score=grade_data.get("relevance_score", 5.0),
                    quality_score=grade_data.get("quality_score", 5.0),
                    novelty_score=grade_data.get("novelty_score", 5.0),
                    importance_reason=grade_data.get("importance_reason", ""),
                    key_insights=grade_data.get("key_insights", []),
                    recommended_tags=grade_data.get("recommended_tags", []),
                )

                # Calculate overall score
                overall_score = (importance.relevance_score + importance.quality_score + importance.novelty_score) / 3.0

                # Determine if should save or review
                should_save = overall_score >= query.save_threshold
                should_review = overall_score >= query.review_threshold and overall_score < query.save_threshold

                graded = GradedInformation(
                    information=info,
                    importance=importance,
                    overall_score=overall_score,
                    should_save=should_save,
                    should_review=should_review,
                )

                graded_results.append(graded)
                logger.debug(f"Graded '{info.title}' - Score: {overall_score:.1f}, Save: {should_save}, Review: {should_review}")

            except Exception as e:
                logger.error(f"Failed to grade information: {e}")
                # Create default grading
                graded = self._create_default_grading(info, query)
                graded_results.append(graded)

        return graded_results

    def _create_default_grading(
        self,
        info: GatheredInformation,
        query: ResearchQuery,
    ) -> GradedInformation:
        """Create default grading when agent fails.

        Args:
            info: Gathered information
            query: Research query

        Returns:
            Graded information with default scores
        """
        importance = ImportanceStatement(
            topic=query.query,
            relevance_score=5.0,
            quality_score=5.0,
            novelty_score=5.0,
            importance_reason="Default grading due to processing error",
            key_insights=["Information requires manual review"],
            recommended_tags=[query.query.lower()],
        )

        return GradedInformation(
            information=info,
            importance=importance,
            overall_score=5.0,
            should_save=False,
            should_review=True,
        )
