"""
Research agent script for collecting and analyzing information from various sources.
"""

import argparse
import asyncio
import sys
from datetime import datetime
from pathlib import Path
from textwrap import dedent

from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.team.team import Team
from agno.tools.arxiv import ArxivTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.hackernews import HackerNewsTools
from agno.tools.newspaper4k import Newspaper4kTools

arxiv_download_dir = Path(__file__).parent.joinpath("tmp", "arxiv_pdfs__{session_id}")
arxiv_download_dir.mkdir(parents=True, exist_ok=True)

# Create reports directory
reports_dir = Path(__file__).parent.joinpath("reports")
reports_dir.mkdir(exist_ok=True)

reddit_researcher = Agent(
    name="Reddit Researcher",
    role="Research a topic on Reddit",
    model=Claude(),
    tools=[DuckDuckGoTools()],
    add_name_to_instructions=True,
    instructions=dedent(
        """
    You are a Reddit researcher.
    You will be given a topic to research on Reddit.
    You will need to find the 8 most relevant posts on Reddit.
    """
    ),
)

hackernews_researcher = Agent(
    name="HackerNews Researcher",
    model=Claude(),
    role="Research a topic on HackerNews.",
    tools=[HackerNewsTools()],
    add_name_to_instructions=True,
    instructions=dedent(
        """
    You are a HackerNews researcher.
    You will be given a topic to research on HackerNews.
    You will need to find the 8 most relevant posts on HackerNews.
    """
    ),
)

academic_paper_researcher = Agent(
    name="Academic Paper Researcher",
    model=Claude(),
    role="Research academic papers and scholarly content",
    tools=[GoogleSearchTools(), ArxivTools(download_dir=arxiv_download_dir)],
    add_name_to_instructions=True,
    instructions=dedent(
        """
    You are a academic paper researcher.
    You will be given a topic to research in academic literature.
    You will need to find relevant scholarly articles, papers, and academic discussions.
    Focus on peer-reviewed content and citations from reputable sources.
    Provide brief summaries of key findings and methodologies.
    """
    ),
)

twitter_researcher = Agent(
    name="Twitter Researcher",
    model=Claude(),
    role="Research trending discussions and real-time updates",
    tools=[DuckDuckGoTools()],
    add_name_to_instructions=True,
    instructions=dedent(
        """
    You are a Twitter/X researcher.
    You will be given a topic to research on Twitter/X.
    You will need to find trending discussions, influential voices, and real-time updates.
    Focus on verified accounts and credible sources when possible.
    Track relevant hashtags and ongoing conversations.
    """
    ),
)

duckduckgo_researcher = Agent(
    name="DuckDuckGo Web Researcher",
    model=Claude(),
    role="Comprehensive web research using DuckDuckGo search",
    tools=[DuckDuckGoTools()],
    add_name_to_instructions=True,
    instructions=dedent(
        """
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
    """
    ),
)

newspaper_researcher = Agent(
    name="Newspaper & News Researcher",
    model=Claude(),
    role="Research current news articles and newspaper coverage",
    tools=[Newspaper4kTools()],
    add_name_to_instructions=True,
    instructions=dedent(
        """
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
    """
    ),
)


agent_team = Team(
    name="Discussion Team",
    mode="collaborate",
    model=Claude(),
    members=[
        reddit_researcher,
        hackernews_researcher,
        academic_paper_researcher,
        twitter_researcher,
        duckduckgo_researcher,
        newspaper_researcher,
    ],
    instructions=[
        dedent(
            """
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
        """
        )
    ],
    success_criteria="The team has reached a consensus.",
    enable_agentic_context=True,
    show_tool_calls=True,
    markdown=True,
    show_members_responses=True,
)


async def run_research_and_save_report(research_topic: str):
    """Run the research team and save the final report to a markdown file."""

    # Run the team discussion and collect the final response
    print("🔍 Starting research discussion...")

    # Collect all response content
    full_response = ""
    final_response = None

    response_stream = await agent_team.arun(
        message=f"Start the discussion on the topic: '{research_topic}'",
        stream=True,
        stream_intermediate_steps=True,
    )

    async for response in response_stream:
        if hasattr(response, "content") and response.content:
            full_response += response.content
        final_response = response

    # Use the final response content if available, otherwise use collected content
    if final_response and hasattr(final_response, "content") and final_response.content:
        report_text = final_response.content
    else:
        report_text = full_response

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = research_topic.replace("?", "").replace(" ", "_").replace("'", "")[:50]
    filename = f"research_report_{safe_topic}_{timestamp}.md"
    report_path = reports_dir / filename

    # Save the report to markdown file
    print(f"\n💾 Saving report to: {report_path}")

    report_content = f"""# Research Report: {research_topic}

Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

{report_text}

---

*This report was automatically generated by the moargents research team.*
"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"✅ Report successfully saved to: {report_path}")
    return final_response


def main():
    """Main function with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Multi-agent research team for comprehensive topic analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python researcher.py "How did Robinson Crusoe manage to bake bread?"
  python researcher.py "What is the future of artificial intelligence?"
  python researcher.py "How does photosynthesis work?"
        """,
    )

    parser.add_argument("topic", help="The research topic to investigate")

    parser.add_argument(
        "--output-dir",
        default="reports",
        help="Directory to save the research report (default: reports)",
    )

    args = parser.parse_args()

    # Validate topic
    if not args.topic.strip():
        print("❌ Error: Research topic cannot be empty")
        sys.exit(1)

    # Update reports directory if specified
    global reports_dir
    reports_dir = Path(__file__).parent.joinpath(args.output_dir)
    reports_dir.mkdir(exist_ok=True)

    print(f"🎯 Research Topic: {args.topic}")
    print(f"📁 Output Directory: {reports_dir}")
    print()

    # Run the research
    try:
        asyncio.run(run_research_and_save_report(args.topic))
    except KeyboardInterrupt:
        print("\n⚠️  Research interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during research: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
