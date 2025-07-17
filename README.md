# RHDH Sidekick - Local Engineering Assistant

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
[![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A locally-running agentic system designed to act as your personal engineering assistant. RHDH Sidekick integrates with your existing tools (GitHub, Jira, codebase) to help automate routine development tasks without requiring context switches to chat interfaces.

**Current Features:**
- AI-powered knowledge search with RAG capabilities
- Automated release notes generation from Jira tickets and GitHub PRs
- Automated test failure analysis for Playwright tests from Prow CI
- Interactive conversational interfaces for iterative refinement

**Planned Features:** Daily standup prep, PR review assistance, Jira maintenance, documentation updates, dynamic plugin configuration, and CI/CD flake analysis.

## 🚀 Setup

```bash
# Install dependencies
uv sync --group dev

# Verify installation
uv run sidekick --help
```

## ⚙️ Configuration

sidekick uses environment variables for configuration. You can set these directly in your shell or create a `.env` file in the project root.

### Creating a .env file

Create a `.env` file in the project root directory:

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your configuration
```

### Required Environment Variables

```bash
# JIRA Configuration (required for release notes)
JIRA_SERVER_URL=https://your-jira-instance.com
JIRA_TOKEN=your-jira-api-token

# GitHub Configuration (required for release notes)
GITHUB_ACCESS_TOKEN=your-github-token
```

### Getting API Tokens

- **JIRA Token**: Go to your JIRA profile → Security → API tokens → Create token
- **GitHub Token**: Go to GitHub Settings → Developer settings → Personal access tokens → Generate new token
  - Required scopes: `repo` (for accessing pull requests)

## 🔍 Search Command

The main feature of sidekick is its AI-powered search functionality that uses RAG (Retrieval-Augmented Generation) to search through knowledge bases.

### Basic Usage

```bash
# Search for information
uv run sidekick search "your search query here"

# Example searches
uv run sidekick search "How to install RHDH on OpenShift?"
uv run sidekick search "What are the authentication methods?"
uv run sidekick search "Explain the plugin architecture"
```

### Interactive Mode

The search command runs in interactive mode by default. After each search result, you can:

- Enter a new query to continue searching
- Press Enter to exit the search session

### Verbose Logging

```bash
# Enable debug logging
uv run sidekick -v search "your query"

# Enable trace logging
uv run sidekick -vv search "your query"
```

## 📝 Release Notes Generation

The release notes command generates comprehensive release notes from JIRA tickets and associated GitHub pull requests using AI.

### Usage

```bash
# Generate release notes for a JIRA ticket
uv run sidekick release-notes generate PROJ-123

# Generate release notes in text format
uv run sidekick release-notes generate PROJ-456 --format text

# Show information about the release notes feature
uv run sidekick release-notes info
```

### Interactive Follow-up

After generating release notes, you can ask follow-up questions:

```bash
uv run sidekick release-notes generate PROJ-123
# After initial generation, you can ask:
# - "Make it more concise"
# - "Add more technical details"
# - "Explain the security improvements"
# - "Format this for a blog post"
```

### How It Works

1. **Fetches JIRA ticket details** using the provided ticket ID
2. **Extracts GitHub PR links** from ticket descriptions, comments, or fields
3. **Retrieves PR details** including descriptions, changes, and commits
4. **Generates comprehensive release notes** using AI that includes:
   - Clear title based on JIRA ticket summary
   - Key changes and improvements from PR descriptions
   - Technical details from changed files when relevant
   - Proper markdown or text formatting

> **Note**: The release notes generator is based on work from [dzemanov/release-notes-generator](https://gitlab.cee.redhat.com/dzemanov/release-notes-generator) ([GitHub](https://github.com/dzemanov)).

## 🔍 Test Analysis

The test analysis feature provides AI-powered root cause analysis for Playwright test failures from Prow CI logs. It automatically analyzes test artifacts including JUnit XML files, screenshots, and pod logs to identify the cause of test failures.

### Usage

```bash
# Analyze a specific Prow CI test failure using the team approach (default)
uv run sidekick test-analysis analyze "https://prow.ci.openshift.org/view/gs/test-platform-results/logs/pull/123/test-run-456"

# Use the single agent instead of the team for analysis
uv run sidekick test-analysis analyze --agent "https://prow.ci.openshift.org/view/gs/test-platform-results/logs/pull/123/test-run-456"

# Download artifacts first, then analyze using cached data
uv run sidekick test-analysis download "https://prow.ci.openshift.org/view/gs/test-platform-results/logs/pull/123/test-run-456"
uv run sidekick test-analysis analyze "https://prow.ci.openshift.org/view/gs/test-platform-results/logs/pull/123/test-run-456"

# Show available commands and options
uv run sidekick test-analysis --help
```

### How It Works

1. **Extracts test artifacts** from Prow CI logs stored in Google Cloud Storage
2. **Parses JUnit XML files** to identify failed test cases and extract failure messages
3. **Analyzes screenshots** using AI vision to understand visual test failures
4. **Reviews pod logs** and build logs for additional context
5. **Provides comprehensive root cause analysis** with:
   - Clear explanation of what went wrong
   - Visual confirmation from screenshots when available
   - Specific failure points from logs
   - Actionable insights for fixing the issues

### Interactive Follow-up

After initial analysis, you can ask follow-up questions:

```bash
# After initial analysis, you can ask:
# - "Can you explain the screenshot in more detail?"
# - "What logs should I check for more information?"
# - "How can I reproduce this failure locally?"
# - "What are the most common causes of this type of failure?"
```

### Analysis Modes

The test analysis feature supports two analysis modes:

#### Team Mode (Default)
- **Coordinate Mode Team**: Uses specialized agents for different types of analysis
- **Screenshot Analyzer**: Dedicated agent for visual evidence analysis
- **Log Analyzer**: Specialized agent for JUnit XML, build logs, and pod logs
- **Team Leader**: Coordinates analysis and synthesizes findings from all agents
- **Best for**: Complex failures requiring multiple perspectives and comprehensive analysis

#### Agent Mode (`--agent`)
- **Single Agent**: Uses a single comprehensive agent for all analysis
- **Unified Analysis**: Processes all artifacts (JUnit XML, screenshots, logs) in one pass
- **Best for**: Faster analysis or when you prefer a single analytical perspective

### Features

- **Multi-format Analysis**: Supports JUnit XML, screenshots (PNG/JPG), and various log formats
- **Visual Confirmation**: AI-powered screenshot analysis to understand UI-related failures
- **Comprehensive Coverage**: Analyzes test results, pod logs, and build logs
- **Interactive Mode**: Conversational interface for deeper investigation
- **Cloud Integration**: Direct access to Prow CI artifacts in Google Cloud Storage
- **Flexible Analysis**: Choose between team coordination or single agent analysis

### Prerequisites

- Google Cloud Storage access credentials for Prow CI artifacts
- Prow CI link with test failure information

> **Note**: The test analysis feature is built on the TestTriage project by [subhashkhileri](https://github.com/subhashkhileri/TestTriage).

## Other Commands

```bash
# Show version
uv run sidekick version

# Show application info
uv run sidekick info
```

## License

Apache License 2.0 - See [LICENSE](LICENSE) file for details.
