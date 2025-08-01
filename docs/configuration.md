# Configuration Guide

This guide covers all configuration options for RHDH Sidekick, including environment variables, settings management, and runtime configuration.

## Overview

RHDH Sidekick uses a hierarchical configuration system:

1. **Default values** in `settings.py`
2. **Environment variables** override defaults
3. **CLI arguments** override environment variables
4. **Runtime configuration** for dynamic settings

## Environment Variables

### Core Configuration

```bash
# Logging Configuration
LOG_LEVEL=INFO              # Logging level: TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=logs/sidekick.log  # Log file path (optional)
LOG_FORMAT=pretty           # Log format: pretty (colored) or json

# Legacy format (still supported)
LOGGING__LEVEL=DEBUG
LOGGING__FILE=logs/app.log
LOGGING__FORMAT=json

# Debug Mode
AGNO_DEBUG=true            # Enable Agno framework debugging
```

### API Credentials

```bash
# Jira Integration (required for Jira features)
JIRA_SERVER_URL=https://your-instance.atlassian.net
JIRA_TOKEN=your-jira-api-token
JIRA_PERSONAL_TOKEN=your-jira-api-token  # Alternative name

# GitHub Integration (required for GitHub features)
GITHUB_ACCESS_TOKEN=your-github-personal-access-token

# Google Cloud (required for test analysis)
GOOGLE_API_KEY=your-google-api-key

# Google Drive (required for knowledge sync from Google Drive)
# Note: OAuth credentials file required separately
```

### Optional Services

```bash
# Langfuse Tracing (optional)
LANGFUSE_PUBLIC_KEY=your-public-key
LANGFUSE_SECRET_KEY=your-secret-key
LANGFUSE_HOST=https://your-langfuse-instance.com

# OpenTelemetry (set automatically by Langfuse)
OTEL_EXPORTER_OTLP_ENDPOINT=https://langfuse.com/api/public/otel
OTEL_EXPORTER_OTLP_HEADERS=Authorization=Basic <encoded>
```

### User Configuration

```bash
# User ID for memory persistence
USER=your-username  # Automatically used if --user-id not provided
```

## Settings Management

### Settings Structure

The main settings are defined in `src/sidekick/settings.py`:

```python
from pydantic import BaseSettings, Field
from pathlib import Path
from typing import Literal

class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = Field(default="INFO")
    format: Literal["pretty", "json"] = Field(default="pretty")
    file: Path | None = Field(default=None)
    trace_enabled: bool = Field(default=True)
    pytest_mode: bool = Field(default=False)

class Settings(BaseSettings):
    """Application settings."""

    # Logging
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    log_level: str = Field(default="INFO")
    log_file: Path | None = Field(default=None)
    log_format: Literal["pretty", "json"] = Field(default="pretty")

    # API Configuration
    api_timeout: int = Field(default=30)
    api_retry_count: int = Field(default=3)

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"

settings = Settings()
```

### Loading Order

1. **Default values** from field definitions
2. **`.env` file** in project root (if exists)
3. **Environment variables** with automatic parsing
4. **CLI arguments** override everything

### Nested Configuration

Use `__` delimiter for nested settings:

```bash
# Sets settings.logging.level = "DEBUG"
LOGGING__LEVEL=DEBUG

# Sets settings.logging.format = "json"
LOGGING__FORMAT=json
```

## CLI Configuration

### Global Options

```bash
# Verbose logging
sidekick -v <command>     # DEBUG level
sidekick -vv <command>    # TRACE level

# Explicit log level
sidekick --log-level=DEBUG <command>

# Log to file
sidekick --log-file=debug.log <command>

# Log format
sidekick --log-format=json <command>

# Disable streaming
sidekick --no-streaming <command>

# User ID
sidekick --user-id=alice <command>

# Enable Langfuse
sidekick --langfuse <command>
```

### Command-Specific Options

#### Chat Commands

```bash
# Jira chat with custom options
sidekick chat jira --help

# GitHub chat with repository
sidekick chat github --repo owner/repo

# Search with custom knowledge path
sidekick chat search --knowledge-path ./my-docs

# Team chat with repository
sidekick chat team --repo owner/repo
```

#### Knowledge Commands

```bash
# Sync with custom configuration
sidekick knowledge sync --config my-sources.yaml --base-path ./my-knowledge

# Download with specific format
sidekick knowledge download gdrive <url> --format pdf --depth 2

# Reindex with custom paths
sidekick knowledge reindex --knowledge-path ./docs --vector-db-path ./vectors
```

## Configuration Files

### .env File

Create a `.env` file in the project root:

```bash
# .env
LOG_LEVEL=DEBUG
LOG_FILE=logs/debug.log

JIRA_SERVER_URL=https://mycompany.atlassian.net
JIRA_TOKEN=abc123...

GITHUB_ACCESS_TOKEN=ghp_...

GOOGLE_API_KEY=AIza...
```

### Knowledge Sources Configuration

Create `knowledge/external/sources.yaml`:

```yaml
sources:
  - type: gdrive
    name: team-docs
    export_format: md
    documents:
      - url: "https://docs.google.com/document/d/ID/edit"
        depth: 2
        comment: "Team documentation"

  - type: git
    name: project-docs
    url: "https://github.com/org/repo"
    branch: main
    files:
      - "docs/**/*.md"
      - "README.md"

  - type: web
    name: external-docs
    urls:
      - "https://docs.example.com"
    depth: 2
    patterns:
      - "*/documentation/*"
```

### Google Drive Credentials

For Google Drive integration:

1. Download OAuth credentials from Google Cloud Console
2. Save as `.client_secret.googleusercontent.com.json` in project root
3. First run will open browser for authentication
4. Token saved to `tmp/token_drive.json`

## Runtime Configuration

### Memory Configuration

Memory is configured per user:

```python
# In src/sidekick/memory_config.py
def get_memory_config(user_id: str) -> MemoryConfiguration:
    return MemoryConfiguration(
        llm=llm,
        knowledge=KnowledgeConfiguration(
            data_path=Path(f"tmp/memory/{user_id}/data"),
            vector_path=Path(f"tmp/memory/{user_id}/vectors"),
        ),
        enabled=True,
        instructions_agent=None,  # Use agent's own instructions
    )
```

### Agent-Specific Configuration

Each agent can have specific configuration:

```python
# JiraAgent configuration
jira_agent = JiraAgent(
    storage_path=Path("tmp/jira.db"),
    workspace_dir=Path("tmp/jira_workspace"),
    read_only=False,  # Enable write access
)

# SearchAgent configuration
search_agent = SearchAgent(
    knowledge_path=Path("knowledge/external"),
    vector_db_path=Path("tmp/vectors"),
    session_id="unique-session-123",
)
```

### Storage Configuration

Agents use SQLite for storage:

```python
# Storage path structure
tmp/
├── sidekick.db          # Default storage
├── jira_agent.db        # Jira agent storage
├── search_agent.db      # Search agent storage
└── release_manager.db   # Release manager storage
```

## Advanced Configuration

### Custom Prompt Variables

Agents can use custom variables in prompts:

```yaml
# In prompt template
variables:
  max_results: 10
  include_details: true

# Override in code
agent_factory = MyAgent(
    prompt_variables={
        "max_results": 20,
        "include_details": false
    }
)
```

### Tool Configuration

Configure tools with specific options:

```python
# Google Drive tools
gdrive_tools = GoogleDriveTools(
    workspace_dir=Path("./downloads"),
    credentials_path=Path(".client_secret.json"),
    export_formats={
        "document": "md",  # Markdown for docs
        "spreadsheet": "csv",  # CSV for sheets
    }
)

# State management
state_tools = StateManagementToolkit(
    namespace="my_agent",
    persistent=True,
    storage_path=Path("tmp/state.db")
)
```

### Model Configuration

Configure AI models:

```python
from agno.models.google import Gemini

# Default Gemini configuration
model = Gemini()  # Uses gemini-2.0-flash-exp

# Custom model
model = Gemini(
    id="gemini-1.5-pro",
    temperature=0.7,
    max_tokens=4096,
)
```

## Security Best Practices

### 1. Never Commit Secrets

Add to `.gitignore`:
```
.env
.env.local
*.client_secret*.json
tmp/token*.json
```

### 2. Use Least Privilege

```bash
# Read-only Jira access
JIRA_READ_ONLY=true

# Minimal GitHub scopes
GITHUB_ACCESS_TOKEN=ghp_...  # Only 'repo' scope
```

### 3. Rotate Credentials

Regularly update:
- API tokens
- OAuth credentials
- Service account keys

### 4. Validate Configuration

```python
# In your agent
def validate_config(self):
    """Validate required configuration."""
    if not os.getenv("JIRA_SERVER_URL"):
        raise ValueError("JIRA_SERVER_URL not configured")

    if not self.workspace_dir.exists():
        self.workspace_dir.mkdir(parents=True)
```

## Troubleshooting

### Common Issues

1. **Missing environment variables**
   ```bash
   # Check current environment
   env | grep -E "(JIRA|GITHUB|GOOGLE)"

   # Source .env file
   source .env
   ```

2. **Invalid configuration**
   ```bash
   # Validate settings
   uv run python -c "from sidekick.settings import settings; print(settings.dict())"
   ```

3. **Permission errors**
   ```bash
   # Check file permissions
   ls -la .env
   chmod 600 .env  # Restrict to owner only
   ```

4. **Conflicting settings**
   ```bash
   # CLI takes precedence
   LOG_LEVEL=INFO sidekick -vv chat search
   # Result: TRACE level (CLI wins)
   ```

### Debug Configuration

```bash
# Enable all debugging
export AGNO_DEBUG=true
export LOG_LEVEL=TRACE
export LOG_FILE=debug.log

# Run with maximum verbosity
uv run sidekick -vv --log-format=json chat jira
```

### Configuration Validation Script

Create `scripts/validate_config.py`:

```python
#!/usr/bin/env python
"""Validate sidekick configuration."""

import os
import sys
from pathlib import Path

def check_env_var(name: str, required: bool = True) -> bool:
    """Check if environment variable is set."""
    value = os.getenv(name)
    if value:
        print(f"✓ {name} is set")
        return True
    elif required:
        print(f"✗ {name} is NOT set (required)")
        return False
    else:
        print(f"- {name} is not set (optional)")
        return True

def main():
    """Run configuration validation."""
    print("Validating RHDH Sidekick Configuration\n")

    all_good = True

    # Required variables
    print("Required Environment Variables:")
    all_good &= check_env_var("JIRA_SERVER_URL")
    all_good &= check_env_var("JIRA_TOKEN") or check_env_var("JIRA_PERSONAL_TOKEN")
    all_good &= check_env_var("GITHUB_ACCESS_TOKEN")
    all_good &= check_env_var("GOOGLE_API_KEY")

    print("\nOptional Environment Variables:")
    check_env_var("LOG_LEVEL", required=False)
    check_env_var("LOG_FILE", required=False)
    check_env_var("LANGFUSE_PUBLIC_KEY", required=False)

    print("\nConfiguration Files:")
    if Path(".env").exists():
        print("✓ .env file exists")
    else:
        print("- .env file not found (optional)")

    if Path(".client_secret.googleusercontent.com.json").exists():
        print("✓ Google credentials file exists")
    else:
        print("- Google credentials file not found (required for Google Drive)")

    if not all_good:
        print("\n❌ Configuration validation failed!")
        sys.exit(1)
    else:
        print("\n✅ Configuration validation passed!")

if __name__ == "__main__":
    main()
```

Run validation:
```bash
uv run python scripts/validate_config.py
```

This configuration system provides flexibility while maintaining security and ease of use. Always validate your configuration before running agents in production environments.
