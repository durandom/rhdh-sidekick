# Sidekick Prompt Template System

This directory contains the LangChain-based prompt template system for Sidekick agents. The system allows for easy customization and management of agent instructions through YAML/JSON files.

## Directory Structure

```
prompts/
├── __init__.py          # Package exports
├── base.py              # Base prompt template classes
├── loaders.py          # Template loading utilities
├── registry.py         # Template registry for management
├── README.md           # This file
└── templates/          # Template files
    ├── agents/         # Agent-specific templates
    │   ├── search.yaml
    │   ├── jira.yaml
    │   └── ...
    └── shared/         # Shared template components
        └── common_instructions.yaml
```

## Quick Start

### 1. Using Templates in Agents

Agents can use templates by overriding `get_agent_instructions()`:

```python
def get_agent_instructions(self) -> list[str]:
    """Get instructions from prompt template."""
    return self.get_agent_instructions_from_template(
        # Pass any template variables here
        knowledge_base_name="My Knowledge Base",
        max_iterations=5
    )
```

### 2. Creating a New Template

Create a YAML file in `templates/agents/my_agent.yaml`:

```yaml
name: my_agent
version: "1.0"
description: "My custom agent template"

# Define default variables
variables:
  model_name: "gpt-4"
  temperature: 0.7

# Include shared instructions
includes:
  - shared/common_instructions.yaml

# Main template content with variable substitution
template: |
  You are an AI assistant using {model_name} with temperature {temperature}.

  YOUR RESPONSIBILITIES:
  - Provide helpful responses
  - Follow user instructions carefully
  - Ask for clarification when needed
```

### 3. Variable Substitution

Templates support LangChain-style variable substitution:

```yaml
template: |
  Welcome to {app_name}!
  Current environment: {environment}
  API endpoint: {api_url}
```

Use in code:
```python
instructions = template.format(
    app_name="Sidekick",
    environment="production",
    api_url="https://api.example.com"
)
```

### 4. Template Composition

Templates can include other templates:

```yaml
includes:
  - shared/common_instructions.yaml
  - shared/security_guidelines.yaml

template: |
  Additional agent-specific instructions here...
```

### 5. Loading Templates Programmatically

```python
from sidekick.prompts import get_prompt_registry

# Get template from registry
registry = get_prompt_registry()
template = registry.get("agents.search")

# Format with variables
instructions = template.format(knowledge_base="docs")

# Or load directly from file
from sidekick.prompts.loaders import load_prompt_template
template = load_prompt_template("path/to/template.yaml")
```

## Advanced Features

### Dynamic Templates

Create templates programmatically:

```python
from sidekick.prompts import BasePromptTemplate, PromptConfig

config = PromptConfig(
    name="dynamic_agent",
    variables={"mode": "advanced"}
)

template = BasePromptTemplate(
    config=config,
    template_content="Dynamic content with {mode} mode"
)
```

### Partial Templates

Pre-fill some variables:

```python
# Create partial with defaults
partial = template.partial(
    api_key="default-key",
    region="us-east-1"
)

# Later, provide remaining variables
final = partial.format(user_id="12345")
```

### Template Merging

Combine multiple templates:

```python
base_template = registry.get("agents.base")
search_template = registry.get("agents.search")

combined = base_template.merge_with(search_template)
```

## Best Practices

1. **Use YAML for templates**: More readable than JSON for multi-line content
2. **Leverage includes**: Share common instructions across agents
3. **Document variables**: List all variables in the template file
4. **Version templates**: Use version field for tracking changes
5. **Test templates**: Validate variable substitution before deployment

## Environment Variables

The prompt system respects these environment variables:

- `SIDEKICK_PROMPTS_DIR`: Override default templates directory
- `SIDEKICK_PROMPTS_RELOAD`: Set to "true" to reload templates on each access

## Extending the System

To add new features:

1. Extend `BasePromptTemplate` for custom behavior
2. Create custom loaders by extending `PromptLoader`
3. Add new template formats by implementing loader classes

## Examples

See `examples/prompt_templates_demo.py` for comprehensive examples of:
- Basic template usage
- Variable substitution
- Template composition
- Dynamic template creation
- Partial application

## Migration from Hardcoded Instructions

To migrate an agent from hardcoded instructions:

1. Extract instructions to a YAML template
2. Replace `get_agent_instructions()` to use `get_agent_instructions_from_template()`
3. Test that instructions are loaded correctly
4. Remove hardcoded instruction strings

The system maintains backward compatibility - agents without templates will use their hardcoded instructions.
