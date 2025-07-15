# RHDH Sidekick: Local Agentic System

## **The Reality Check**

Coding tools like GitHub Copilot, Cursor AI, and Gemini are becoming standard tools that engineers need to learn, similar to how we all had to adopt Google Docs instead of OpenOffice. The differentiator isn't access to AI assistance—it's having AI that understands your specific workflows, tools, and team processes.

We should think of AI as a fellow co-worker: capable of handling busy work and repetitive tasks, but still needing clear guidance and context. Like onboarding a new team member, the AI needs to learn your processes, understand your codebase, and know which tools to use for different situations.

Slack bots seem like an obvious solution for team AI, but they're limiting. They can't access your local development environment, can't run commands on your behalf, and force all interactions through a chat interface that interrupts your flow. We need something that works where engineers actually work: locally, integrated with existing tools, and customizable to individual needs.

## **The Vision: RHDH Sidekick**

RHDH Sidekick is a locally-running agentic system that acts as your personal engineering assistant. It knows your team's processes, has access to your tools (GitHub, Jira, codebase), and can help with daily tasks without requiring you to context-switch to chat interfaces.

### **Core Concept**

Instead of one-size-fits-all chatbots, engineers get personalized AI agents that:

- Run on their laptop (with models hosted as services)
- Have memory and context about their work
- Analyze data and propose actions (execution comes in future iterations)
- Integrate with existing workflows seamlessly

**Security-First Approach**: In the initial iteration, Sidekick focuses on analysis and recommendations rather than execution. It can create and modify local files but will not initiate actions on external systems (GitHub, Jira, Slack) without explicit user approval. Action execution will be added in future iterations once proper security controls are established.

### **Example Use Cases**

**Daily Standup Prep Agent**

```shell
sidekick standup
# Reviews your recent commits, Jira updates, and PRs
# Generates talking points for standup (saves to local file)
# Identifies blockers and suggests next steps
```

**PR Review Assistant**

```shell
sidekick review-prep PR-1234
# Analyzes code changes against team best practices
# Checks for missing tests, documentation updates
# Suggests reviewers based on code ownership
# Generates PR description template (saves locally for copy/paste)
```

**Jira Maintenance Agent**

```shell
sidekick jira-cleanup
# Identifies stale issues assigned to you
# Suggests priority updates based on recent activity
# Finds duplicate or related issues
# Proposes status updates (saves recommendations to local file)
```

**Documentation Helper**

```shell
sidekick doc-update
# Scans recent commits for changes requiring doc updates
# Generates draft documentation from code changes (saves locally)
# Suggests which repositories need documentation PRs
# Proposes improvements to existing docs
```

**Knowledge Retrieval**

```shell
sidekick find "dynamic plugin configuration patterns"
# Searches team documentation, best practices, processes, and codebase
# Provides context-aware answers with sources from internal docs
# Learns from your queries to improve future responses
```

**Dynamic Plugin Configuration Generator**

```shell
sidekick plugin-config --upstream-plugin backstage-plugin-techdocs
# Analyzes upstream Backstage plugin documentation
# Generates RHDH dynamic plugin configuration files
# Creates local templates ready for customization and deployment
# Suggests configuration options based on team best practices
```

**CI/CD Flake Analysis**

```shell
sidekick analyze-flakes --pipeline "rhdh-build" --days 30
# Analyzes CI/CD logs to identify test flakes and infrastructure failures
# Categorizes failures by type (network, timeout, resource, test flake)
# Identifies patterns and recurring issues across builds
# Generates reports with failure trends and suggested remediation steps
```

## **Technical Requirements**

Based on our framework evaluation, the system must support:

### **Local-First Architecture**

- **Agents run locally** on engineer laptops
- **Models as services** (cloud/intranet hosted, but agents are local)
- **No mandatory cloud dependencies** for core functionality
- **Container distribution** for zero-install deployment

### **Personalization & Memory**

- **Individual agent instances** per engineer
- **Persistent memory** about projects, preferences, and context
- **Learning capability** from interactions and feedback
- **Customizable behavior** for different team roles

### **Hackability & Transparency**

- **Easy to modify** agent behavior without framework expertise
- **Inspectable actions** and decision processes
- **Hot reload** for rapid iteration
- **Simple code** without heavy abstractions
- **Clear audit trails** of all agent actions

### **Team Collaboration**

- **Shareable agent definitions** via git repositories
- **Collaborative improvement** of agent capabilities
- **Version control** for agent configurations
- **Easy onboarding** for new team members

### **Tool Integration**

- **GitHub API** for repository operations
- **Jira API** for issue management
- **Local filesystem** access for codebase analysis
- **Team documentation** and best practices repositories
- **CI/CD system logs** for failure analysis
- **MCP (Model Context Protocol)** support for standardized tool access
- **Existing CLI tools** integration without wrappers

### **Framework Language Considerations**

Given that our team's primary coding stack is **TypeScript**, we should consider framework options in both Python and TypeScript:

- **CrewAI (Python)** remains the leading candidate due to its excellent balance of simplicity, local execution, and extensibility
- **TypeScript alternatives** should be evaluated if they offer similar characteristics:
  - Local execution capabilities
  - Simple agent definition patterns
  - Multi-agent coordination
  - Minimal framework overhead
  - Easy hackability and modification
- **Decision criteria**: Framework must meet all core requirements regardless of language
- **Team familiarity**: TypeScript expertise could accelerate development and adoption
- **Ecosystem**: Consider available tool integrations and LLM libraries in each language

## **Why CrewAI Fits**

CrewAI meets our requirements because it:

- **Runs locally** with minimal dependencies
- **Simple agent definition** using Python classes
- **Multi-agent coordination** for complex workflows
- **Flexible tool integration** without heavy abstractions
- **Easy to hack** and modify without framework lock-in
- **Supports external APIs** directly without proprietary wrappers

## **Implementation Plan**

**Phase 1: Core Framework (4 weeks)**

- Set up CrewAI-based local agent system
- Create container distribution mechanism
- Implement basic GitHub/Jira integration
- Build simple CLI interface

**Phase 2: Essential Agents (8 weeks)**

- Daily standup prep agent
- PR review assistant
- Jira maintenance agent
- Basic documentation helper
- Dynamic plugin configuration generator
- CI/CD flake analysis agent

**Phase 3: Team Deployment (2 weeks)**

- Package agents for team distribution
- Create onboarding documentation
- Gather feedback and iterate

## **Success Metrics**

- **Agent creation time**: New agent in \< 2 hours
- **Daily usage**: Team members use agents for routine tasks
- **Modification frequency**: Engineers customize agents monthly
- **Team sharing**: Agent improvements contributed by multiple team members
- **Workflow integration**: Agents become part of standard development process

## **Next Steps**

1. Prototype basic RHDH Sidekick using CrewAI
2. Build one concrete agent (standup prep) as proof of concept
3. Test with small group of volunteers
4. Refine based on feedback and expand to full team

The goal isn't to replace human judgment but to eliminate the repetitive information gathering and formatting tasks that slow down our development workflow. Engineers should spend time on engineering, not hunting through Jira and GitHub for status updates.
