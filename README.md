# sidekick - Modern Python CLI Application

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
[![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A modern Python CLI application with AI-powered search capabilities built with Typer, Rich, and Pydantic.

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
JIRA_USERNAME=your-username
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

## Other Commands

```bash
# Show version
uv run sidekick version

# Show application info
uv run sidekick info
```

## License

Apache License 2.0 - See [LICENSE](LICENSE) file for details.
