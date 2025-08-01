# Contributing to RHDH Sidekick

Thank you for your interest in contributing to RHDH Sidekick! This guide will help you understand the project architecture and get started with development.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Development Environment](#development-environment)
- [Code Structure](#code-structure)
- [Key Concepts](#key-concepts)
- [Adding Features](#adding-features)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)

## Architecture Overview

RHDH Sidekick is a locally-running agentic system built on the [Agno](https://github.com/agno-agi/agno) framework. It provides AI-powered assistance for engineering tasks through specialized agents that integrate with your development tools.

For a detailed technical architecture including diagrams and component descriptions, see the [Architecture Documentation](docs/architecture.md).

### Core Components

1. **CLI Layer** (`src/sidekick/cli/`)
   - Built with [Typer](https://typer.tiangolo.com/) for modern CLI interfaces
   - Modular command structure with sub-applications
   - Global options for logging, streaming, and user configuration

2. **Agent System** (`src/sidekick/agents/`)
   - Base factory pattern for consistent agent creation
   - Specialized agents for different domains (Jira, GitHub, Search, etc.)
   - Mixin-based composition for code reuse

3. **Team Coordination** (`src/sidekick/teams/`)
   - Multi-agent teams for complex workflows
   - Coordinate mode teams that combine specialized agents
   - Shared memory and state management

4. **Knowledge Management** (`src/sidekick/knowledge/`)
   - RAG-powered search across multiple sources
   - Vector database integration with LanceDB
   - Support for Google Drive, Git repos, and web pages

5. **Prompt System** (`src/sidekick/prompts/`)
   - YAML-based prompt templates with variable substitution
   - Template inheritance and includes
   - Registry pattern for dynamic loading

6. **Tool Integration** (`src/sidekick/tools/`)
   - Google Drive toolkit for document management
   - State management for agent sessions
   - Test analysis utilities

## Development Environment

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) for dependency management
- Google Cloud credentials (for certain features)
- API tokens for Jira and GitHub

### Setup

```bash
# Clone the repository
git clone https://github.com/durandom/rhdh-sidekick.git
cd rhdh-sidekick

# Install dependencies
uv sync --group dev

# Copy environment template
cp .env.example .env
# Edit .env with your API tokens

# Run the application
uv run sidekick --help
```

### Development Commands

```bash
# Run tests
uv run pytest

# Run with debug logging
uv run sidekick -v <command>

# Format code
uv run ruff format

# Lint code
uv run ruff check

# Type checking
uv run mypy src/
```

For complete configuration options and environment variables, see the [Configuration Guide](docs/configuration.md).

## Code Structure

```
src/sidekick/
├── cli/              # CLI commands and sub-applications
├── agents/           # AI agent implementations
│   ├── base.py       # Base agent factory
│   └── mixins/       # Reusable agent components
├── teams/            # Multi-agent team implementations
├── knowledge/        # Knowledge base management
├── prompts/          # Prompt templates and registry
│   └── templates/    # YAML prompt definitions
├── tools/            # Tool integrations
├── utils/            # Shared utilities
├── workflows/        # Complex workflow implementations
└── settings.py       # Application configuration
```

## Key Concepts

### Agent Factory Pattern

All agents inherit from `BaseAgentFactory` and implement:
- `create_agent()` - Create the Agno Agent instance
- `setup_context()` - Initialize async resources (MCP tools, knowledge base)
- `cleanup_context()` - Clean up resources
- `get_required_env_vars()` - Declare environment dependencies

### Mixin Composition

Common agent functionality is provided through mixins:
- `JiraMixin` - MCP Atlassian server integration
- `KnowledgeMixin` - Knowledge base and RAG tools
- `WorkspaceMixin` - File operations and workspace management
- `StorageMixin` - SQLite storage for agent state

### Prompt Templates

Agents use YAML-based prompt templates that support:
- Variable substitution with defaults
- Template inheritance via includes
- Instruction list formatting
- Version management

### Memory and State

- User-specific memory using Agno's Memory v2
- Session storage in SQLite databases
- Workspace directories for file operations
- State management tools for complex workflows

## Adding Features

### Adding a New Agent

1. Create agent file in `src/sidekick/agents/`
2. Inherit from `BaseAgentFactory` and relevant mixins
3. Implement required methods
4. Create prompt template in `src/sidekick/prompts/templates/agents/`
5. Add CLI command in `src/sidekick/cli/`

For a comprehensive step-by-step guide with examples and best practices, see the [Creating Agents Guide](docs/creating-agents.md).

Example structure:
```python
from ..agents.base import BaseAgentFactory
from ..agents.mixins import WorkspaceMixin, StorageMixin

class MyAgent(BaseAgentFactory, WorkspaceMixin, StorageMixin):
    def create_agent(self, context):
        # Create and return Agno Agent
        pass

    def get_required_env_vars(self):
        return ["MY_API_KEY"]
```

### Adding a New Command

1. Create command module in `src/sidekick/cli/`
2. Use Typer to define command structure
3. Register in `src/sidekick/cli/app.py`

### Adding Tool Integration

1. Create tool class in `src/sidekick/tools/`
2. Follow Agno's tool interface patterns
3. Add documentation and examples

## Testing

### Test Structure

```
tests/
├── unit/         # Unit tests for individual components
├── integration/  # Integration tests for component interactions
├── e2e/         # End-to-end CLI tests
└── conftest.py  # Shared fixtures
```

### Writing Tests

- Use pytest for all tests
- Mock external dependencies
- Test both success and error cases
- Use fixtures for common setup

### Running Tests

```bash
# All tests
uv run pytest

# Specific test file
uv run pytest tests/unit/test_agents.py

# With coverage
uv run pytest --cov=src --cov-report=html
```

For detailed testing patterns, debugging tips, and best practices, see the [Testing Guide](docs/testing.md).

## Documentation

### Code Documentation

- Use Google-style docstrings
- Document all public APIs
- Include usage examples
- Keep docstrings up-to-date

### User Documentation

- Update README.md for user-facing changes
- Add detailed guides in `docs/` for complex features
- Update CLAUDE.md for AI assistant context
- Include examples for new features

### Architecture Documentation

- Update this CONTRIBUTING.md for architectural changes
- Document design decisions in `docs/plans/`
- Keep component diagrams current

## Submitting Changes

### Before Submitting

1. **Run all tests**: `uv run pytest`
2. **Format code**: `uv run ruff format`
3. **Check linting**: `uv run ruff check`
4. **Update documentation**: Add/update relevant docs
5. **Test manually**: Verify your changes work as expected

### Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes following the coding standards
4. Commit with clear messages: `git commit -m "feat: add new agent for X"`
5. Push to your fork: `git push origin feature/my-feature`
6. Create a pull request with:
   - Clear description of changes
   - Link to related issues
   - Test results
   - Documentation updates

### Commit Messages

Follow conventional commits:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Test additions/changes
- `chore:` - Maintenance tasks

## Getting Help

- Check existing issues and discussions
- Review the documentation in `docs/`
- Ask questions in pull requests
- Refer to the Agno documentation for framework details

## Detailed Documentation

For more in-depth information, see these guides in the `docs/` directory:

- **[Architecture](docs/architecture.md)** - System architecture, components, and data flow
- **[Configuration](docs/configuration.md)** - Environment variables, settings, and runtime configuration
- **[Creating Agents](docs/creating-agents.md)** - Step-by-step guide to building new agents
- **[Testing](docs/testing.md)** - Testing strategies, patterns, and best practices

## Additional Resources

- [Agno Documentation](https://github.com/agno-agi/agno)
- [Typer Documentation](https://typer.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Rich Documentation](https://rich.readthedocs.io/)

Thank you for contributing to RHDH Sidekick! Your efforts help make this tool better for everyone.
