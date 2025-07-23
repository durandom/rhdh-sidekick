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

### Response Output Options

By default, sidekick uses streaming output for real-time response display. You can control this behavior:

```bash
# Default: streaming output (real-time response)
uv run sidekick search "your query"

# Disable streaming (wait for complete response)
uv run sidekick --no-streaming search "your query"
```

### Verbose Logging

```bash
# Enable debug logging
uv run sidekick -v search "your query"

# Enable trace logging
uv run sidekick -vv search "your query"

# Combine options
uv run sidekick -vv --no-streaming search "your query"
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

## 📚 Knowledge Management

The knowledge management system allows you to sync and manage documentation from multiple sources including Google Drive, Git repositories, and web pages. All content is automatically organized and made searchable through the AI-powered search functionality.

### Quick Start

1. **Edit configuration file**:
   ```bash
   # The default configuration is at knowledge/external/sources.yaml
   vi knowledge/external/sources.yaml
   ```

2. **Sync all sources**:
   ```bash
   # Sync all configured sources (uses knowledge/external/sources.yaml → knowledge/external/ by default)
   uv run sidekick knowledge sync
   ```

3. **Search your knowledge**:
   ```bash
   # Search across all synced content
   uv run sidekick search "How to configure authentication"
   ```

### Configuration

Knowledge sources are defined in `knowledge/external/sources.yaml` by default. The system supports three source types:

#### Google Drive Documents
```yaml
- type: gdrive
  name: team-docs
  export_format: md
  documents:
    - url: "https://docs.google.com/document/d/DOCUMENT_ID/edit"
      depth: 2  # Follow links 2 levels deep
      comment: "Main documentation"
```

#### Git Repositories
```yaml
- type: git
  name: project-docs
  url: "https://github.com/org/repo"
  branch: main
  follow_links: true
  files:
    - "docs/**/*.md"
    - "README.md"
    - "*.md"
```

#### Web Pages
```yaml
- type: web
  name: external-docs
  urls:
    - "https://docs.example.com"
  depth: 2
  patterns:
    - "*/docs/*"
    - "*/documentation/*"
  export_format: md
```

### Commands

#### Sync Command
```bash
# Sync all sources from default configuration (knowledge/external/sources.yaml → knowledge/external/)
uv run sidekick knowledge sync

# Sync specific source by name
uv run sidekick knowledge sync --source gdrive

# Use custom configuration file and output directory
uv run sidekick knowledge sync --config my-sources.yaml --base-path knowledge/my-project
```

#### Download Commands
Download specific content without editing the configuration file:

```bash
# Download Google Drive documents
uv run sidekick knowledge download gdrive "https://docs.google.com/document/d/ID/edit" --depth 2

# Download from Git repository
uv run sidekick knowledge download git "https://github.com/org/repo" --branch main --files "docs/**/*.md"

# Download web pages
uv run sidekick knowledge download web "https://example.com/docs" --depth 2
```

#### Reindex Command
Rebuild the vector database for improved search performance:

```bash
# Reindex knowledge base with default paths
uv run sidekick knowledge reindex

# Reindex with custom knowledge directory
uv run sidekick knowledge reindex --knowledge-path ./docs

# Reindex with custom vector database path and table name
uv run sidekick knowledge reindex --vector-db-path ./vectordb --table-name my_docs
```

The reindex command is useful when:
- Documents have been updated or modified outside of the sync process
- Search results seem outdated or incomplete
- The vector database has become corrupted
- You want to rebuild embeddings with updated AI models

### Directory Structure

The knowledge system organizes content by source:
```
knowledge/
├── sources.yaml              # Configuration file
├── sources.yaml.example      # Example configuration
├── external/                 # External sources (synced content)
│   ├── .manifests/           # File tracking (auto-managed)
│   │   ├── gdrive.json
│   │   └── rhdh.json
│   ├── gdrive/               # Google Drive documents
│   │   └── *.md
│   └── rhdh/                 # Git repository files
│       └── docs/
└── product-documentation/    # Static product documentation
    ├── about/
    ├── authentication/
    └── ...
```

### Features

- **Multi-Source Support**: Google Drive, Git repositories, and web pages
- **Automatic Cleanup**: Removes files that are no longer available
- **Format Conversion**: HTML to Markdown conversion for web content
- **Link Following**: Configurable depth for following document links
- **Shallow Git Clones**: Efficient repository downloading
- **Manifest Tracking**: Tracks downloaded files for proper cleanup
- **Organized Storage**: Source-based directory organization
- **AI Search Integration**: All content automatically indexed for search

### Google Drive Setup

For Google Drive sources, you need OAuth2 authentication:

1. **Create Google Cloud Project** and enable Google Drive API
2. **Create OAuth2 Credentials** for a desktop application
3. **Download credentials** and save as `.client_secret.googleusercontent.com.json` in project root
4. **Run sync/download command** - it will open a browser for authorization on first use

See `knowledge/README.md` for detailed setup instructions.

### Legacy Google Drive Commands

The original Google Drive commands are still available for backwards compatibility:

```bash
# List available export formats
uv run sidekick gdrive formats

# Debug access to a specific document
uv run sidekick gdrive debug DOCUMENT_ID

# Export documents directly
uv run sidekick gdrive export DOCUMENT_ID --format pdf
```

## ⚖️ Jira Triager

### Usage

```bash
# Triage a Jira issue by ticket ID (fields auto-fetched)
uv run sidekick jira-triager triage RHIDP-6496

# Triage a Jira issue by manually specifying fields
uv run sidekick jira-triager triage --title "Password reset fails" --description "Reset link returns 500 error."

# Override specific fields when using a ticket ID
uv run sidekick jira-triager triage RHIDP-6496 --component "Authentication" --team ""
```

- The command will recommend the best team and component for the given Jira issue.
- If you provide a Jira issue ID, the tool will automatically fetch the title, description, components, team, and assignee from Jira.
- You can override any field by specifying it as an option.

### How It Works

1. **Fetches Jira issue details** using the provided ticket ID (if given), including summary, description, components, team, and assignee.
2. **Retrieves historical Jira tickets** from the local knowledge base for context.
3. **Uses AI-powered triage** to analyze the current issue in the context of past tickets, considering any existing assignments.
4. **Recommends the most appropriate team and component** for the issue, filling in only missing fields and respecting any already-assigned values.
5. **Outputs the recommended assignment** directly in the CLI.

> The Jira triager leverages Retrieval-Augmented Generation (RAG) and a predefined list of allowed teams and components to ensure recommendations are relevant and actionable.

### Future Improvements
- When making decision, consider current assignee (if there is one) and the team they belong to
- New command to apply changes to the Jira ticket automatically
- Provide better support for RHDHBUGS and RHDHSUPP specific components

## Other Commands

```bash
# Show version
uv run sidekick version

# Show application info
uv run sidekick info
```

### Jira Data Extraction: `load_jira`

The `load_jira` (CLI command: `load-past-jiras`) command fetches and transforms Jira issues from one or more projects and saves them to a single JSON file for downstream analysis or RAG workflows.

**Usage:**

```
uv run sidekick jira load-past-jiras [OPTIONS]
```

**Options:**
- `--projects TEXT`  Comma-separated list of Jira project keys (default: `RHDHSUPP,RHIDP,RHDHBUGS`)
- `--jql-extra TEXT` Extra JQL filter to further restrict issues (e.g., `AND status = "Closed"`)
- `--num-issues INTEGER` Number of issues to return per project (default: 100)

**Behavior:**
- Always applies built-in filters: only issues with `resolution = "Done"`, `resolutiondate >= -180d`, `Team` and `component` present, and excludes doc review issues if filtered in code.
- Combines issues from all specified projects into a single file: `knowledge/rag/jira/sample_jiras.json`
- Temporary files for each project are deleted after merging.

**Example:**

```
uv run sidekick jira load-past-jiras --projects RHIDP,RHDHSUPP --num-issues 50 --jql-extra 'AND status = "Closed"'
```

This will fetch up to 50 closed issues per project from RHIDP and RHDHSUPP, apply all built-in filters, and save the combined results to `knowledge/rag/jira/sample_jiras.json`.

## License

Apache License 2.0 - See [LICENSE](LICENSE) file for details.
