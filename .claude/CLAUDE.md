# OmniLabs — Extensible MCP Server for Multi-Perspective Analysis

## What is OmniLabs?

OmniLabs is a YAML-driven MCP server that provides multi-perspective strategic analysis for any project. It auto-discovers agent definitions from YAML files and exposes them as MCP tools that Claude Code orchestrates to analyze your codebase.

## Architecture

- **MCP Server** (`src/omnilabs_mcp/server.py`) — FastMCP-based, exposes tools/resources/prompts
- **Agent Registry** (`src/omnilabs_mcp/agents/registry.py`) — auto-discovers YAML agents from `builtin/` and `~/.omnilabs/agents/`
- **AgentSpec** (`src/omnilabs_mcp/agents/spec.py`) — the contract every agent fulfills
- **Session Store** (`src/omnilabs_mcp/core/store.py`) — in-memory + JSON sync for dashboard
- **Dashboard** (`src/omnilabs_mcp/dashboard/app.py`) — live at `http://localhost:3141`

## Built-in Agents (YAML)

| Agent         | Focus                                          | File                              |
| ------------- | ---------------------------------------------- | --------------------------------- |
| `business`    | Product-market fit, competitive landscape, GTM | `agents/builtin/business.yaml`    |
| `financial`   | Infrastructure costs, TCO, build-vs-buy        | `agents/builtin/financial.yaml`   |
| `technical`   | Architecture quality across 6 dimensions       | `agents/builtin/technical.yaml`   |
| `adversarial` | Stress-testing assumptions, blind spots        | `agents/builtin/adversarial.yaml` |

Claude Code subagents (`.claude/agents/*.md`) are also available for direct subagent invocation.

## How to Use

1. Install: `pip install -e .`
2. Add to Claude Code MCP settings: `"omnilabs": { "command": "omnilabs-mcp" }`
3. Paste: `Analyze this project with OmniLabs`
4. Or run individual agents: `Run just the technical analysis with OmniLabs`

## Adding Agents

- **Personal**: drop a `.yaml` in `~/.omnilabs/agents/` (overrides built-in if same `id`)
- **Contribute**: PR a `.yaml` to `src/omnilabs_mcp/agents/builtin/` (see CONTRIBUTING.md)

## Design Principles

- **Code-first analysis**: Agents read the actual codebase, not just documentation
- **Evidence over opinion**: Every finding must be traceable to code or data
- **Constructive challenge**: The devil's advocate strengthens ideas, doesn't kill them
- **Actionable output**: Every report includes a clear decision and implementation roadmap
- **Language-agnostic**: Works with any tech stack — agents adapt to what they find

## Evaluation Framework

OmniLabs includes evals to validate agent output quality. See `docs/evaluation-guide.md` for details.

- **Code-based graders**: `evaluation/graders/code-based/grade-<agent>.sh` — deterministic structural validation
- **Model-based rubrics**: `evaluation/graders/model-based/rubric-<agent>.md` — LLM-as-Judge quality scoring
- **Tasks**: `evaluation/tasks/<agent>/task-*.md` — test scenarios with expected behaviors
- **Golden datasets**: `evaluation/datasets/golden-*.md` — reference project descriptions
- **Run evals**: `bash evaluation/harness/run-all.sh`
- **Docs**: `docs/architecture.md`, `docs/contributing-evals.md`, `docs/evaluation-guide.md`

## Continuous Learning

OmniLabs includes an optional continuous learning system that captures and retrieves knowledge across sessions. See `docs/continuous-learning.md` for the full guide.

### Knowledge Base Search Protocol

**Before starting any analysis task**, search the knowledge base for relevant prior findings:

1. Use `mcp__docs-mcp-server__search_docs` with library `omnilabs-memories`
2. Search with 2-3 keyword variations related to the current task
3. Review the top results for applicable patterns, decisions, or findings

### Knowledge Capture Protocol

After completing analysis work, evaluate whether reusable knowledge was produced:

- **Analysis patterns**: Recurring approaches to market sizing, cost modeling, architecture scoring
- **Eval findings**: Insights about agent behavior, grader false positives/negatives
- **Agent behavior**: Prompt engineering discoveries, output format nuances
- **Framework decisions**: Architecture choices, convention changes

Use the `continuous-learning` skill to capture memories to `.claude/memories/`.

### Prerequisites

- **Ollama** running locally with `nomic-embed-text` model
- The system degrades gracefully if Ollama is unavailable
