# Continuous Learning System

The continuous learning system captures knowledge from OmniLabs analysis sessions and makes it retrievable via semantic search in future sessions. It uses local embeddings (Ollama) and a semantic search MCP server (docs-mcp-server) to build a persistent knowledge base.

## Prerequisites

| Dependency | Purpose | Install |
|-----------|---------|---------|
| [Ollama](https://ollama.com) | Local embedding model runtime | `brew install ollama` or download from ollama.com |
| `nomic-embed-text` | Text embedding model | `ollama pull nomic-embed-text` |
| Node.js | Runs docs-mcp-server via npx | `brew install node` or download from nodejs.org |

Start Ollama before using the learning system:

```bash
ollama serve                          # foreground
brew services start ollama            # background (macOS)
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Analysis Session                          │
│                                                             │
│  1. SessionStart hook                                       │
│     └── ollama-status.sh                                    │
│         ├── Check Ollama at localhost:11434                  │
│         ├── Verify nomic-embed-text model                   │
│         └── Sync .claude/memories/ to docs-mcp-server       │
│                                                             │
│  2. Search KB before starting work                          │
│     └── mcp__docs-mcp-server__search_docs                   │
│         └── Semantic search over indexed memories            │
│                                                             │
│  3. Do analysis work                                        │
│     └── PreToolUse hook reminds about knowledge capture     │
│                                                             │
│  4. Capture knowledge                                       │
│     └── continuous-learning skill                           │
│         ├── Evaluate: is this reusable?                     │
│         ├── Search: does it already exist?                  │
│         ├── Structure: use appropriate template             │
│         └── Save: write to .claude/memories/                │
│                                                             │
│  5. Next session starts → memories are indexed → searchable │
└─────────────────────────────────────────────────────────────┘
```

### Component Map

| Component | Type | File | Event |
|-----------|------|------|-------|
| Ollama status hook | SessionStart hook | `.claude/hooks/ollama-status.sh` | On session start |
| Learning activator | PreToolUse hook | `.claude/hooks/continuous-learning-activator.sh` | Before each tool use |
| Continuous learning skill | Skill | `.claude/skills/continuous-learning/SKILL.md` | Invoked by assistant |
| Memory templates | Reference | `.claude/skills/continuous-learning/references/templates.md` | Referenced by skill |
| docs-mcp-server | MCP server | Configured in `settings.json` | Always running |
| Knowledge base | Files | `.claude/memories/*.md` | Read/write by skill |

## Memory Types

### Learnings

Naming: `learning_<topic>_<specific>.md`

Discoveries made through debugging, investigation, or analysis that weren't obvious beforehand.

**When to capture:**
- Solution required significant investigation
- Found a non-obvious pattern in codebase analysis
- Discovered a workaround for an agent or tool limitation
- Evaluation revealed unexpected agent behavior

### Decisions

Naming: `decision_<domain>_<topic>.md`

Deliberate choices about how OmniLabs or the analyzed project should work.

**When to capture:**
- Architecture or methodology choice made
- Convention or standard established
- Scoring calibration adjusted
- User expressed a preference

## Domain Reference

| Domain | Description | Example Filenames |
|--------|-------------|-------------------|
| `analysis` | Strategic analysis patterns and methodologies | `learning_analysis_tam-estimation-saas.md` |
| `evaluation` | Eval framework findings, grader patterns | `learning_evaluation_false-positive-moat.md` |
| `agent` | Agent behavior, prompt engineering insights | `decision_agent_score-range-calibration.md` |
| `framework` | OmniLabs architecture decisions | `decision_framework_hook-registration.md` |
| `tooling` | Tool usage, MCP server behaviors | `learning_tooling_ollama-embedding-limits.md` |
| `debugging` | Debugging techniques, error resolution | `learning_debugging_grader-exit-codes.md` |

## Templates

Four templates are available in `.claude/skills/continuous-learning/references/templates.md`:

1. **Learning Template** — Problem, trigger conditions, solution, verification, example
2. **Decision Template (ADR)** — Decision, context, options, choice, consequences, scope
3. **Analysis Pattern Template** — Pattern, when to apply, example, anti-pattern, scoring impact
4. **Eval Finding Template** — Finding, root cause, resolution, verification, regression risk

## Workflow

### Capturing Knowledge

1. **Evaluate** — After completing a task, ask: "Is this reusable? Would future sessions benefit?"
2. **Search** — Query docs-mcp-server to check if the knowledge already exists
3. **Research** — Gather context; use web search for general topics
4. **Structure** — Choose the right template and fill all required fields
5. **Save** — Write to `.claude/memories/` with proper naming convention

### Retrieving Knowledge

Before starting any analysis task:

```
mcp__docs-mcp-server__search_docs(library: "omnilabs-memories", query: "cost analysis serverless")
```

Try 2-3 keyword variations for broader coverage. Review top results for applicable patterns.

### Retrospective

Invoke `/retrospective` to review the current session and extract the most valuable memories.

## Configuration

The learning system is configured in `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [...],
    "PreToolUse": [...]
  },
  "mcpServers": {
    "docs-mcp-server": {
      "command": "npx",
      "args": ["@arabold/docs-mcp-server@latest", "--read-only", "--telemetry=false"],
      "env": {
        "OPENAI_API_KEY": "ollama",
        "OPENAI_API_BASE": "http://localhost:11434/v1",
        "DOCS_MCP_EMBEDDING_MODEL": "openai:nomic-embed-text"
      }
    }
  }
}
```

The `OPENAI_API_KEY=ollama` trick uses Ollama's OpenAI-compatible endpoint for embeddings.

## Troubleshooting

### Ollama not running

```
Ollama: not running (KB search unavailable)
```

Fix: `ollama serve` (foreground) or `brew services start ollama` (background).

### nomic-embed-text model missing

```
nomic-embed-text: missing
```

Fix: `ollama pull nomic-embed-text`

### docs-mcp-server not connecting

Verify Node.js is installed (`node --version`) and npx is available (`npx --version`). The MCP server is started automatically by Claude Code based on settings.json configuration.

### Memories not being indexed

The ollama-status hook syncs memories on session start. If memories were added mid-session, restart Claude Code or manually trigger a refresh.

## Best Practices

- **Name memories clearly** — Use descriptive, searchable names
- **One insight per file** — Keep memories focused and self-contained
- **Include the "why"** — Document rationale, not just the what
- **Add concrete examples** — Code snippets, analysis excerpts, specific numbers
- **Update, don't duplicate** — Edit existing memories when new info is found
- **Review periodically** — Use `/retrospective` to identify outdated memories
- **Tag consistently** — Use domain prefixes for easy categorization

## Graceful Degradation

If Ollama is not installed or not running, the learning system degrades gracefully:
- Analysis works normally without KB search
- The activator hook still reminds about knowledge capture
- Memories can still be saved as files (just without semantic search)
- Next time Ollama is available, all existing memories will be indexed
