# Knowledge Base

This directory contains knowledge bases and documentation for the sidekick project.

## Structure

- `rag/rhdh/` - Local RHDH documentation for RAG processing
- `rhdh/` - Git submodule pointing to external RHDH knowledge repository
- `team-docs/` - Internal team documentation

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
cd knowledge/rhdh

# Pull the latest changes
git pull origin main

# Go back to the main repository
cd ../..

# Commit the submodule update
git add knowledge/rhdh
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
cd knowledge/rhdh
# Make your changes and commit them
git add .
git commit -m "Update RHDH knowledge"
git push origin main

# Return to main repo and update the reference
cd ../..
git add knowledge/rhdh
git commit -m "Update RHDH knowledge submodule reference"
```

### Common Issues and Solutions

#### Submodule appears as modified but no changes
This usually means the submodule is pointing to a different commit:
```bash
cd knowledge/rhdh
git checkout main
git pull origin main
cd ../..
git add knowledge/rhdh
git commit -m "Sync RHDH submodule to latest"
```

#### Submodule directory is empty
```bash
git submodule update --init knowledge/rhdh
```

#### Remove submodule (if needed)
```bash
# Remove from .gitmodules
git config -f .gitmodules --remove-section submodule.knowledge/rhdh

# Remove from .git/config
git config --remove-section submodule.knowledge/rhdh

# Remove the directory
git rm --cached knowledge/rhdh
rm -rf knowledge/rhdh

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
