"""Research Coordinator agent implementation."""

import json
from pathlib import Path
from textwrap import dedent

from agno.models.anthropic import Claude
from agno.team.team import Team
from loguru import logger

from .base import BaseResearchAgent
from .models import ResearchPlan, ResearchQuery, SourceType


class ResearchCoordinatorAgent(BaseResearchAgent):
    """Agent responsible for planning and coordinating research."""

    def __init__(self):
        """Initialize the Research Coordinator agent."""
        instructions = """You are a Research Coordinator responsible for planning comprehensive research strategies.

Your responsibilities:
1. Analyze the research query to understand the core topic and objectives
2. Create a structured research plan with clear objectives and strategies
3. Identify key areas to investigate and appropriate search strategies
4. Determine which sources to exclude based on user preferences
5. Adjust research plans between iterations based on feedback

When creating a research plan:
- Break down complex queries into specific, actionable objectives
- Suggest diverse search strategies to gather comprehensive information
- Identify 3-5 key focus areas that will provide the most value
- Consider the research depth (quick/standard/deep) when planning

Output your plan as a JSON object with these fields:
- objectives: Array of strings (e.g., ["objective1", "objective2"])
- search_strategies: Array of strings (e.g., ["strategy1", "strategy2"])
- focus_areas: Array of strings (e.g., ["area1", "area2"])

Example format:
{
  "objectives": ["Find the best pizza dough recipe", "Understand fermentation techniques"],
  "search_strategies": ["Search for authentic Italian recipes", "Look for scientific articles on dough"],
  "focus_areas": ["Ingredient ratios", "Fermentation time", "Kneading techniques"]
}
"""

        super().__init__(
            name="Research Coordinator",
            instructions=instructions,
        )

    async def process(self, input_data: ResearchQuery) -> ResearchPlan:
        """Create a research plan from the query.

        Args:
            input_data: Research query

        Returns:
            Research plan
        """
        logger.info(f"Creating research plan for: {input_data.query}")

        # Determine excluded sources
        excluded_sources = []
        if input_data.no_web:
            excluded_sources.append(SourceType.WEB)
        if input_data.no_local:
            excluded_sources.append(SourceType.LOCAL_KNOWLEDGE)
        if input_data.no_arxiv:
            excluded_sources.append(SourceType.ARXIV)

        # Create prompt for the agent
        prompt = f"""Create a research plan for the following query:

Query: {input_data.query}
Research Depth: {input_data.depth}
Excluded Sources: {", ".join([s.value for s in excluded_sources]) if excluded_sources else "None"}

Please create a comprehensive research plan that will guide the research process."""

        messages = [self._create_message(prompt)]

        try:
            response = await self._run_agent(messages)

            # Parse the JSON response - handle extra content after JSON
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

            plan_data = safe_json_parse(response.content)

            # Clean up data - ensure all fields are lists of strings
            def clean_string_list(data, field_name):
                items = data.get(field_name, [])
                if not isinstance(items, list):
                    return []
                cleaned = []
                for item in items:
                    if isinstance(item, str):
                        cleaned.append(item)
                    elif isinstance(item, dict) and "area" in item:
                        cleaned.append(item["area"])
                    elif isinstance(item, dict):
                        # Try to extract a meaningful string value
                        for key in ["title", "name", "value", "description"]:
                            if key in item:
                                cleaned.append(str(item[key]))
                                break
                        else:
                            cleaned.append(str(item))
                    else:
                        cleaned.append(str(item))
                return cleaned

            plan = ResearchPlan(
                query=input_data.query,
                objectives=clean_string_list(plan_data, "objectives"),
                search_strategies=clean_string_list(plan_data, "search_strategies"),
                focus_areas=clean_string_list(plan_data, "focus_areas"),
                excluded_sources=excluded_sources,
                iteration=1,
            )

            logger.debug(f"Created research plan with {len(plan.objectives)} objectives")
            return plan

        except Exception as e:
            logger.error(f"Failed to create research plan: {e}")
            # Return a basic plan as fallback
            return ResearchPlan(
                query=input_data.query,
                objectives=[f"Research {input_data.query}"],
                search_strategies=["General web search", "Academic search"],
                focus_areas=["Main topic overview"],
                excluded_sources=excluded_sources,
                iteration=1,
            )

    async def update_plan(self, current_plan: ResearchPlan, feedback: dict) -> ResearchPlan:
        """Update the research plan based on feedback.

        Args:
            current_plan: Current research plan
            feedback: Feedback from review

        Returns:
            Updated research plan
        """
        logger.info(f"Updating research plan for iteration {current_plan.iteration + 1}")

        prompt = f"""Update the research plan based on the following feedback:

Current Plan:
- Query: {current_plan.query}
- Objectives: {json.dumps(current_plan.objectives)}
- Focus Areas: {json.dumps(current_plan.focus_areas)}

Feedback:
- Missing Areas: {json.dumps(feedback.get("missing_areas", []))}
- Improvement Suggestions: {json.dumps(feedback.get("improvement_suggestions", []))}

Please create an updated research plan that addresses the feedback."""

        messages = [self._create_message(prompt)]

        try:
            response = await self._run_agent(messages)
            plan_data = json.loads(response.content)

            updated_plan = ResearchPlan(
                query=current_plan.query,
                objectives=plan_data.get("objectives", current_plan.objectives),
                search_strategies=plan_data.get("search_strategies", current_plan.search_strategies),
                focus_areas=plan_data.get("focus_areas", current_plan.focus_areas),
                excluded_sources=current_plan.excluded_sources,
                iteration=current_plan.iteration + 1,
            )

            return updated_plan

        except Exception as e:
            logger.error(f"Failed to update research plan: {e}")
            # Return current plan with incremented iteration
            current_plan.iteration += 1
            return current_plan


class ResearchTeam:
    """Team of research agents working collaboratively."""

    def __init__(
        self,
        arxiv_download_dir: Path | None = None,
        enable_all_agents: bool = True,
        model_id: str = "claude-3-5-sonnet-20241022",
    ):
        """Initialize the research team.

        Args:
            arxiv_download_dir: Directory for arxiv downloads
            enable_all_agents: Whether to enable all specialized agents
            model_id: Claude model ID to use
        """
        self.arxiv_download_dir = arxiv_download_dir
        self.enable_all_agents = enable_all_agents
        self.model_id = model_id

        # Import the specialized agents
        from .gatherer import (AcademicPaperResearcherAgent, DuckDuckGoResearcherAgent, HackerNewsResearcherAgent, NewspaperResearcherAgent,
                               RedditResearcherAgent, TwitterResearcherAgent)

        # Create team members based on configuration
        self.members = []

        if enable_all_agents:
            self.members = [
                RedditResearcherAgent(model_id=model_id).agent,
                HackerNewsResearcherAgent(model_id=model_id).agent,
                AcademicPaperResearcherAgent(
                    arxiv_download_dir=str(arxiv_download_dir) if arxiv_download_dir else None, model_id=model_id
                ).agent,
                TwitterResearcherAgent(model_id=model_id).agent,
                DuckDuckGoResearcherAgent(model_id=model_id).agent,
                NewspaperResearcherAgent(model_id=model_id).agent,
            ]
        else:
            # Minimal team with just web search
            self.members = [
                DuckDuckGoResearcherAgent(model_id=model_id).agent,
            ]

        # Create the team with comprehensive instructions
        self.team = Team(
            name="Research Team",
            mode="collaborate",
            model=Claude(id=model_id),
            members=self.members,
            instructions=[self._get_team_instructions()],
            success_criteria="The team has reached a consensus.",
            enable_agentic_context=True,
            show_tool_calls=True,
            markdown=True,
            show_members_responses=True,
        )

    def _get_team_instructions(self) -> str:
        """Get comprehensive team instructions."""
        return dedent("""
        You are a discussion master responsible for synthesizing team research into a comprehensive, detailed academic-style summary.

        Your role is to:
        1. Facilitate productive discussion between team members
        2. Identify when sufficient research has been gathered from multiple perspectives
        3. Synthesize findings into a thorough, well-documented academic paper format
        4. Ensure all claims are properly cited with complete source information

        When summarizing the team's research, create a VERBOSE and DETAILED report using the following IMRAD structure:

        ## Abstract
        Compose a comprehensive overview of the research question and methodology in 200-300 words, presenting the key findings from each research domain (Reddit, HackerNews, Academic, Social Media, Web Search, News Coverage) in flowing prose. Articulate the main conclusions and implications of the study while briefly mentioning the limitations encountered and potential directions for future research. Write this section as a cohesive narrative that introduces readers to the scope and significance of the investigation.

        ## Introduction (minimum 3-4 paragraphs)
        Begin with extensive background context and historical perspective on the topic, weaving together relevant information that establishes the foundation for your research. Present detailed motivation for the research with supporting evidence, explaining why this particular investigation was necessary and timely. Clearly articulate the specific research question or hypothesis along with related sub-questions, demonstrating the focused nature of your inquiry. Discuss the significance and relevance of the topic in the current context, connecting it to broader themes and contemporary issues. Conclude the introduction with a preview of the multi-source research approach, explaining how different perspectives will be integrated to provide a comprehensive understanding of the subject matter.

        ## Methods (detailed methodology section)
        Provide a comprehensive description of each research approach used by team members, explaining how different methodologies were coordinated to create a multi-faceted investigation. Detail the specific tools and platforms utilized, including Reddit search, HackerNews API, ArXiv database, Google Scholar, Twitter/X analysis, DuckDuckGo web search, and Newspaper4k news analysis, describing how each tool contributed unique insights to the overall research framework. Explain the search strategies, keywords, and filtering criteria employed across different platforms, demonstrating the systematic approach taken to ensure comprehensive coverage. Discuss the time periods covered and geographical scope where relevant, providing context for the temporal and spatial boundaries of the research. Elaborate on the data collection protocols and quality assessment methods used to maintain research integrity and reliability. Acknowledge the limitations and potential biases of each source, demonstrating awareness of methodological constraints and their impact on the findings.

        ## Results (extensively detailed findings)
        Organize your findings into separate subsections for each research source, presenting each with in-depth analysis written in flowing prose:

        ### Reddit Community Insights
        Present the Reddit findings in comprehensive paragraphs that integrate quantitative metrics (post counts, engagement levels) with qualitative themes and patterns identified within the community discussions. Highlight the most influential posts with full citations, incorporating representative quotes and examples with proper attribution. Trace the timeline of discussions and evolving perspectives within the Reddit community.

        ### HackerNews Technical Perspectives
        Analyze the HackerNews findings through detailed narrative that combines technical insights with community engagement patterns. Discuss the most significant discussions and their contributors, weaving together technical details with broader implications identified by the community.

        ### Academic Literature Review
        Synthesize the academic findings in scholarly prose that presents the peer-reviewed research, citation patterns, and methodological approaches discovered. Connect different studies and papers through narrative analysis that demonstrates the evolution of academic thought on the topic.

        ### Social Media Trends and Public Opinion
        Describe the social media findings through comprehensive analysis that captures trending discussions, influential voices, and public sentiment. Present the data as a flowing narrative that connects individual posts and conversations to broader social trends.

        ### Web Search Findings
        Integrate the web search results into a cohesive analysis that presents the most authoritative sources and their key contributions. Weave together insights from different web sources to create a comprehensive picture of online discourse and information availability.

        ### News Coverage Analysis
        Present the news media findings through comprehensive analysis that captures current events, journalistic perspectives, and evolving news narratives. Synthesize coverage from different news outlets to reveal how the topic is being framed in contemporary media discourse, including breaking developments, expert commentary, and public interest patterns.

        Following each subsection, provide cross-source comparison and convergent themes analysis in paragraph form, discussing how different sources complement each other. Address contradictions and divergent viewpoints through detailed narrative analysis that explores the reasons behind different perspectives and their implications for understanding the topic.

        ## Discussion (comprehensive analysis - minimum 4-5 paragraphs)
        Begin with an in-depth interpretation of findings supported by evidence from across all research sources, creating a cohesive narrative that synthesizes the diverse perspectives encountered. Provide detailed comparison across different sources and communities, explaining how various platforms and methodologies yielded complementary or contrasting insights. Analyze why different sources may have varying perspectives, considering the unique characteristics, user demographics, and cultural contexts of each platform or information source. Discuss methodological limitations and their impact on findings, demonstrating critical awareness of how research constraints may have influenced the results. Explore broader implications for theory, practice, and policy, connecting your findings to real-world applications and potential impacts. Establish connections to existing literature and identify knowledge gaps that your research has revealed or addressed. Conclude the discussion by examining unexpected findings and their significance, explaining how these discoveries contribute to a deeper understanding of the research topic.

        ## Conclusion (thorough summary and future directions)
        Provide a comprehensive summary of main findings from each source, weaving them together into a coherent narrative that demonstrates the interconnected nature of insights gained from different research domains. Present a direct, evidence-based answer to the original research question, supported by specific examples and data from your multi-source investigation. Discuss practical applications and recommendations that emerge from your findings, explaining how this research can be applied in real-world contexts. Offer detailed suggestions for future research with specific methodologies, identifying areas where additional investigation would be valuable and proposing concrete approaches for advancing knowledge in this field. Conclude with final thoughts on the topic's broader significance, placing your research within the larger context of ongoing scholarly and public discourse while highlighting its unique contributions to understanding the subject matter.

        ## References (complete bibliographic information)
        Use the following citation formats:

        **Reddit Posts:**
        [Username]. (Date). "Post Title." Reddit. r/subreddit. [Full URL]

        **HackerNews:**
        [Username]. (Date). "Story/Comment Title." Hacker News. [Full URL with comment ID if applicable]

        **Academic Papers:**
        Author, A. A. (Year). Title of paper. *Journal Name*, Volume(Issue), pages. DOI or [ArXiv URL]

        **Twitter/X Posts:**
        [@Handle]. (Date). "Tweet content..." Twitter/X. [Full URL]

        **Web Articles:**
        Author, A. A. (Date). "Article Title." *Website Name*. [Full URL]

        **News Articles:**
        Author, A. A. (Date). "Headline." *Newspaper/News Source*. [Full URL]

        CITATION REQUIREMENTS:
        - Include complete URLs for all online sources
        - Provide access dates for time-sensitive content
        - Include engagement metrics where available (upvotes, retweets, citations)
        - Group references by source type for better organization
        - Ensure all in-text citations have corresponding reference entries
        - Include archive.org links for potentially ephemeral content

        WRITING STYLE REQUIREMENTS:
        Write the entire report in English language.

        Your Unique Voice:
        As a Cross-Pollinator engineer, emphasize:

        - **Connections**: "This reminds me of..." / "Similar to how..."
        - **People**: "I learned this from..." / "The team discovered..."
        - **Clarity**: Direct language, concrete examples, no fluff
        - **Teaching**: "Here's how to think about this..."
        - **Experience**: "In my 25 years, this pattern keeps appearing..."

        When technical terms must be used, explain them immediately in simple language that a cross-reading manager would understand. maintain the comprehensive academic structure. Use everyday English expressions and familiar concepts to make complex research accessible to all readers. Include specific examples and evidence for all claims, but present them in a way that would engage and inform a curious 25-year-old. Provide context for technical terms and platform-specific jargon using simple english explanations and analogieso. Aim for 5000-7500 words total length for comprehensive coverage.

        Stop the discussion when you have gathered sufficient diverse perspectives and detailed information to create a comprehensive, well-cited academic report following this enhanced format.
        """)

    async def run_research(self, topic: str, stream: bool = True):
        """Run the research team on a topic.

        Args:
            topic: Research topic
            stream: Whether to stream responses

        Returns:
            Research team response
        """
        logger.info(f"Starting research team for topic: {topic}")

        response = await self.team.arun(
            message=f"Start the discussion on the topic: '{topic}'",
            stream=stream,
            stream_intermediate_steps=True,
        )

        return response
