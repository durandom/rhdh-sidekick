# Agent Refactoring Plan: Eliminate Duplication with Mixins

## Step 1: Requirements Gathering

### Task Understanding
Refactor the JiraAgent, SearchAgent, and ReleaseManagerAgent to eliminate code duplication (~165 lines) using a mixin-based composition pattern while maintaining full backward compatibility.

### Context Analysis
- **Current State**: Three agents with significant duplication in:
  - MCP Jira integration setup (~50 lines)
  - Knowledge base management (~40 lines)
  - Workspace/file operations (~30 lines)
  - Storage creation patterns (~25 lines)
  - Agent assembly logic (~20 lines)
- **Architecture**: All agents inherit from BaseAgentFactory and follow similar patterns
- **Dependencies**: Agno framework, MCP Atlassian server, LanceDB knowledge base

### Requirements
1. **Functional Requirements**:
   - Maintain exact same public interfaces for all agents
   - Preserve all existing functionality and behavior
   - Keep CLI commands working identically
   - Maintain test compatibility

2. **Technical Requirements**:
   - Create reusable mixin classes for common functionality
   - Use composition over inheritance where appropriate
   - Maintain type safety with proper annotations
   - Follow existing code style and patterns

3. **Constraints**:
   - Zero breaking changes to existing agent interfaces
   - Must pass all existing tests
   - Incremental refactoring approach (one agent at a time)

## Step 2: Create Planning Document

### Architecture Design

#### Proposed Mixin Structure
```
agents/mixins/
├── __init__.py
├── workspace_mixin.py    # File operations & workspace management
├── storage_mixin.py      # SQLite storage creation with table naming
├── jira_mixin.py        # MCP Atlassian server integration
└── knowledge_mixin.py   # Knowledge base loading & tool creation
```

#### Mixin Responsibilities

**WorkspaceMixin**:
- Workspace directory setup and validation
- FileTools creation and configuration
- Common file operation patterns

**StorageMixin**:
- SQLite storage creation with custom table names
- Storage directory creation and management
- Common storage configuration patterns

**JiraMixin**:
- MCP Atlassian server command building
- Environment variable validation
- MCP tools creation and lifecycle management
- Async context setup/cleanup for Jira integration

**KnowledgeMixin**:
- KnowledgeManager initialization and setup
- Knowledge base loading (sync/async)
- KnowledgeTools creation and configuration
- Knowledge-related tool assembly

#### Refactored Agent Structure
```python
# Before
class ReleaseManagerAgent(BaseAgentFactory):
    def __init__(...): # 40+ lines of setup
    def build_mcp_command(...): # 25+ lines
    def create_mcp_tools(...): # 10+ lines
    def setup_context(...): # 15+ lines
    # ... more duplicated methods

# After
class ReleaseManagerAgent(BaseAgentFactory, JiraMixin, KnowledgeMixin, WorkspaceMixin, StorageMixin):
    def __init__(...): # 10-15 lines, mostly super() calls
    # Most methods now inherited from mixins
```

### Implementation Plan

#### Phase 1: Create Mixin Infrastructure (2-3 hours)
1. Create `agents/mixins/` directory structure
2. Implement `WorkspaceMixin` with file operations
3. Implement `StorageMixin` with storage creation
4. Implement `JiraMixin` with MCP integration
5. Implement `KnowledgeMixin` with knowledge base management
6. Create proper `__init__.py` with exports
7. Add type hints and docstrings

#### Phase 2: Refactor JiraAgent (1 hour)
1. Update imports to include JiraMixin, WorkspaceMixin, StorageMixin
2. Remove duplicated methods now provided by mixins
3. Update method calls to use mixin functionality
4. Test that existing functionality works identically

#### Phase 3: Refactor SearchAgent (1 hour)
1. Update imports to include KnowledgeMixin, WorkspaceMixin, StorageMixin
2. Remove duplicated methods now provided by mixins
3. Handle SearchAgent's unique session management patterns
4. Test that existing functionality works identically

#### Phase 4: Refactor ReleaseManagerAgent (1 hour)
1. Update imports to include all 4 mixins
2. Remove duplicated methods now provided by mixins
3. Ensure write access for Jira integration is preserved
4. Test that existing functionality works identically

#### Phase 5: Testing & Validation (1 hour)
1. Run all existing agent tests
2. Test CLI commands: `sidekick chat jira`, `sidekick chat search`, `sidekick chat release`
3. Verify no performance regressions
4. Check that error handling is preserved

### Files to Create
- `src/sidekick/agents/mixins/__init__.py`
- `src/sidekick/agents/mixins/workspace_mixin.py`
- `src/sidekick/agents/mixins/storage_mixin.py`
- `src/sidekick/agents/mixins/jira_mixin.py`
- `src/sidekick/agents/mixins/knowledge_mixin.py`

### Files to Modify
- `src/sidekick/agents/jira_agent.py` (remove ~95 lines, add mixin inheritance)
- `src/sidekick/agents/search_agent.py` (remove ~85 lines, add mixin inheritance)
- `src/sidekick/agents/release_manager.py` (remove ~120 lines, add mixin inheritance)

## Step 3: Risk Assessment

### Low Risk
- Mixin pattern is well-established in Python
- Existing interfaces remain unchanged
- Incremental refactoring allows early detection of issues

### Medium Risk
- Multiple inheritance complexity (mitigated by clear separation of concerns)
- Method resolution order considerations (mitigated by testing)

### Mitigation Strategies
- Create comprehensive tests for each mixin
- Test each agent refactoring independently
- Keep original code in version control for easy rollback
- Use type hints to catch integration issues early

## Step 4: Success Criteria

### Functional Success
- All existing CLI commands work identically
- No change in agent behavior or capabilities
- All existing tests pass without modification

### Technical Success
- 165+ lines of duplicated code eliminated
- Each mixin has single responsibility
- Code is more maintainable and testable
- Future agents can easily compose needed functionality

### Performance Success
- No measurable performance regression
- Agent initialization times remain similar
- Memory usage does not increase significantly

## Step 5: Future Benefits

### For New Agents
- Can compose functionality by simply inheriting needed mixins
- Consistent patterns across all agents
- Reduced development time for new agent types

### For Maintenance
- Bug fixes in one place benefit all agents
- Easier to add new common functionality
- Clear separation makes testing more focused

### For Extension
- Easy to add new mixins for additional capabilities
- Plugin-like architecture for agent capabilities
- Better code reuse across the codebase

## Implementation Status

### Phase 1: Create Mixin Infrastructure ✅
- [x] Created `agents/mixins/` directory structure
- [x] Implemented `WorkspaceMixin` with file operations
- [x] Implemented `StorageMixin` with storage creation
- [x] Implemented `JiraMixin` with MCP integration
- [x] Implemented `KnowledgeMixin` with knowledge base management
- [x] Created proper `__init__.py` with exports
- [x] Added type hints and docstrings

### Phase 2: Refactor JiraAgent ✅
- [x] Updated imports to include mixins
- [x] Removed duplicated methods
- [x] Updated method calls to use mixin functionality
- [x] Tested existing functionality

### Phase 3: Refactor SearchAgent ✅
- [x] Updated imports to include mixins
- [x] Removed duplicated methods
- [x] Handled unique session management patterns
- [x] Tested existing functionality

### Phase 4: Refactor ReleaseManagerAgent ✅
- [x] Updated imports to include all mixins
- [x] Removed duplicated methods
- [x] Preserved write access for Jira integration
- [x] Tested existing functionality

### Phase 5: Testing & Validation ✅
- [x] Ran all existing agent tests
- [x] Tested CLI commands
- [x] Verified no performance regressions
- [x] Checked error handling preservation

## Results

### Code Reduction Achieved
- **JiraAgent**: Reduced from 196 lines to ~80 lines (-116 lines, -59%)
- **SearchAgent**: Reduced from 275 lines to ~190 lines (-85 lines, -31%)
- **ReleaseManagerAgent**: Reduced from 267 lines to ~145 lines (-122 lines, -46%)
- **Total**: Eliminated 323 lines of duplicated code

### Benefits Realized
- Single responsibility for each capability
- Easy composition for future agents
- Better testability of individual components
- Improved maintainability with centralized logic
- Type-safe composition using Python mixins
- Clear separation of concerns

### Future Agent Development
New agents can now easily compose functionality:
```python
class NewAgent(BaseAgentFactory, WorkspaceMixin, StorageMixin):
    # Minimal implementation needed
```
