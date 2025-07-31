"""Information Gatherer agent implementation."""

from datetime import datetime
from textwrap import dedent

from agno.tools.arxiv import ArxivTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.hackernews import HackerNewsTools
from agno.tools.newspaper4k import Newspaper4kTools
from loguru import logger

from .base import BaseResearchAgent
from .models import GatheredInformation, ResearchPlan, SourceType


class InformationGathererAgent(BaseResearchAgent):
    """Agent responsible for gathering information from various sources."""

    def __init__(self):
        """Initialize the Information Gatherer agent."""
        instructions = """You are an Information Gatherer responsible for collecting relevant information from various sources.

Your responsibilities:
1. Search for information based on the research plan
2. Extract relevant content from sources
3. Create concise snippets that capture key information
4. Collect metadata about sources

For now, simulate searching by creating realistic mock data based on the research topic.
In the future, you will have access to real web search, arXiv, and local knowledge tools.

When gathering information:
- Focus on the objectives and focus areas from the research plan
- Provide diverse perspectives from different types of sources
- Include both overview information and specific details
- Ensure information is relevant and high-quality

For each piece of information, create a JSON object with:
- source_type: "web", "local_knowledge", or "arxiv"
- source_url: URL or identifier (can be simulated)
- title: Title of the source
- content: Full relevant content (1-3 paragraphs)
- snippet: Brief excerpt (1-2 sentences)
- metadata: Additional metadata (author, date, etc.)
"""

        super().__init__(
            name="Information Gatherer",
            instructions=instructions,
            # TODO: Add real tools when implementing:
            # tools=[WebSearchTool(), LocalKnowledgeTool(), ArxivTool()]
        )

    async def process(self, input_data: ResearchPlan) -> list[GatheredInformation]:
        """Gather information based on the research plan.

        Args:
            input_data: Research plan

        Returns:
            List of gathered information
        """
        logger.info(f"Gathering information for: {input_data.query}")

        # Create prompt for the agent
        prompt = f"""Gather information for the following research plan:

Query: {input_data.query}
Objectives: {", ".join(input_data.objectives)}
Focus Areas: {", ".join(input_data.focus_areas)}
Search Strategies: {", ".join(input_data.search_strategies)}
Excluded Sources: {", ".join([s.value for s in input_data.excluded_sources])}

Please gather 5-8 pieces of relevant information from various sources.
Return the information as a JSON array."""

        messages = [self._create_message(prompt)]

        try:
            response = await self._run_agent(messages)

            # Parse the JSON response
            import json

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

            info_list = safe_json_parse(response.content)

            # Handle nested structure if AI returns wrapped data
            if isinstance(info_list, dict) and "gathered_information" in info_list:
                info_list = info_list["gathered_information"]

            # Ensure info_list is a list
            if not isinstance(info_list, list):
                logger.warning(f"Expected list but got {type(info_list)}: {info_list}")
                info_list = []

            gathered = []
            for info_data in info_list:
                # Ensure info_data is a dictionary
                if not isinstance(info_data, dict):
                    logger.warning(f"Expected dict but got {type(info_data)}: {info_data}")
                    continue
                # Skip excluded source types
                source_type = SourceType(info_data.get("source_type", "web"))
                if source_type in input_data.excluded_sources:
                    continue

                # Clean metadata to ensure all values are strings
                raw_metadata = info_data.get("metadata", {})
                clean_metadata = {}
                for key, value in raw_metadata.items():
                    if isinstance(value, list):
                        # Convert lists to comma-separated strings
                        clean_metadata[key] = ", ".join(str(item) for item in value)
                    else:
                        clean_metadata[key] = str(value)

                gathered_info = GatheredInformation(
                    source_type=source_type,
                    source_url=info_data.get("source_url"),
                    title=info_data.get("title", "Untitled"),
                    content=info_data.get("content", ""),
                    snippet=info_data.get("snippet", ""),
                    metadata=clean_metadata,
                    gathered_at=datetime.now(),
                )
                gathered.append(gathered_info)

            logger.debug(f"Gathered {len(gathered)} pieces of information")
            return gathered

        except Exception as e:
            logger.error(f"Failed to gather information: {e}")
            # Return mock data as fallback
            return self._create_mock_data(input_data)

    def _create_mock_data(self, plan: ResearchPlan) -> list[GatheredInformation]:
        """Create mock gathered information for testing.

        Args:
            plan: Research plan

        Returns:
            List of mock gathered information
        """
        mock_data = []

        if SourceType.WEB not in plan.excluded_sources:
            mock_data.append(
                GatheredInformation(
                    source_type=SourceType.WEB,
                    source_url="https://example.com/article1",
                    title=f"Understanding {plan.query}: A Comprehensive Guide",
                    content=f"This article provides a detailed overview of {plan.query}. "
                    f"It covers the fundamental concepts and recent developments in the field. "
                    f"The research shows promising results and applications.",
                    snippet=f"A comprehensive guide to understanding {plan.query} and its applications.",
                    metadata={"author": "Dr. Example", "date": "2024-01-15"},
                )
            )

        if SourceType.ARXIV not in plan.excluded_sources:
            mock_data.append(
                GatheredInformation(
                    source_type=SourceType.ARXIV,
                    source_url="https://arxiv.org/abs/2024.01234",
                    title=f"Recent Advances in {plan.query}: A Survey",
                    content=f"This paper surveys recent advances in {plan.query}. "
                    f"We analyze current state-of-the-art approaches and identify key challenges. "
                    f"Our findings suggest several promising directions for future research.",
                    snippet=f"A survey of recent advances and future directions in {plan.query}.",
                    metadata={"authors": "Smith et al.", "date": "2024-01-20", "arxiv_id": "2024.01234"},
                )
            )

        return mock_data


class RedditResearcherAgent(BaseResearchAgent):
    """Agent specializing in Reddit research."""

    def __init__(self, model_id: str = "claude-3-5-sonnet-20241022"):
        """Initialize Reddit researcher agent."""
        instructions = dedent("""
        You are a Reddit researcher.
        You will be given a topic to research on Reddit.
        You will need to find the 8 most relevant posts on Reddit.
        """)

        super().__init__(
            name="Reddit Researcher",
            instructions=instructions,
            model_id=model_id,
            tools=[DuckDuckGoTools()],
        )

    async def process(self, input_data):
        """Process research request for Reddit.

        This is handled by the Team framework, so we don't need
        to implement this method for team-based agents.
        """
        pass


class HackerNewsResearcherAgent(BaseResearchAgent):
    """Agent specializing in HackerNews research."""

    def __init__(self, model_id: str = "claude-3-5-sonnet-20241022"):
        """Initialize HackerNews researcher agent."""
        instructions = dedent("""
        You are a HackerNews researcher.
        You will be given a topic to research on HackerNews.
        You will need to find the 8 most relevant posts on HackerNews.
        """)

        super().__init__(
            name="HackerNews Researcher",
            instructions=instructions,
            model_id=model_id,
            tools=[HackerNewsTools()],
        )

    async def process(self, input_data):
        """Process research request for HackerNews.

        This is handled by the Team framework, so we don't need
        to implement this method for team-based agents.
        """
        pass


class AcademicPaperResearcherAgent(BaseResearchAgent):
    """Agent specializing in academic paper research."""

    def __init__(self, arxiv_download_dir: str | None = None, model_id: str = "claude-3-5-sonnet-20241022"):
        """Initialize academic paper researcher agent."""
        instructions = dedent("""
        You are a academic paper researcher.
        You will be given a topic to research in academic literature.
        You will need to find relevant scholarly articles, papers, and academic discussions.
        Focus on peer-reviewed content and citations from reputable sources.
        Provide brief summaries of key findings and methodologies.
        """)

        # Create ArxivTools with download directory if provided
        tools = [GoogleSearchTools()]
        if arxiv_download_dir:
            tools.append(ArxivTools(download_dir=arxiv_download_dir))
        else:
            tools.append(ArxivTools())

        super().__init__(
            name="Academic Paper Researcher",
            instructions=instructions,
            model_id=model_id,
            tools=tools,
        )

    async def process(self, input_data):
        """Process research request for academic papers.

        This is handled by the Team framework, so we don't need
        to implement this method for team-based agents.
        """
        pass


class TwitterResearcherAgent(BaseResearchAgent):
    """Agent specializing in Twitter/X research."""

    def __init__(self, model_id: str = "claude-3-5-sonnet-20241022"):
        """Initialize Twitter researcher agent."""
        instructions = dedent("""
        You are a Twitter/X researcher.
        You will be given a topic to research on Twitter/X.
        You will need to find trending discussions, influential voices, and real-time updates.
        Focus on verified accounts and credible sources when possible.
        Track relevant hashtags and ongoing conversations.
        """)

        super().__init__(
            name="Twitter Researcher",
            instructions=instructions,
            model_id=model_id,
            tools=[DuckDuckGoTools()],
        )

    async def process(self, input_data):
        """Process research request for Twitter.

        This is handled by the Team framework, so we don't need
        to implement this method for team-based agents.
        """
        pass


class DuckDuckGoResearcherAgent(BaseResearchAgent):
    """Agent specializing in comprehensive web research."""

    def __init__(self, model_id: str = "claude-3-5-sonnet-20241022"):
        """Initialize DuckDuckGo web researcher agent."""
        instructions = dedent("""
        You are a comprehensive web researcher specializing in DuckDuckGo search.

        Your research methodology:
        1. Perform multiple strategic searches using different keyword combinations
        2. Analyze and rank results by relevance, credibility, and recency
        3. Select the TOP 10 MOST ACCURATE and authoritative sources
        4. Thoroughly summarize each source's key information
        5. Always include the complete source URL for each result

        For each research topic, you must:
        - Use varied search terms to capture different perspectives
        - Prioritize authoritative sources (government sites, academic institutions, reputable news outlets, established organizations)
        - Evaluate source credibility and publication dates
        - Extract key facts, statistics, and insights from each source
        - Provide comprehensive summaries that capture the essence of each source
        - Organize findings in order of relevance and reliability

        Your output should be written in a flowing, prose-like academic style using complete sentences and paragraphs rather than bullet points. Structure your response as follows:

        ## Web Research Summary

        ### Search Strategy
        Begin with a comprehensive paragraph explaining the search methodology employed, detailing the specific search terms utilized and the strategic approach taken to ensure comprehensive coverage of the topic. Describe how different keyword combinations were selected to capture various perspectives and angles on the subject matter.

        ### Top 10 Sources Analysis

        Present each source as a detailed paragraph that seamlessly integrates the source information, credibility assessment, and comprehensive summary. Each source should be introduced with its title and publication details, followed by the complete URL, and then a thorough analysis of its content, reliability, and contribution to understanding the topic. Discuss the key findings, methodologies, and insights presented in each source while evaluating its credibility and relevance to the research question.

        **Source 1:** [Provide comprehensive paragraph analysis including URL, summary, and credibility assessment]

        **Source 2:** [Continue with detailed prose-style analysis]

        [Continue for all 10 sources in paragraph form]

        ### Synthesis and Analysis
        Conclude with several comprehensive paragraphs that weave together the main themes and consensus points discovered across all sources. Discuss how different sources complement or contradict each other, analyze the most reliable and well-supported facts that emerged from the research, and identify areas where further investigation might be beneficial. Present this synthesis in a flowing narrative style that demonstrates the interconnections between various findings and perspectives.

        Focus on accuracy, comprehensiveness, and proper source attribution with complete URLs. Write your entire response in simple German language that a 10-year-old would understand, explaining technical terms and concepts in child-friendly ways while maintaining thoroughness.
        """)

        super().__init__(
            name="DuckDuckGo Web Researcher",
            instructions=instructions,
            model_id=model_id,
            tools=[DuckDuckGoTools()],
        )

    async def process(self, input_data):
        """Process research request for web search.

        This is handled by the Team framework, so we don't need
        to implement this method for team-based agents.
        """
        pass


class NewspaperResearcherAgent(BaseResearchAgent):
    """Agent specializing in news and newspaper research."""

    def __init__(self, model_id: str = "claude-3-5-sonnet-20241022"):
        """Initialize newspaper researcher agent."""
        instructions = dedent("""
        You are a comprehensive news and newspaper researcher specializing in current events and journalistic coverage.

        Your research methodology:
        1. Search for relevant news articles from reputable news sources
        2. Extract and analyze article content, headlines, and publication details
        3. Identify key news outlets covering the topic and their perspectives
        4. Summarize breaking news, recent developments, and ongoing coverage
        5. Always include complete article URLs and publication information

        For each research topic, you must:
        - Focus on recent news coverage and current events related to the topic
        - Prioritize established news organizations and reputable journalists
        - Extract key facts, quotes, and developments from news articles
        - Identify different editorial perspectives and news angles
        - Track how the story has evolved over time in the media
        - Note geographic differences in coverage when relevant

        Your output should be written in a flowing, prose-like academic style using complete sentences and paragraphs rather than bullet points. Structure your response as follows:

        ## News Coverage Analysis

        ### Research Approach
        Begin with a comprehensive paragraph explaining your news research methodology, detailing how you searched for relevant coverage across different news sources and the criteria used to select the most significant articles. Describe the time frame of coverage examined and any notable patterns in how different news outlets approached the topic.

        ### Major News Sources and Coverage

        Present each significant news source and its coverage as detailed paragraphs that integrate publication information, article content, and journalistic perspective. Each source should be introduced with the publication name and article details, followed by the complete URL, and then a thorough analysis of the content, editorial stance, and contribution to public understanding of the topic. Discuss key quotes, facts, and insights while evaluating the credibility and newsworthiness of each source.

        **Source 1:** [Provide comprehensive paragraph analysis including publication, URL, content summary, and journalistic perspective]

        **Source 2:** [Continue with detailed prose-style analysis of news coverage]

        [Continue for all major news sources covering the topic]

        ### Timeline and Coverage Evolution
        Analyze how news coverage of the topic has evolved over time, identifying key moments when coverage intensified, major breaking news developments, and shifts in media focus or public interest. Discuss how different news cycles and events influenced the way the story was covered.

        ### Editorial Perspectives and Media Analysis
        Conclude with comprehensive paragraphs that examine different editorial perspectives encountered across news sources, analyzing how various publications framed the topic and what this reveals about media coverage patterns. Identify any notable biases, gaps in coverage, or areas where the journalistic community showed consensus or disagreement.

        Focus on accuracy, timeliness, and proper source attribution with complete URLs. Write your entire response in simple German language that a 10-year-old would understand, explaining news terms and current events in child-friendly ways while maintaining thoroughness and journalistic integrity.
        """)

        super().__init__(
            name="Newspaper & News Researcher",
            instructions=instructions,
            model_id=model_id,
            tools=[Newspaper4kTools()],
        )

    async def process(self, input_data):
        """Process research request for news.

        This is handled by the Team framework, so we don't need
        to implement this method for team-based agents.
        """
        pass
