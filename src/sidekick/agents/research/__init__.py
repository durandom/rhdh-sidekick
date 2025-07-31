"""Research agents for the sidekick research command."""

from .analyst import AnalystAgent
from .base import BaseResearchAgent
from .coordinator import ResearchCoordinatorAgent, ResearchTeam
from .gatherer import (AcademicPaperResearcherAgent, DuckDuckGoResearcherAgent, HackerNewsResearcherAgent, InformationGathererAgent,
                       NewspaperResearcherAgent, RedditResearcherAgent, TwitterResearcherAgent)
from .generator import ReportGeneratorAgent
from .grader import GradingAgent
from .models import (AnalysisResult, GatheredInformation, GradedInformation, ImportanceStatement, ResearchDepth, ResearchPlan,
                     ResearchQuery, ResearchReport, ResearchResult, ReviewResult, SourceType)
from .reviewer import QualityReviewerAgent

__all__ = [
    # Base classes
    "BaseResearchAgent",
    # Core agents
    "ResearchCoordinatorAgent",
    "InformationGathererAgent",
    "GradingAgent",
    "AnalystAgent",
    "QualityReviewerAgent",
    "ReportGeneratorAgent",
    # Specialized gatherer agents
    "RedditResearcherAgent",
    "HackerNewsResearcherAgent",
    "AcademicPaperResearcherAgent",
    "TwitterResearcherAgent",
    "DuckDuckGoResearcherAgent",
    "NewspaperResearcherAgent",
    # Team
    "ResearchTeam",
    # Models
    "ImportanceStatement",
    "ResearchQuery",
    "ResearchResult",
    "ResearchPlan",
    "GatheredInformation",
    "GradedInformation",
    "AnalysisResult",
    "ReviewResult",
    "ResearchReport",
    "ResearchDepth",
    "SourceType",
]
