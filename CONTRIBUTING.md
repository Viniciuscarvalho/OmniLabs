# Contributing an Agent to OmniLabs

Adding a new agent is a **single-file PR**. No Python required.

## Step-by-step

### 1. Create a YAML file

Copy the template below and save it as `src/omnilabs_mcp/agents/builtin/your_agent.yaml`:

```yaml
# One-line description of what this agent does
# Your Name — your-github-handle

id: your_agent
name: Your Agent Name
icon: "🎯"
focus: One sentence describing what this agent analyzes
tags: [engineering]
key_outputs:
  - First key deliverable
  - Second key deliverable
  - Third key deliverable

system_prompt: |
  You are a [specialist role] with [relevant expertise].

  Read the entire codebase before forming conclusions.

  Your analysis must cover:

  **Section 1**
  - What to analyze
  - What evidence to look for

  **Section 2**
  - More analysis areas

  **Verdict**
  - Summary score or assessment

  CRITICAL: Every finding must cite specific files and code as evidence.
```

### 2. Required fields

| Field | Rules |
|---|---|
| `id` | Lowercase, alphanumeric with `_` or `-`. Must be unique. |
| `name` | Human-readable, title case. |
| `icon` | Single emoji. |
| `focus` | One sentence, shown in dashboard and catalog. |
| `tags` | At least one tag. Use existing: `core`, `engineering`, `strategy`, `risk`, `compliance`. |
| `key_outputs` | 2-4 concrete deliverables this agent produces. |
| `system_prompt` | The full expert prompt. **Must be >100 chars.** See guidelines below. |

### 3. System prompt guidelines

A good agent prompt:

- **Defines a clear expert persona** — "You are a senior [role] with [specific experience]"
- **Mandates codebase reading** — "Read the entire codebase before..."
- **Has structured sections** — Named analysis areas with bullet points
- **Requires evidence** — Every finding must cite specific files, lines, or patterns
- **Ends with a verdict** — A score, assessment, or decision framework
- **Is detailed enough to be useful** — Minimum 500 words recommended

A bad agent prompt:
- Generic: "Analyze the code and give feedback"
- No evidence requirement: conclusions without file references
- No structure: a wall of text without sections
- Too short: under 100 words won't produce specialist output

### 4. Test your agent locally

Before submitting a PR, test it by dropping the YAML in `~/.omnilabs/agents/`:

```bash
cp your_agent.yaml ~/.omnilabs/agents/
# Restart Claude Code, then:
# > list_agents  (should show your agent)
# > Run my-agent on this repo
```

### 5. Submit your PR

- One file: `src/omnilabs_mcp/agents/builtin/your_agent.yaml`
- PR title: `agent: add [agent name]`
- Description: explain what gap this agent fills

That's it. No Python changes, no registry updates, no enum modifications.

## Overriding built-in agents

To customize a built-in agent's prompt for your local use, create a YAML file with the **same `id`** in `~/.omnilabs/agents/`. User agents override built-in ones.

## Agent ideas we'd love to see

- **Security Audit** — OWASP Top 10, auth review, dependency scanning
- **Accessibility** — WCAG 2.1 compliance, screen reader support
- **Performance** — Bundle size, render performance, database query optimization
- **Developer Experience** — Onboarding friction, documentation quality
- **Compliance** — GDPR, SOC2, HIPAA readiness assessment
- **API Design** — REST/GraphQL best practices, versioning, documentation
- **Data Architecture** — Schema design, migration safety, data integrity
- **Testing Strategy** — Coverage gaps, test quality, missing edge cases
