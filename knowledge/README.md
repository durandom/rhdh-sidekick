# Knowledge Base

This directory contains the unified knowledge management system for the sidekick project. It supports automatic synchronization from multiple sources including Google Drive, Git repositories, and web pages.

## Quick Start

1. **Edit the default configuration**:
   ```bash
   # Default configuration is at knowledge/external/sources.yaml
   nano sources.yaml
   ```

2. **Sync all sources**:
   ```bash
   # Uses knowledge/external/sources.yaml and outputs to knowledge/external/ by default
   uv run sidekick knowledge sync
   ```

3. **For custom projects**, create your own configuration:
   ```bash
   # Copy example to new location
   cp sources.yaml.example my-project/sources.yaml

   # Sync with custom paths
   uv run sidekick knowledge sync --config my-project/sources.yaml --base-path knowledge/my-project
   ```

## Directory Structure

```
knowledge/
├── sources.yaml.example      # Example configuration
├── external/                 # External sources (synced content)
│   ├── .manifests/           # File tracking manifests (auto-managed)
│   ├── sources.yaml              # Configuration file
│   │   ├── gdrive.json
│   │   └── rhdh.json
│   ├── rhdh/                 # RHDH team documentation from Google Drive
│   │   └── gdrive/
│   │       └── *.md
│   └── other-sources/        # Other configured sources
└── my-project/               # Example custom knowledge base
    ├── sources.yaml          # Custom configuration
    ├── .manifests/
    └── ...
```

## Configuration File Format

The `sources.yaml` file defines all knowledge sources:

```yaml
sources:
  # Google Drive documents
  - type: gdrive
    name: gdrive
    export_format: md
    documents:
      - url: "https://docs.google.com/document/d/ID/edit"
        depth: 2
        comment: "Documentation with link following"

  # Git repositories
  - type: git
    name: rhdh
    url: "https://github.com/janus-idp/backstage-showcase"
    branch: main
    follow_links: true
    files:
      - "docs/**/*.md"
      - "README.md"

  # Web pages
  - type: web
    name: external-docs
    urls:
      - "https://docs.redhat.com/en/documentation/red_hat_developer_hub"
    depth: 2
    patterns:
      - "*/documentation/*"
    export_format: md
```

## Source Types

### Google Drive (`gdrive`)
- **Purpose**: Sync Google Docs and Sheets
- **Authentication**: OAuth2 (browser-based auth on first use)
- **Features**: Link following, multiple export formats
- **Output**: Markdown or other formats

### Git Repositories (`git`)
- **Purpose**: Clone and extract files from Git repositories
- **Method**: Shallow clone for efficiency
- **Features**: File pattern matching, symlink handling
- **Output**: Files copied as-is to destination

### Web Pages (`web`)
- **Purpose**: Download and convert web pages
- **Method**: HTTP requests with HTML to Markdown conversion
- **Features**: Crawling with depth limits, pattern filtering
- **Output**: Markdown files

## Commands

### Sync All Sources
```bash
# Sync using defaults (knowledge/external/sources.yaml → knowledge/external/)
uv run sidekick knowledge sync

# Sync specific source
uv run sidekick knowledge sync --source gdrive

# Use custom config and output path
uv run sidekick knowledge sync --config my-sources.yaml --base-path knowledge/custom
```

### Download Individual Items
```bash
# Download Google Drive document
uv run sidekick knowledge download gdrive "https://docs.google.com/document/d/ID/edit"

# Clone Git repository
uv run sidekick knowledge download git "https://github.com/org/repo" --files "docs/**/*.md"

# Download web page
uv run sidekick knowledge download web "https://example.com/docs" --depth 2
```

## File Management

### Manifest System
- Each source gets a manifest file in `.manifests/`
- Tracks all downloaded files for cleanup
- Removes files that are no longer available during sync
- JSON format with timestamps and file lists

### Directory Organization
- Each source gets its own directory named after the `name` field
- Files maintain their relative path structure when possible
- No conflicts between sources due to isolation

## Integration with Search

All synced content is automatically available for the AI-powered search:

```bash
# Search across all knowledge sources
uv run sidekick search "How to configure authentication"
```

The search system indexes all markdown and text files in the knowledge directory structure.

## Google Drive Authentication Setup

To use Google Drive sources, you need to set up OAuth2 authentication:

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name your project (e.g., "Sidekick Knowledge Sync")
4. Click "Create"

### 2. Enable Google Drive API

1. In your project dashboard, go to "APIs & Services" → "Library"
2. Search for "Google Drive API"
3. Click on it and press "Enable"

### 3. Create OAuth2 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - Choose "External" (unless you have a Google Workspace)
   - Fill in required fields (app name, user support email)
   - Add your email to test users
   - Save and continue through all steps
4. Back in "Create OAuth client ID":
   - Application type: "Desktop app"
   - Name: "Sidekick CLI" (or any name you prefer)
   - Click "Create"

### 4. Download and Install Credentials

1. After creation, click the download button (⬇️) next to your OAuth client
2. Save the file as `.client_secret.googleusercontent.com.json` in your project root:
   ```bash
   mv ~/Downloads/client_secret_*.json .client_secret.googleusercontent.com.json
   ```

### 5. First-Time Authentication

When you run your first sync or download command:
1. A browser window will open automatically
2. Log in with your Google account
3. Grant the requested permissions
4. The authentication token will be saved to `tmp/token_drive.json`
5. Future runs will use this token automatically

### Security Notes

- **NEVER commit** `.client_secret.googleusercontent.com.json` to version control
- The token file (`tmp/token_drive.json`) is also sensitive - keep it private
- Both files are in `.gitignore` to prevent accidental commits
- Tokens expire but will auto-refresh when needed

## RHDH Knowledge Submodule

The `rhdh/` directory is a git submodule that points to the external RHDH knowledge repository:
- Repository: `git@gitlab.cee.redhat.com:mhild/rhdh-knowledge.git`
- Purpose: Provides access to RHDH documentation and knowledge base

### Working with the Submodule

#### Initial Setup (for new clones)
When someone clones this repository, they need to initialize and update submodules:

```bash
# Initialize and update all submodules
git submodule init
git submodule update

# Or in one command
git submodule update --init --recursive

# Or clone with submodules from the start
git clone --recursive <this-repo-url>
```

#### Updating the Submodule
To pull the latest changes from the RHDH knowledge repository:

```bash
# Navigate to the submodule directory
cd knowledge/external

# Pull the latest changes
git pull origin main

# Go back to the main repository
cd ../..

# Commit the submodule update
git add knowledge/external
git commit -m "Update RHDH knowledge submodule"
```

#### Checking Submodule Status
```bash
# Check submodule status
git submodule status

# Show submodule information
git submodule foreach git status
```

#### Working with Submodule Changes
```bash
# If you make changes in the submodule directory
cd knowledge/external
# Make your changes and commit them
git add .
git commit -m "Update RHDH knowledge"
git push origin main

# Return to main repo and update the reference
cd ../..
git add knowledge/external
git commit -m "Update RHDH knowledge submodule reference"
```

### Common Issues and Solutions

#### Submodule appears as modified but no changes
This usually means the submodule is pointing to a different commit:
```bash
cd knowledge/external
git checkout main
git pull origin main
cd ../..
git add knowledge/external
git commit -m "Sync RHDH submodule to latest"
```

#### Submodule directory is empty
```bash
git submodule update --init knowledge/external
```

#### Remove submodule (if needed)
```bash
# Remove from .gitmodules
git config -f .gitmodules --remove-section submodule.knowledge/external

# Remove from .git/config
git config --remove-section submodule.knowledge/external

# Remove the directory
git rm --cached knowledge/external
rm -rf knowledge/external

# Commit the changes
git add .gitmodules
git commit -m "Remove RHDH knowledge submodule"
```

## Best Practices

1. **Always commit submodule updates**: When the submodule is updated, commit the new reference in the main repository
2. **Use specific commits**: Submodules track specific commits, not branches, for reproducible builds
3. **Document dependencies**: Make sure team members know about submodule requirements
4. **Automate updates**: Consider using CI/CD to keep submodules updated
5. **Check submodule status**: Regularly check `git submodule status` to ensure consistency
