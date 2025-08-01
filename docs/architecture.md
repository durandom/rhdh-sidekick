# RHDH Sidekick Architecture

This document provides a detailed technical overview of the RHDH Sidekick architecture.

## System Overview

RHDH Sidekick is built as a modular, extensible system that runs locally on developer machines while leveraging cloud-hosted AI models. The architecture emphasizes:

- **Local-first execution** - All agents run on the developer's machine
- **Tool integration** - Native integration with GitHub, Jira, and other developer tools
- **Extensibility** - Easy to add new agents and capabilities
- **Memory persistence** - Agents remember context across sessions

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI Layer                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────┐   │
│  │  chat   │  │knowledge│  │release- │  │test-analysis│   │
│  │commands │  │commands │  │  notes  │  │  commands   │   │
│  └────┬────┘  └────┬────┘  └────┬────┘  └──────┬──────┘   │
└───────┼────────────┼────────────┼──────────────┼───────────┘
        │            │            │              │
┌───────┴────────────┴────────────┴──────────────┴───────────┐
│                      Agent Layer                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────┐   │
│  │  Jira   │  │ GitHub  │  │ Search  │  │Release Mgr  │   │
│  │  Agent  │  │  Agent  │  │  Agent  │  │   Agent     │   │
│  └────┬────┘  └────┬────┘  └────┬────┘  └──────┬──────┘   │
│       │            │            │              │            │
│  ┌────┴────────────┴────────────┴──────────────┴────┐      │
│  │              Agent Mixins                         │      │
│  │  JiraMixin, KnowledgeMixin, WorkspaceMixin,     │      │
│  │  StorageMixin                                    │      │
│  └──────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
        │
┌───────┴─────────────────────────────────────────────────────┐
│                    Foundation Layer                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────┐   │
│  │  Agno   │  │ Prompts │  │Knowledge│  │   Tools     │   │
│  │Framework│  │ System  │  │ Manager │  │Integration  │   │
│  └─────────┘  └─────────┘  └─────────┘  └─────────────┘   │
└─────────────────────────────────────────────────────────────┘
        │
┌───────┴─────────────────────────────────────────────────────┐
│                    External Services                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────┐   │
│  │  Jira   │  │ GitHub  │  │ Google  │  │ AI Models   │   │
│  │   API   │  │   API   │  │  Drive  │  │  (Gemini)   │   │
│  └─────────┘  └─────────┘  └─────────┘  └─────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### CLI Layer

The CLI layer provides the user interface through Typer-based commands:

- **Main Application** (`cli/app.py`) - Entry point and global options
- **Command Modules** - Specialized commands for different features
- **Rich Integration** - Beautiful terminal output and progress indicators

### Agent Layer

Agents are the core intelligence units, each specialized for different tasks:

#### Base Agent Factory

All agents inherit from `BaseAgentFactory` which provides:
- Standardized initialization pattern
- Context setup/cleanup lifecycle
- Prompt template loading
- Memory integration

#### Agent Types

1. **JiraAgent** - Jira ticket management and search
2. **GitHubAgent** - Repository and PR operations
3. **SearchAgent** - RAG-powered knowledge search
4. **ReleaseManagerAgent** - Coordinated release note generation
5. **TestAnalysisAgent** - Playwright test failure analysis

#### Mixin Architecture

Common functionality is provided through mixins:

```python
class JiraMixin:
    # MCP Atlassian server integration
    # Environment variable validation
    # Tool lifecycle management

class KnowledgeMixin:
    # Knowledge base loading
    # Vector database operations
    # RAG tool creation

class WorkspaceMixin:
    # File system operations
    # Workspace directory management
    # FileTools integration

class StorageMixin:
    # SQLite storage creation
    # Session persistence
    # State management
```

### Team Layer

Teams coordinate multiple agents for complex workflows:

- **TagTeam** - Combines Jira, GitHub, and Search agents
- **TestAnalysisTeam** - Coordinates screenshot and log analysis
- **Shared Memory** - Teams share context and findings

### Foundation Layer

#### Agno Framework

The project is built on [Agno](https://github.com/agno-agi/agno), which provides:
- Agent creation and lifecycle management
- Tool integration patterns
- Memory persistence
- Streaming response handling

#### Prompt System

A sophisticated prompt management system:
- YAML-based templates with variables
- Template inheritance and includes
- Registry pattern for dynamic loading
- Version management

#### Knowledge Manager

Handles all knowledge base operations:
- Multi-source synchronization (Google Drive, Git, Web)
- Vector database management (LanceDB)
- Document chunking and embedding
- RAG retrieval operations

#### Tool Integration

Standardized tool patterns:
- MCP (Model Context Protocol) for external services
- FileTools for local operations
- Custom tools for specific integrations

## Data Flow

### Typical Request Flow

1. **User Input** → CLI command with parameters
2. **CLI Processing** → Parse arguments, setup logging
3. **Agent Creation** → Factory creates agent with context
4. **Tool Setup** → Initialize required tools (MCP, Knowledge, etc.)
5. **LLM Processing** → Agent processes request with tools
6. **Response Streaming** → Stream results back to user
7. **Cleanup** → Close connections, save state

### Memory and State

```
User-specific Memory (Agno Memory v2)
├── Conversation History
├── User Preferences
└── Context Retention

Session Storage (SQLite)
├── Agent State
├── Tool Results
└── Temporary Data

Knowledge Base (LanceDB)
├── Document Embeddings
├── Metadata
└── Vector Indices
```

## Security Considerations

### API Key Management

- Environment variables for sensitive data
- No hardcoded credentials
- Validation at startup

### Local Execution

- All processing happens locally
- Only API calls go to external services
- No data stored in cloud (except API logs)

### File System Access

- Scoped to workspace directories
- No arbitrary file system access
- User-controlled permissions

## Extension Points

### Adding New Agents

1. Create agent class inheriting from `BaseAgentFactory`
2. Use appropriate mixins for common functionality
3. Define prompt template in YAML
4. Add CLI command

### Adding New Tools

1. Implement tool following Agno patterns
2. Add to agent's tool list
3. Document tool capabilities

### Adding New Commands

1. Create command module in `cli/`
2. Define Typer app with commands
3. Register in main app

## Performance Characteristics

### Startup Time

- Initial load: 2-3 seconds (model initialization)
- Subsequent commands: < 1 second
- Knowledge base indexing: Varies by size

### Memory Usage

- Base application: ~100MB
- With knowledge base: 200-500MB
- During LLM calls: Up to 1GB

### Scalability

- Knowledge base: Tested up to 10,000 documents
- Concurrent agents: Limited by local resources
- API rate limits: Respected per service

## Configuration

### Environment Variables

```bash
# Core Configuration
AGNO_DEBUG=true
LOG_LEVEL=DEBUG

# API Keys
JIRA_SERVER_URL=https://...
JIRA_TOKEN=...
GITHUB_ACCESS_TOKEN=...
GOOGLE_API_KEY=...

# Optional
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_SECRET_KEY=...
LANGFUSE_HOST=...
```

### Settings Management

- Pydantic-based settings in `settings.py`
- Environment variable override
- Nested configuration support
- Type validation

## Monitoring and Observability

### Logging

- Loguru-based structured logging
- Multiple log levels (TRACE, DEBUG, INFO, etc.)
- File and console output
- Automatic pytest integration

### Tracing

- Optional Langfuse integration
- OpenTelemetry support
- Request tracing
- Performance metrics

## Future Architecture Considerations

### Planned Enhancements

1. **Plugin System** - Dynamic agent loading
2. **Remote Execution** - Optional cloud deployment
3. **Team Workflows** - More sophisticated coordination
4. **Caching Layer** - Improved performance
5. **Event System** - Reactive agent triggers

### Scalability Path

1. **Distributed Agents** - Run agents on multiple machines
2. **Shared Knowledge** - Team-wide knowledge bases
3. **Agent Marketplace** - Share agent definitions
4. **Cloud Sync** - Optional state synchronization
