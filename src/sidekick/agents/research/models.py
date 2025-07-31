"""Pydantic models for research agent communication."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ResearchDepth(str, Enum):
    """Research depth levels."""

    QUICK = "quick"
    STANDARD = "standard"
    DEEP = "deep"


class SourceType(str, Enum):
    """Types of information sources."""

    WEB = "web"
    LOCAL_KNOWLEDGE = "local_knowledge"
    ARXIV = "arxiv"
    REDDIT = "reddit"
    HACKERNEWS = "hackernews"
    TWITTER = "twitter"
    NEWS = "news"


class ResearchQuery(BaseModel):
    """Input model for research requests."""

    query: str = Field(..., description="The research topic or question")
    depth: ResearchDepth = Field(ResearchDepth.STANDARD, description="Research depth level")
    max_rounds: int = Field(3, description="Maximum research iterations", ge=1, le=10)
    save_threshold: float = Field(8.0, description="Minimum score to save to knowledge base", ge=0, le=10)
    review_threshold: float = Field(6.0, description="Minimum score for user review", ge=0, le=10)
    no_web: bool = Field(False, description="Disable web search")
    no_local: bool = Field(False, description="Disable local knowledge search")
    no_arxiv: bool = Field(False, description="Disable arXiv search")


class ResearchPlan(BaseModel):
    """Research plan created by the coordinator."""

    query: str
    objectives: list[str] = Field(..., description="Research objectives")
    search_strategies: list[str] = Field(..., description="Search strategies to employ")
    focus_areas: list[str] = Field(..., description="Key areas to investigate")
    excluded_sources: list[SourceType] = Field(default_factory=list)
    iteration: int = Field(1, description="Current research iteration")


class GatheredInformation(BaseModel):
    """Information gathered from a source."""

    source_type: SourceType
    source_url: str | None = None
    title: str
    content: str
    snippet: str = Field(..., description="Brief excerpt or summary")
    metadata: dict[str, str] = Field(default_factory=dict)
    gathered_at: datetime = Field(default_factory=datetime.now)


class ImportanceStatement(BaseModel):
    """Importance evaluation for a piece of information."""

    topic: str = Field(..., description="Research topic")
    relevance_score: float = Field(..., ge=0, le=10, description="How closely related to the topic")
    quality_score: float = Field(..., ge=0, le=10, description="Source credibility and depth")
    novelty_score: float = Field(..., ge=0, le=10, description="New insights provided")
    importance_reason: str = Field(..., description="Why this information is important")
    key_insights: list[str] = Field(..., description="Main insights from this source")
    recommended_tags: list[str] = Field(..., description="Tags for knowledge base")


class GradedInformation(BaseModel):
    """Information with grading and importance evaluation."""

    information: GatheredInformation
    importance: ImportanceStatement
    overall_score: float = Field(..., ge=0, le=10, description="Combined importance score")
    should_save: bool = Field(..., description="Whether to save to knowledge base")
    should_review: bool = Field(..., description="Whether to flag for user review")


class AnalysisResult(BaseModel):
    """Results from the analyst agent."""

    key_findings: list[str] = Field(..., description="Main findings from the research")
    patterns: list[str] = Field(..., description="Identified patterns or trends")
    insights: list[str] = Field(..., description="Key insights and conclusions")
    contradictions: list[str] = Field(default_factory=list, description="Conflicting information found")
    gaps: list[str] = Field(default_factory=list, description="Identified knowledge gaps")
    summary: str = Field(..., description="Executive summary of findings")


class ReviewResult(BaseModel):
    """Results from the quality reviewer."""

    is_complete: bool = Field(..., description="Whether research is sufficiently complete")
    quality_score: float = Field(..., ge=0, le=10, description="Overall quality rating")
    completeness_score: float = Field(..., ge=0, le=10, description="Coverage completeness")
    accuracy_concerns: list[str] = Field(default_factory=list)
    missing_areas: list[str] = Field(default_factory=list)
    improvement_suggestions: list[str] = Field(default_factory=list)
    recommended_action: str = Field(..., description="Continue, refine, or complete")


class ResearchReport(BaseModel):
    """Final research report."""

    title: str
    query: str
    executive_summary: str
    sections: list[dict[str, str]] = Field(..., description="Report sections with titles and content")
    sources: list[dict[str, str]] = Field(..., description="Citations and references")
    metadata: dict[str, str] = Field(default_factory=dict)
    generated_at: datetime = Field(default_factory=datetime.now)
    format: str = Field("markdown", description="Output format")


class ResearchResult(BaseModel):
    """Complete research results."""

    query: ResearchQuery
    plan: ResearchPlan
    findings: list[GradedInformation]
    analysis: AnalysisResult
    review: ReviewResult
    report: ResearchReport
    saved_knowledge: list[GradedInformation] = Field(default_factory=list)
    iterations_completed: int = Field(1)
