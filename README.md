<p align="center">
  <img src="assets/omnilabs-banner.svg" alt="OmniLabs Banner" width="100%">
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-ffd60a?style=flat-square" alt="MIT License"></a>
  <a href="https://claude.com/claude-code"><img src="https://img.shields.io/badge/Claude_Code-compatible-a855f7?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iMTAiIGZpbGw9Im5vbmUiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIvPjwvc3ZnPg==&logoColor=white&style=flat-square" alt="Claude Code"></a>
  <a href="#built-in-agents"><img src="https://img.shields.io/badge/Agents-4_built--in-22c55e?style=flat-square" alt="4 Built-in Agents"></a>
  <a href="#create-your-own-agent"><img src="https://img.shields.io/badge/Extensible-YAML--driven-3b82f6?style=flat-square" alt="YAML-driven"></a>
  <a href="#"><img src="https://img.shields.io/badge/Language-agnostic-9ca3af?style=flat-square" alt="Language Agnostic"></a>
  <a href="https://github.com/sponsors/Viniciuscarvalho"><img src="https://img.shields.io/badge/Sponsor-%E2%9D%A4-ea4aaa?style=flat-square&logo=github-sponsors&logoColor=white" alt="Sponsor"></a>
</p>

<p align="center">
  <strong>Extensible MCP server for multi-perspective project analysis.</strong><br>
  Add an agent in one YAML file. No Python required.<br>
  <sub>Inspired by <a href="https://github.com/EricTechPro/awesome-claude-code-agents">Eric Tech's</a> work on Claude Code sub-agent structures.</sub>
</p>

---

## What It Does

OmniLabs is an **MCP server** that turns Claude Code into a team of specialized analysts. It ships with 4 built-in agents that analyze your project from business, financial, technical, and adversarial perspectives — then synthesize everything into a single actionable report with a **GO / NO-GO / CONDITIONAL GO** decision.

- **YAML-driven** — each agent is a single `.yaml` file, no code required
- **Extensible** — drop a YAML in `~/.omnilabs/agents/` and it's instantly available
- **Code-first** — agents read the actual codebase, not just documentation
- **Evidence-based** — every finding must be traceable to code or data
- **Live dashboard** — real-time progress at `http://localhost:3141`
- **Language-agnostic** — works with any tech stack, any language, any framework

---

## How It Works

```
         ┌──────────────────────────────────────────────────────────────┐
         │                    CLAUDE CODE + MCP                         │
         │                                                              │
         │   📊 Business    💰 Financial    🔧 Technical    🎯 Adversarial │
         │      │              │                │              │        │
         │      │   (YAML agents auto-discovered by registry)  │        │
         │      │              │                │              │        │
         │      └──────────────┴────────┬───────┴──────────────┘        │
         │                              │                               │
         │                     🟣 Synthesized Report                    │
         │                              │                               │
         │                    ┌─────────▼──────────┐                    │
         │                    │  OmniLabs Report   │                    │
         │                    │  GO / NO-GO /      │                    │
         │                    │  CONDITIONAL GO    │                    │
         │                    └────────────────────┘                    │
         │                                                              │
         │              📡 Live dashboard at :3141                      │
         └──────────────────────────────────────────────────────────────┘
```

OmniLabs runs as an **MCP server** inside Claude Code. When you start an analysis, Claude Code calls the MCP tools to get each agent's specialized prompt, reads your codebase through that lens, saves results, and synthesizes a final report. The live dashboard updates in real-time as agents complete.

---

## Quick Start

### 1. Install

```bash
pip install -e .
```

Or install directly from the repo:

```bash
pip install git+https://github.com/Viniciuscarvalho/OmniLabs.git
```

### 2. Configure Claude Code

Add OmniLabs to your Claude Code MCP settings (`~/.claude/settings.json`):

```json
{
  "mcpServers": {
    "omnilabs": {
      "command": "omnilabs-mcp"
    }
  }
}
```

### 3. Run an analysis

Open Claude Code in any project and paste:

```
Analyze this project with OmniLabs
```

That's it. Claude Code will:

1. Call `start_analysis` to create a session
2. Get each agent's specialized prompt via `get_agent_prompt`
3. Read your codebase through each agent's lens
4. Save results with `save_agent_result`
5. Synthesize a unified report with GO / NO-GO / CONDITIONAL GO
6. Dashboard updates live at `http://localhost:3141`

---

## Built-in Agents

|     | Agent         | Focus                                                    | Key Outputs                                                                            |
| --- | ------------- | -------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| 📊  | `business`    | Product-market fit, competitive landscape, GTM readiness | Viability score, TAM/SAM/SOM, moat assessment, GTM strategy                            |
| 💰  | `financial`   | Infrastructure costs, TCO modeling, build-vs-buy         | Cost projections at 4 scales, unit economics, ROI analysis                             |
| 🔧  | `technical`   | Architecture quality across 6 dimensions                 | Scalability, reliability, security, maintainability, observability, operability scores |
| 🎯  | `adversarial` | Stress-testing assumptions, blind spots                  | Risk heat map, failure scenarios, pre-mortem analysis                                  |

All agents are defined in `src/omnilabs_mcp/agents/builtin/*.yaml` and auto-discovered at startup.

---

## MCP Tools & Resources

### Tools

| Tool                                 | Description                                            |
| ------------------------------------ | ------------------------------------------------------ |
| `start_analysis(repo_path, agents?)` | Start a new analysis session (all agents or a subset)  |
| `get_agent_prompt(agent)`            | Get the specialized system prompt for an agent         |
| `save_agent_result(agent, analysis)` | Save completed analysis from an agent                  |
| `mark_agent_error(agent, error)`     | Mark an agent as failed                                |
| `list_agents(tag?)`                  | List all registered agents, optionally filtered by tag |
| `get_session_status()`               | Check status of all agents in the current session      |
| `get_agent_output(agent)`            | Get full output from a completed agent                 |
| `list_sessions()`                    | List all analysis sessions                             |

### Prompts

| Prompt                                | Description                           |
| ------------------------------------- | ------------------------------------- |
| `full_analysis(repo_path)`            | Run all registered agents             |
| `focused_analysis(repo_path, agents)` | Run specific agents (comma-separated) |
| `quick_health_check(repo_path)`       | Quick technical + adversarial check   |

### Resources

| URI                          | Description                                   |
| ---------------------------- | --------------------------------------------- |
| `omnilabs://agents/catalog`  | Full agent catalog (auto-generated from YAML) |
| `omnilabs://session/current` | Current session state                         |

---

## Create Your Own Agent

Adding an agent is a **single YAML file**. No Python, no registry updates, no code changes.

### Option 1: Personal agent (local only)

Drop a `.yaml` file in `~/.omnilabs/agents/`:

```yaml
id: security
name: Security Audit
icon: "🛡️"
focus: Vulnerability assessment, auth review, OWASP Top 10
tags: [engineering, compliance]
key_outputs:
  - Vulnerability inventory by severity
  - Auth & authorization audit
  - OWASP Top 10 coverage map

system_prompt: |
  You are a senior application security engineer...

  Read the entire codebase. Find vulnerabilities a real attacker would exploit.

  **Authentication & Authorization**
  - How does the app authenticate users?
  - Are there routes accessible without authorization?

  **Verdict**
  - Security posture score (1-10).
  - Top 5 vulnerabilities to fix immediately.

  CRITICAL: Every finding must cite specific files and code as evidence.
```

Restart Claude Code and it's available immediately via `list_agents`.

### Option 2: Contribute to the project (PR)

Save your YAML to `src/omnilabs_mcp/agents/builtin/` and open a PR. See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide.

### Required fields

| Field           | Rules                                                                            |
| --------------- | -------------------------------------------------------------------------------- |
| `id`            | Lowercase, alphanumeric with `_` or `-`. Must be unique.                         |
| `name`          | Human-readable, title case.                                                      |
| `icon`          | Single emoji.                                                                    |
| `focus`         | One sentence — shown in dashboard and catalog.                                   |
| `tags`          | At least one. Existing: `core`, `engineering`, `strategy`, `risk`, `compliance`. |
| `key_outputs`   | 2-4 concrete deliverables.                                                       |
| `system_prompt` | Full expert prompt. **Must be >100 chars.**                                      |

### Override built-in agents

Create a YAML with the **same `id`** in `~/.omnilabs/agents/`. User agents override built-in ones.

### Template

See [`examples/TEMPLATE.yaml`](examples/TEMPLATE.yaml) for a starter template, and [`examples/security.yaml`](examples/security.yaml) for a complete community agent example.

---

## Dashboard

The dashboard runs automatically at `http://localhost:3141` when the MCP server starts. It updates in real-time as agents run.

<p align="center">
  <img src="assets/dashboard-preview.png" alt="OmniLabs Dashboard" width="100%" style="border-radius: 12px;">
</p>

### What it shows

- **Session info** — current repo being analyzed
- **Agent cards** — status (idle → running → completed/failed), duration, focus area, tags
- **Live updates** — polls every 1.5s, no manual refresh needed
- **Agent count** — total registered agents (built-in + custom)

State is stored in `~/.omnilabs/state.json` and agent metadata in `~/.omnilabs/agents.json`.

---

## Running Individual Agents

For a focused deep-dive on one dimension:

```
Run just the technical analysis with OmniLabs on this project
```

Or use the `focused_analysis` prompt:

```
Run OmniLabs focused analysis on ~/my-project with agents: business, adversarial
```

Or the quick health check:

```
Run OmniLabs quick health check on this project
```

---

## Agent Discovery

Agents are auto-discovered from two directories, in order (later overrides earlier):

```
1. src/omnilabs_mcp/agents/builtin/*.yaml   ← ships with OmniLabs
2. ~/.omnilabs/agents/*.yaml                 ← your custom/override agents
```

This means you can:

- **Add** new agents by dropping YAML files in `~/.omnilabs/agents/`
- **Override** built-in agents by using the same `id`
- **Share** agents by contributing to `builtin/` via PR

---

## Project Structure

```
OmniLabs/
├── src/omnilabs_mcp/
│   ├── server.py                     # MCP server — tools, resources, prompts
│   ├── agents/
│   │   ├── spec.py                   # AgentSpec dataclass (the contract)
│   │   ├── registry.py               # Auto-discovery from YAML files
│   │   └── builtin/                  # Built-in agent definitions
│   │       ├── business.yaml         # 📊 Business & Product
│   │       ├── financial.yaml        # 💰 Financial & Cost
│   │       ├── technical.yaml        # 🔧 Technical Architecture
│   │       └── adversarial.yaml      # 🎯 Devil's Advocate
│   ├── core/
│   │   ├── models.py                 # Session & AgentResult models
│   │   └── store.py                  # In-memory session store + JSON sync
│   └── dashboard/
│       └── app.py                    # Live dashboard at :3141
├── examples/
│   ├── TEMPLATE.yaml                 # Starter template for new agents
│   └── security.yaml                 # Example community agent
├── tests/
│   └── test_core.py                  # Core tests
├── .claude/
│   ├── agents/                       # Claude Code subagent definitions
│   │   ├── business-product.md
│   │   ├── financial-cost.md
│   │   ├── technical-architecture.md
│   │   ├── devils-advocate.md
│   │   └── lead-synthesis.md
│   ├── skills/                       # Claude Code skills
│   ├── hooks/                        # Session & tool hooks
│   └── CLAUDE.md
├── evaluation/                       # Agent eval framework
├── docs/                             # Architecture & guides
├── CONTRIBUTING.md                   # How to add an agent (single-file PR)
├── pyproject.toml
├── install.sh
└── LICENSE
```

---

## Evaluation Framework

OmniLabs ships with evals to validate agent output quality. See [docs/evaluation-guide.md](docs/evaluation-guide.md) for the full guide.

```bash
# Run all evaluations
bash evaluation/harness/run-all.sh

# Run for a single agent
bash evaluation/harness/run-all.sh --agent business-product

# Run grader test suite
bash evaluation/tests/test-graders.sh
```

Two layers:

- **Code-based graders** — deterministic bash scripts that validate structure (CI-ready)
- **Model-based rubrics** — LLM-as-Judge scoring across 5 dimensions per agent

---

## Continuous Learning (Optional)

OmniLabs can learn from analysis sessions via a local knowledge base. Requires [Ollama](https://ollama.com) with `nomic-embed-text`. The system degrades gracefully if Ollama is unavailable.

See [docs/continuous-learning.md](docs/continuous-learning.md) for the full guide.

---

## Requirements

- Python 3.11+
- [Claude Code](https://claude.com/claude-code) CLI
- Dependencies: `fastmcp>=2.0.0`, `pydantic>=2.0.0`

---

## Contributing

Adding a new agent is a **single-file PR** — just a YAML file in `src/omnilabs_mcp/agents/builtin/`. No Python changes needed.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the step-by-step guide, prompt guidelines, and agent ideas we'd love to see.

---

## Sponsors

OmniLabs is free and open source. If it saves you time or helps you make better decisions, consider sponsoring to support continued development.

<p align="center">
  <a href="https://github.com/sponsors/Viniciuscarvalho">
    <img src="https://img.shields.io/badge/Sponsor_OmniLabs-%E2%9D%A4-ea4aaa?style=for-the-badge&logo=github-sponsors&logoColor=white" alt="Sponsor OmniLabs">
  </a>
</p>

---

<p align="center">
  <sub>MIT License — see <a href="LICENSE">LICENSE</a></sub>
</p>
