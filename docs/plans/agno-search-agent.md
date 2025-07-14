# Agno Search Agent Implementation Plan

## Step 1: Requirements Gathering

### Task Understanding
Implement an Agno-powered AI agent with RAG capabilities to replace the existing simple search functionality in the sidekick CLI application.

### Context Analysis
- **Existing System**: Simple string matching search in `src/sidekick/commands.py`
- **Knowledge Base**: Red Hat Developer Hub documentation in `knowledge/rag/rhdh/` (25 markdown files)
- **Test Coverage**: BDD tests in `tests/bdd/test_search.py` expect specific output format
- **Architecture**: Modular CLI using command registry pattern with Typer framework

### Requirements
1. **Functional Requirements**:
   - Replace simple search with AI-powered RAG search
   - Maintain compatibility with existing BDD tests
   - Use LanceDB for vector storage and hybrid search
   - Integrate with RHDH documentation knowledge base
   - Provide conversational search capabilities

2. **Technical Requirements**:
   - Use Agno framework for agent implementation
   - Claude Sonnet 4 as the LLM backend
   - OpenAI embeddings (text-embedding-3-small, 1536 dimensions)
   - SQLite for agent session storage
   - Maintain existing CLI command structure

3. **Constraints**:
   - Must not modify existing BDD tests
   - Output format must match: "Found X results for 'query'"
   - Must handle "nonexistent" queries gracefully
   - Code must follow existing project patterns

### Success Criteria
- ✅ All existing BDD tests pass without modification
- ✅ Agent provides relevant, context-aware responses from RHDH docs
- ✅ Search command integrates seamlessly with existing CLI
- ✅ Knowledge base loads automatically from `knowledge/rag/`
- ✅ Error handling prevents CLI crashes

### Scope Definition
**In Scope**:
- Agent implementation with RAG capabilities
- Knowledge base management for RHDH documentation
- Search command integration
- Session storage for conversation history

**Out of Scope**:
- Modifying existing BDD tests
- Adding new CLI commands
- Changing overall application architecture
- Adding web interface or API endpoints

## Step 2: Current State Analysis

### Existing Architecture
```
src/sidekick/
├── cli/
│   ├── base.py          # Command registry, logging setup
│   └── app.py           # Main CLI app with global options
├── commands.py          # Example and Search command groups
└── settings.py          # Pydantic settings management
```

### Current Search Implementation
- Located in `SearchCommands.search()` method
- Simple string matching against hardcoded sample data
- Returns formatted results matching BDD test expectations
- No persistent storage or AI capabilities

### Knowledge Base Structure
```
knowledge/rag/rhdh/
├── about/index.md
├── adoption-insights/index.md
├── audit-log/index.md
[... 22 more documentation files]
```

### Dependencies Available
- ✅ agno>=1.7.2
- ✅ lancedb>=0.24.1
- ✅ openai>=1.95.0
- ✅ anthropic>=0.57.1
- ✅ sqlalchemy>=2.0.41

## Step 3: Implementation Approach

### Architecture Design
```
src/sidekick/agents/
├── __init__.py          # Package initialization
├── knowledge.py         # Knowledge base management
└── search_agent.py      # Main agent implementation

Updated:
src/sidekick/commands.py # Modified SearchCommands.search()
```

### Component Design

#### 1. Knowledge Base Manager (`knowledge.py`)
```python
class KnowledgeManager:
    """Manages RHDH documentation knowledge base."""

    def __init__(self, knowledge_path: Path, vector_db_path: Path)
    def load_knowledge(self, recreate: bool = False) -> UrlKnowledge
    def get_vector_db(self) -> LanceDb
```

#### 2. Search Agent (`search_agent.py`)
```python
class SearchAgent:
    """Agno-powered search agent with RAG capabilities."""

    def __init__(self)
    def initialize(self) -> None  # Lazy loading
    def search(self, query: str) -> str
    def _format_response(self, response: str, query: str) -> str
```

#### 3. Integration Layer
- Modify `SearchCommands.search()` to use agent
- Maintain exact output format for BDD compatibility
- Add error handling with fallback to simple search

### Data Flow
1. User executes `sidekick search search <query>`
2. SearchCommands.search() calls SearchAgent.search()
3. Agent searches knowledge base using RAG
4. Response formatted to match BDD test expectations
5. Results displayed to user

### Storage Strategy
- **Vector DB**: `tmp/lancedb/rhdh_docs` table
- **Sessions**: `tmp/agent.db` SQLite database
- **Knowledge**: Load from `knowledge/rag/rhdh/` directory
- **Embeddings**: Cached in LanceDB for reuse

## Step 4: Implementation Details

### File Structure
```
New Files:
- src/sidekick/agents/__init__.py
- src/sidekick/agents/knowledge.py
- src/sidekick/agents/search_agent.py

Modified Files:
- src/sidekick/commands.py (SearchCommands class only)
```

### Key Implementation Decisions

#### Agent Configuration
- **Model**: Claude Sonnet 4 (claude-sonnet-4-20250514)
- **Instructions**: ["Search your knowledge before answering", "Be concise and direct"]
- **History**: 3 previous runs for context
- **Output**: Markdown format for rich display

#### Knowledge Base Settings
- **Embedder**: OpenAI text-embedding-3-small (1536 dimensions)
- **Search Type**: Hybrid (keyword + semantic)
- **Table Name**: "rhdh_docs"
- **URI**: "tmp/lancedb"

#### Error Handling Strategy
- Graceful degradation if agent initialization fails
- Fallback to simple search for critical errors
- Proper logging for debugging
- User-friendly error messages

### BDD Test Compatibility
Current tests expect:
- Query "python" → "Found 1 results for 'python'" + "Python programming tutorial"
- Query "nonexistent" → "No results found for 'nonexistent'"

Strategy: Format agent responses to match these patterns exactly.

## Step 5: Testing Strategy

### Existing Test Coverage
- BDD tests in `tests/bdd/test_search.py`
- Feature file: `tests/bdd/features/search.feature`
- Test scenarios cover both found and not-found cases

### Validation Approach
1. Run existing BDD tests before implementation
2. Implement agent incrementally
3. Test agent responses match expected format
4. Run BDD tests after each major change
5. Validate knowledge base loading and search quality

### Test Commands
```bash
# Run BDD tests specifically
uv run pytest tests/bdd/test_search.py -v

# Run all tests with coverage
uv run pytest --cov=src --cov-report=term-missing

# Manual CLI testing
uv run sidekick search search python
uv run sidekick search search nonexistent
```

## Step 6: Dependencies and Prerequisites

### Required Dependencies
All dependencies already available in `pyproject.toml`:
- agno>=1.7.2 ✅
- lancedb>=0.24.1 ✅
- openai>=1.95.0 ✅
- anthropic>=0.57.1 ✅

### Environment Setup
- OpenAI API key for embeddings
- Anthropic API key for Claude
- Sufficient disk space for vector database (~100MB)

### Knowledge Base Preparation
- RHDH documentation already available in `knowledge/rag/rhdh/`
- 25 markdown files with comprehensive Red Hat Developer Hub content
- No additional preparation needed

## Step 7: Risk Assessment

### Technical Risks
1. **API Rate Limits**: Mitigated by caching embeddings and responses
2. **Vector DB Size**: Estimated ~100MB, acceptable for development
3. **Agent Response Format**: Addressed by response formatting layer
4. **Knowledge Loading Time**: Mitigated by lazy loading strategy

### Integration Risks
1. **BDD Test Compatibility**: High priority, addressed by exact format matching
2. **CLI Performance**: Lazy loading prevents startup delays
3. **Error Handling**: Fallback mechanisms ensure CLI stability

### Mitigation Strategies
- Incremental implementation with testing at each step
- Fallback to simple search if agent fails
- Comprehensive error logging for debugging
- Format validation before returning responses

## Step 8: Implementation Timeline

### Phase 1: Foundation (High Priority)
1. Create agents directory structure
2. Implement KnowledgeManager class
3. Basic agent initialization

### Phase 2: Core Functionality (High Priority)
1. Implement SearchAgent with RAG capabilities
2. Knowledge base loading and vector storage
3. Basic search functionality

### Phase 3: Integration (High Priority)
1. Update SearchCommands to use agent
2. Response formatting for BDD compatibility
3. Error handling and fallback logic

### Phase 4: Validation (Medium Priority)
1. Run existing BDD tests
2. Manual testing and validation
3. Performance optimization if needed

## Step 9: Success Metrics

### Functional Metrics
- ✅ All existing BDD tests pass (100% compatibility)
- ✅ Agent provides relevant responses from RHDH docs
- ✅ Search handles both successful and failed queries
- ✅ CLI maintains same user experience

### Technical Metrics
- ✅ Knowledge base loads successfully
- ✅ Vector database stores embeddings correctly
- ✅ Agent sessions persist properly
- ✅ Error handling prevents crashes

### Quality Metrics
- ✅ Code follows existing project patterns
- ✅ Type hints and documentation complete
- ✅ No new lint or type errors
- ✅ Memory usage remains reasonable

---

## Next Steps

After plan approval:
1. Begin Phase 1 implementation
2. Create agents directory and base structure
3. Implement knowledge management layer
4. Build and test core agent functionality
5. Integrate with existing search command
6. Validate against BDD tests

## Implementation Notes

This plan follows the existing project patterns and maintains backward compatibility while adding powerful AI-driven search capabilities. The modular design allows for easy maintenance and future enhancements.
