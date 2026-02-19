<p align="center">
  <img src="assets/omnilabs-banner.svg" alt="OmniLabs Banner" width="100%">
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-ffd60a?style=flat-square" alt="MIT License"></a>
  <a href="https://claude.com/claude-code"><img src="https://img.shields.io/badge/Claude_Code-compatible-a855f7?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iMTAiIGZpbGw9Im5vbmUiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIvPjwvc3ZnPg==&logoColor=white&style=flat-square" alt="Claude Code"></a>
  <a href="#agents"><img src="https://img.shields.io/badge/Agents-5_specialized-22c55e?style=flat-square" alt="5 Agents"></a>
  <a href="#agents"><img src="https://img.shields.io/badge/Models-Sonnet_%2B_Opus-3b82f6?style=flat-square" alt="Sonnet + Opus"></a>
  <a href="#"><img src="https://img.shields.io/badge/Language-agnostic-9ca3af?style=flat-square" alt="Language Agnostic"></a>
</p>

<p align="center">
  <strong>Plug-and-play agent teams framework for Claude Code.</strong><br>
  Multi-perspective strategic analysis for any project.<br>
  <sub>Inspired by <a href="https://github.com/EricTechPro/awesome-claude-code-agents">Eric Tech's</a> work on Claude Code sub-agent structures.</sub>
</p>

---

## What It Does

OmniLabs deploys **5 specialized AI agents** that analyze your project from business, financial, technical, and adversarial perspectives — then synthesize everything into a single actionable report with a **GO / NO-GO / CONDITIONAL GO** decision.

- **Code-first** — agents read the actual codebase, not just documentation
- **Evidence-based** — every finding must be traceable to code or data
- **Multi-perspective** — 4 analysts + 1 devil's advocate, converging into synthesis
- **Actionable** — every report includes a clear decision and 30/60/90-day roadmap
- **Language-agnostic** — works with any tech stack, any language, any framework

---

## How It Works

```
         ┌──────────────────────────────────────────────────────────────┐
         │                      YOUR PROJECT                           │
         │                                                             │
         │   🟡 Business    🟢 Financial    🔵 Technical    🔴 Devil's │
         │   Product        Cost            Architecture   Advocate    │
         │   (Sonnet)       (Sonnet)        (Sonnet)       (Sonnet)   │
         │      │              │                │              │       │
         │      │              │                │              │       │
         │      └──────────────┴────────┬───────┴──────────────┘       │
         │                              │                              │
         │                      🟣 Lead Synthesis                      │
         │                          (Opus)                             │
         │                              │                              │
         │                    ┌─────────▼──────────┐                   │
         │                    │  OmniLabs Report   │                   │
         │                    │  GO / NO-GO /      │                   │
         │                    │  CONDITIONAL GO    │                   │
         │                    └────────────────────┘                   │
         └──────────────────────────────────────────────────────────────┘
```

The 4 analyst agents run **in parallel**, reading your actual codebase. The Lead Synthesis agent (powered by **Opus** for deeper reasoning) waits for all analysts to complete, then produces the final report.

---

## Agents

| | Agent | Model | Role |
|---|-------|-------|------|
| 🟡 | `business-product` | Sonnet | Market opportunity, product-market fit, competitive landscape, go-to-market |
| 🟢 | `financial-cost` | Sonnet | Infrastructure costs, TCO modeling, build-vs-buy, ROI projections |
| 🔵 | `technical-architecture` | Sonnet | Architecture scoring across 6 dimensions (scalability, reliability, security, maintainability, observability, operability) |
| 🔴 | `devils-advocate` | Sonnet | Stress-testing, assumption challenging, pre-mortem analysis, blind spot identification |
| 🟣 | `lead-synthesis` | **Opus** | Orchestration, convergence/divergence analysis, final OmniLabs Report |

The 4 analysts use **read-only tools** (Read, Grep, Glob, Bash) for safety. The lead inherits all tools for coordination.

---

## Install

### One-line install

```bash
curl -sL https://raw.githubusercontent.com/Viniciuscarvalho/OmniLabs/main/install.sh | bash
```

### Manual install

```bash
git clone https://github.com/Viniciuscarvalho/OmniLabs.git
cp -r OmniLabs/.claude/ /path/to/your/project/.claude/
```

### Cherry-pick

Copy individual agent files from `.claude/agents/` into your project's `.claude/agents/` directory.

> The installer detects existing `.claude/` directories and merges safely — it won't overwrite your files.

---

## Quick Start

Open Claude Code in your project and paste:

```
Run a full OmniLabs strategic analysis of this project.

Create a team called "omnilabs-analysis" with 5 agents:

1. business-product (Sonnet) — Analyze market opportunity, PMF, competitive landscape, and GTM strategy.
2. financial-cost (Sonnet) — Model infrastructure costs, calculate TCO at different scales, evaluate build-vs-buy, project ROI.
3. technical-architecture (Sonnet) — Evaluate architecture across 6 dimensions, score each 1-10 with evidence from code.
4. devils-advocate (Sonnet) — Stress-test all findings. Challenge assumptions with evidence. Run pre-mortem analysis.
5. lead-synthesis (Opus) — Wait for all 4 analysts, then synthesize the OmniLabs Report with GO/NO-GO decision.

Run analysts 1-4 in parallel. Agent 5 starts only after all 4 complete.
```

See [`agent-team-prompt.md`](agent-team-prompt.md) for the full prompt with all configuration options.

---

## Individual Agent Prompts

For focused deep-dives, each agent has a dedicated prompt file with comprehensive evaluation criteria and structured output expectations:

| | Agent | Prompt File | What It Covers |
|---|-------|-------------|----------------|
| 🟡 | Business & Product | [`business-product-analysis.md`](business-product-analysis.md) | Product definition, market opportunity, PMF signals, competitive landscape, GTM, business model, risks |
| 🟢 | Financial & Cost | [`financial-cost-analysis.md`](financial-cost-analysis.md) | Infrastructure inventory, third-party costs, TCO at 4 scales, unit economics, optimization, runway |
| 🔵 | Technical Architecture | [`technical-architecture-review.md`](technical-architecture-review.md) | 6-dimension scoring: scalability, reliability, maintainability, security, observability, operability |
| 🔴 | Devil's Advocate | [`devil-advocate-challenge.md`](devil-advocate-challenge.md) | Assumption deconstruction, architectural fragility, pre-mortem, competitor counterattack |

Copy the contents of any prompt file and paste it into Claude Code.

---

## The OmniLabs Report

The lead synthesis agent produces a structured executive report:

| Section | Description |
|---------|-------------|
| **Decision** | GO / NO-GO / CONDITIONAL GO with confidence level |
| **Dimension Scores** | Quantitative ratings across all analysis dimensions |
| **Consensus Findings** | Where 3+ analysts agree (high confidence) |
| **Contested Findings** | Where analysts disagree, with evidence from both sides |
| **Blind Spots** | Issues no single analyst fully addressed |
| **Risk Matrix** | Probability x Impact with mitigations |
| **Implementation Roadmap** | 30/60/90-day phased action plan |

---

## Examples

| Scenario | Description |
|----------|-------------|
| [SaaS Product Evaluation](examples/saas-evaluation.md) | Should we launch this B2B analytics platform? |
| [Technical Migration](examples/tech-migration.md) | Should we migrate from Rails monolith to Go microservices? |
| [Market Entry](examples/market-entry.md) | Should we expand from individual devs to enterprise? |

---

## Project Structure

```
OmniLabs/
├── .claude/
│   ├── agents/
│   │   ├── business-product.md          # 🟡 Business & Product Strategy
│   │   ├── financial-cost.md            # 🟢 Financial & Cost Analysis
│   │   ├── technical-architecture.md    # 🔵 Technical Architecture
│   │   ├── devils-advocate.md           # 🔴 Devil's Advocate
│   │   └── lead-synthesis.md            # 🟣 Lead Synthesis (Opus)
│   ├── settings.json
│   └── CLAUDE.md
├── business-product-analysis.md         # Detailed prompt: business
├── financial-cost-analysis.md           # Detailed prompt: financial
├── technical-architecture-review.md     # Detailed prompt: architecture
├── devil-advocate-challenge.md          # Detailed prompt: adversarial
├── agent-team-prompt.md                 # Team orchestration prompt
├── examples/
│   ├── saas-evaluation.md
│   ├── tech-migration.md
│   └── market-entry.md
├── install.sh
├── README.md
└── LICENSE
```

---

## Requirements

- [Claude Code](https://claude.com/claude-code) CLI
- Agent teams support (enabled automatically via `settings.json`)

---

## Contributing

Contributions welcome — new agents, improved frameworks, better prompts. Open an issue or PR.

---

<p align="center">
  <sub>MIT License — see <a href="LICENSE">LICENSE</a></sub>
</p>
