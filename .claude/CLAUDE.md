# OmniLabs — Extensible MCP Server for Multi-Perspective Analysis

## What is OmniLabs?

OmniLabs is a YAML-driven MCP server that provides multi-perspective strategic analysis for any project. It auto-discovers agent definitions from YAML files and exposes them as MCP tools that Claude Code orchestrates to analyze your codebase.

## Architecture

- **MCP Server** (`src/omnilabs_mcp/server.py`) — FastMCP-based, 3-gate control flow (Discover → Plan → Execute)
- **Agent Registry** (`src/omnilabs_mcp/agents/registry.py`) — auto-discovers YAML agents from `builtin/` and `~/.omnilabs/agents/`
- **AgentSpec** (`src/omnilabs_mcp/agents/spec.py`) — the contract every agent fulfills, includes token cost estimation
- **Session Store** (`src/omnilabs_mcp/core/store.py`) — in-memory + JSON sync for dashboard
- **Dashboard** (`src/omnilabs_mcp/dashboard/app.py`) — live at `http://localhost:3141`, shows cost tier badges

## 3-Gate Control Flow

Nothing runs by default. You choose which agents to execute:

1. **Discover** — `list_agents()`, `recommend_agents(task)`, `list_presets()` to browse what's available
2. **Plan** — `plan_analysis(repo, agents=[...])` to preview token cost before committing
3. **Execute** — `start_analysis()` then `run_agent()` one at a time

## Built-in Agents (4 core)

| Agent         | Focus                                          | File                              |
| ------------- | ---------------------------------------------- | --------------------------------- |
| `business`    | Product-market fit, competitive landscape, GTM | `agents/builtin/business.yaml`    |
| `financial`   | Infrastructure costs, TCO, build-vs-buy        | `agents/builtin/financial.yaml`   |
| `technical`   | Architecture quality across 6 dimensions       | `agents/builtin/technical.yaml`   |
| `adversarial` | Stress-testing assumptions, blind spots        | `agents/builtin/adversarial.yaml` |

## Marketing Agents (13 via conversion)

Convert from markdown source with: `python scripts/convert_agents.py ~/marketing-agent ~/.omnilabs/agents/`

Agents: seo-strategist, content-strategist, copywriter, social-media-manager, community-manager, product-marketing-manager, gtm-strategist, email-marketing-specialist, lifecycle-marketing-manager, marketing-analyst, cro-specialist, pr-strategist, communications-manager

## Presets

| Preset          | Agents                                                          |
| --------------- | --------------------------------------------------------------- |
| `core`          | business, financial, technical, adversarial                     |
| `health-check`  | technical, adversarial                                          |
| `due-diligence` | business, financial, adversarial                                |
| `marketing`     | All agents tagged "marketing"                                   |
| `gtm`           | business, gtm-strategist, product-marketing-manager, copywriter |

Claude Code subagents (`.claude/agents/*.md`) are also available for direct subagent invocation.

## How to Use

1. Install: `pip install -e .`
2. Add to Claude Code MCP settings: `"omnilabs": { "command": "omnilabs-mcp" }`
3. Browse agents: `list_agents()` or `recommend_agents("improve SEO")`
4. Preview cost: `plan_analysis(repo, agents=["technical"])` or `plan_analysis(repo, preset="core")`
5. Execute: `start_analysis(repo, agents=[...])` then `run_agent("technical")`

## Adding Agents

- **Personal**: drop a `.yaml` in `~/.omnilabs/agents/` (overrides built-in if same `id`)
- **Convert from markdown**: `python scripts/convert_agents.py <source_dir> [target_dir]`
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
