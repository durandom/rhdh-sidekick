# Research Command Implementation Plan

## Overview

This document outlines the plan for implementing a new `research` command in the sidekick CLI that utilizes an Agno workflow v2 with an agent team to perform comprehensive research tasks.

## Requirements

### Functional Requirements

1. **Command Interface**
   - Command: `sidekick research "query" [OPTIONS]`
   - Support various research depths (quick/standard/deep)
   - Multiple output formats (markdown/json/html)
   - Save results to file or display in terminal
   - Configurable agent team size and behavior

2. **Research Capabilities**
   - General-purpose research on any topic
   - Integration with local knowledge base (existing knowledge management system)
   - Web search capabilities for up-to-date information
   - Arxiv search capabilieites (incl. download of papers and addition to existing knowledge management system)
   - Ability to analyze and synthesize information from multiple sources
   - Iterative research with configurable rounds

3. **Agent Team Architecture**
   - Multiple specialized agents working together
   - Coordination through Agno workflow v2
   - Clear roles and responsibilities for each agent
   - Communication and handoff between agents

### Technical Requirements

1. **Dependencies**
   - Anthropic API (Claude models) - already in pyproject.toml
   - Agno framework - already in pyproject.toml
   - Web search capabilities (ddgs/duckduckgo-search) - already in pyproject.toml
   - Local knowledge integration (lancedb) - already in pyproject.toml

2. **API Key Management**
   - Support for Anthropic API key via environment variable
   - Option to pass API key via command line
   - Proper error handling for missing/invalid keys

3. **Integration**
   - structured input/output of agents, strict typing (via pydantic)

## Architecture Design

### Agent Team Structure

1. **Research Coordinator Agent**
   - Role: Plans the research approach and coordinates other agents
   - Responsibilities:
     - Analyze the research query
     - Create a research plan
     - Delegate tasks to other agents
     - Monitor progress and adjust strategy

2. **Information Gatherer Agent**
   - Role: Collects raw information from various sources
   - Responsibilities:
     - Search local knowledge base
     - Perform web searches
     - Extract relevant information
     - Pass findings to analyst

3. **Analyst Agent**
   - Role: Processes and structures the gathered information
   - Responsibilities:
     - Analyze collected data
     - Identify patterns and insights
     - Structure information logically
     - Create preliminary findings

4. **Quality Reviewer Agent**
   - Role: Validates and improves research results
   - Responsibilities:
     - Review findings for accuracy
     - Check for completeness
     - Identify gaps or contradictions
     - Suggest improvements

5. **Grading Agent**
   - Role: Evaluates relevance of discovered knowledge
   - Responsibilities:
     - Grade relevance of each piece of knowledge (web/arxiv) to the research topic
     - Provide relevance scores (0-10 scale)
     - Generate importance statements explaining why knowledge is valuable
     - Decide which knowledge should be permanently added to knowledge base
     - Create metadata for knowledge base entries

6. **Report Generator Agent**
   - Role: Creates the final output in requested format
   - Responsibilities:
     - Synthesize all findings
     - Format according to user preference
     - Create clear, actionable output
     - Include sources and references

### Grading Agent Details

The Grading Agent plays a crucial role in determining what knowledge gets permanently stored:

**Grading Criteria:**

- **Relevance Score (0-10)**: How closely the content relates to the research topic
- **Quality Score (0-10)**: Credibility, depth, and accuracy of the source
- **Novelty Score (0-10)**: Whether the information adds new insights

**Importance Statement Structure:**

```python
class ImportanceStatement:
    topic: str                    # Research topic
    relevance_score: float        # 0-10 scale
    quality_score: float          # 0-10 scale
    novelty_score: float          # 0-10 scale
    importance_reason: str        # Why this is important
    key_insights: List[str]       # Bullet points of main insights
    recommended_tags: List[str]   # Tags for knowledge base
```

**Storage Decision Logic:**

- Score >= save_threshold: Automatically save to knowledge base
- Score >= review_threshold and < save_threshold: Flag for user review
- Score < review_threshold: Include in research but don't save

Both thresholds are configurable:

- `--save-threshold`: Minimum score for automatic saving (default: 8.0)
- `--review-threshold`: Minimum score for flagging for review (default: 6.0)

### Workflow vs Team Approach

**Agno Workflow v2** is designed for "deterministic agent automation" - structured, controlled execution with defined steps. **Teams** are for "agentic coordination between agents" - more dynamic collaboration.

For the research command, we'll use **Workflow v2** because:

- We need deterministic, repeatable research processes
- Clear step sequencing (gather → grade → analyze → review → generate)
- Controlled iteration with max_rounds
- Input/output validation between steps

### Agno Workflow v2 Implementation

```python
from agno import Agent, Team
from agno.workflow.v2 import Workflow, Step, Parallel, Condition, Loop
from agno.models.anthropic import Claude
from pydantic import BaseModel
from typing import List

class ResearchQuery(BaseModel):
    query: str
    depth: str
    max_rounds: int
    save_threshold: float
    review_threshold: float

class ResearchResult(BaseModel):
    findings: List[dict]
    saved_knowledge: List[dict]
    report: str

# Individual Agents
coordinator_agent = Agent(
    name="Research Coordinator",
    model=Claude(id="claude-sonnet-4-20250514"),
    instructions="Plan and coordinate research approach. Create structured research plans.",
)

gatherer_agent = Agent(
    name="Information Gatherer",
    model=Claude(id="claude-sonnet-4-20250514"),
    tools=[WebSearchTools(), KnowledgeSearchTools(), ArxivTools()],
    instructions="Collect information from web, local knowledge, and arXiv sources.",
)

grader_agent = Agent(
    name="Grading Agent",
    model=Claude(id="claude-sonnet-4-20250514"),
    instructions="Grade relevance, quality, and novelty of information. Provide structured scores and importance statements.",
)

analyst_agent = Agent(
    name="Analyst",
    model=Claude(id="claude-sonnet-4-20250514"),
    instructions="Analyze and structure gathered information into coherent findings.",
)

reviewer_agent = Agent(
    name="Quality Reviewer",
    model=Claude(id="claude-sonnet-4-20250514"),
    instructions="Review findings for completeness, accuracy, and gaps. Suggest improvements.",
)

generator_agent = Agent(
    name="Report Generator",
    model=Claude(id="claude-sonnet-4-20250514"),
    instructions="Generate final research report in requested format with sources.",
)

# Research Team for parallel information gathering
research_team = Team(
    agents=[gatherer_agent, grader_agent],
    instructions="Collect and grade information from multiple sources in parallel"
)

# Custom function for knowledge base integration
def save_relevant_knowledge(workflow, execution_input):
    """Custom function to save high-scoring knowledge to knowledge base"""
    graded_data = execution_input.get("graded_data", [])
    saved_items = []

    for item in graded_data:
        if item.get("relevance_score", 0) >= workflow.save_threshold:
            # Save to knowledge base with importance statement
            saved_items.append(item)
            # Integration with existing KnowledgeManager here

    return {"saved_knowledge": saved_items}

# Evaluator function for continuing research
def should_continue_research(step_input) -> bool:
    """Determine if research should continue based on completeness"""
    review_result = step_input.get("review_result", {})
    current_round = step_input.get("current_round", 0)
    max_rounds = step_input.get("max_rounds", 3)

    is_incomplete = review_result.get("is_complete", False) == False
    under_limit = current_round < max_rounds

    return is_incomplete and under_limit

# Workflow v2 Definition
research_workflow = Workflow(
    name="Research Workflow v2",
    description="Comprehensive research with agent team coordination",
    steps=[
        # Step 1: Initial planning
        Step(
            name="Research Planning",
            agent=coordinator_agent
        ),

        # Step 2: Iterative research with conditional continuation
        Loop(
            name="Research Iteration Loop",
            steps=[
                # Parallel information gathering and grading
                Parallel(
                    Step(name="Web Research", agent=gatherer_agent),
                    Step(name="Local Knowledge Search", agent=gatherer_agent),
                    Step(name="ArXiv Search", agent=gatherer_agent),
                ),

                # Grade all collected information
                Step(name="Grade Information", agent=grader_agent),

                # Save relevant knowledge (custom function)
                Step(name="Save Knowledge", function=save_relevant_knowledge),

                # Analyze findings
                Step(name="Analyze Findings", agent=analyst_agent),

                # Review for completeness
                Step(name="Quality Review", agent=reviewer_agent),

                # Conditional continuation
                Condition(
                    name="Continue Research Check",
                    evaluator=should_continue_research,
                    steps=[
                        Step(name="Update Research Plan", agent=coordinator_agent)
                    ]
                )
            ]
        ),

        # Step 3: Final report generation
        Step(
            name="Generate Report",
            agent=generator_agent
        )
    ]
)

# Usage with proper Workflow v2 execution
async def run_research(query: str, options: dict) -> ResearchResult:
    research_input = ResearchQuery(
        query=query,
        depth=options.get("depth", "standard"),
        max_rounds=options.get("max_rounds", 3),
        save_threshold=options.get("save_threshold", 8.0),
        review_threshold=options.get("review_threshold", 6.0)
    )

    # Execute the workflow v2
    result = await research_workflow.arun(research_input.model_dump())

    return ResearchResult(
        findings=result.get("findings", []),
        saved_knowledge=result.get("saved_knowledge", []),
        report=result.get("report", "")
    )
```

## Implementation Plan

### File Structure

```text
src/sidekick/
├── cli/
│   └── research.py          # CLI command definition
├── agents/
│   └── research/
│       ├── __init__.py
│       ├── base.py          # Base research agent class
│       ├── coordinator.py   # Research Coordinator
│       ├── gatherer.py      # Information Gatherer
│       ├── grader.py        # Grading Agent
│       ├── analyst.py       # Analyst
│       ├── reviewer.py      # Quality Reviewer
│       └── generator.py     # Report Generator
├── workflows/
│   └── research_workflow.py # Agno workflow implementation
└── research/
    ├── __init__.py
    ├── config.py           # Research configuration
    └── utils.py            # Research utilities
```

### Command Options

```bash
sidekick research "query" [OPTIONS]

Options:
  --depth         [quick|standard|deep]  Research depth (default: standard)
  --format        [markdown|json|html]   Output format (default: markdown)
  --output        PATH                   Save to file (optional)
  --agents        INTEGER                Number of agents (default: 6)
  --max-rounds    INTEGER                Max research iterations (default: 3)
  --verbose       BOOLEAN                Show agent thinking process
  --api-key       TEXT                   Anthropic API key (or use env var)
  --no-web        BOOLEAN                Disable web search
  --no-local      BOOLEAN                Disable local knowledge search
  --no-arxiv      BOOLEAN                Disable arXiv search
  --save-threshold FLOAT                 Minimum relevance score to save to knowledge base (default: 8.0)
  --review-threshold FLOAT               Minimum score for flagging for review (default: 6.0)
```

### Integration Points

1. **Local Knowledge Integration**
   - Reuse existing `KnowledgeManager` from `src/sidekick/knowledge/`
   - Search vector database using query embeddings
   - Retrieve relevant documents for context

2. **Web Search Integration**
   - Use `ddgs` library for DuckDuckGo searches
   - Implement rate limiting and error handling
   - Parse and clean web results

3. **ArXiv Integration**
   - Search arXiv for academic papers
   - Download relevant papers (PDF and metadata)
   - Extract text content for analysis
   - Store papers in knowledge base with grading metadata

4. **Knowledge Base Storage**
   - Integrate with existing knowledge management system
   - Store graded content with relevance scores
   - Include importance statements as metadata
   - Enable future retrieval based on topics

5. **Memory Integration**
   - Use existing memory configuration system
   - Store research sessions for future reference
   - Allow continuation of previous research

## Testing Strategy

### Unit Tests

- Test individual agent behaviors
- Test workflow coordination
- Test output formatting

### Integration Tests

- Test API key validation
- Test knowledge base integration
- Test web search functionality

### End-to-End Tests

- Test complete research workflows
- Test different query types
- Test error scenarios

## Implementation Steps

1. **Create base research agent infrastructure**
   - Define base agent class with common functionality
   - Implement agent communication protocol
   - Set up Agno workflow framework

2. **Implement individual agents**
   - Start with Research Coordinator
   - Implement Information Gatherer with local/web/arxiv search
   - Create Grading Agent with relevance scoring
   - Create Analyst with data processing logic
   - Build Quality Reviewer with validation rules
   - Develop Report Generator with formatting

3. **Create workflow orchestration**
   - Implement Agno workflow v2 pattern
   - Add agent coordination logic
   - Handle iterative research rounds

4. **Build CLI command**
   - Create research.py in cli directory
   - Add command registration to app.py
   - Implement option parsing and validation

5. **Add integrations**
   - Connect to knowledge base
   - Implement web search
   - Add memory persistence

6. **Testing and refinement**
   - Write comprehensive tests
   - Handle edge cases
   - Optimize performance

## Next Steps

1. Review and approve this plan
2. Begin implementation with base infrastructure
3. Iterate on agent behaviors based on testing
4. Deploy and gather user feedback

## Risks and Mitigations

1. **API Rate Limits**
   - Risk: Hitting Anthropic API limits
   - Mitigation: Implement rate limiting and caching

2. **Large Research Topics**
   - Risk: Research becoming too broad/unfocused
   - Mitigation: Implement scope limiting in coordinator

3. **Conflicting Information**
   - Risk: Different sources providing contradictory data
   - Mitigation: Quality reviewer to identify and flag conflicts

4. **Performance**
   - Risk: Long research times for deep queries
   - Mitigation: Implement progress indicators and early termination
