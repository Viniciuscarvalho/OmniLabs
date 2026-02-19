# OmniLabs

**Plug-and-play agent teams framework for Claude Code** — multi-perspective strategic analysis for any project.

OmniLabs deploys 5 specialized AI agents that analyze your project from business, financial, technical, and adversarial perspectives, then synthesize everything into a single actionable report with a GO / NO-GO / CONDITIONAL GO decision.

Inspired by [Eric Tech's](https://github.com/EricTechPro/awesome-claude-code-agents) work on Claude Code sub-agent structures.

---

## How It Works

```
┌─────────────────────────────────────────────────────┐
│                   Your Project                       │
│                                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │ Business │ │Financial │ │Technical │ │Devil's │ │
│  │ Product  │ │  Cost    │ │  Arch    │ │Advocate│ │
│  │ (Sonnet) │ │ (Sonnet) │ │ (Sonnet) │ │(Sonnet)│ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └───┬────┘ │
│       │             │            │            │      │
│       └─────────────┴────────────┴────────────┘      │
│                         │                            │
│                ┌────────▼────────┐                   │
│                │ Lead Synthesis  │                   │
│                │    (Opus)       │                   │
│                └────────┬────────┘                   │
│                         │                            │
│                ┌────────▼────────┐                   │
│                │ OmniLabs Report │                   │
│                │ GO / NO-GO /    │                   │
│                │ CONDITIONAL GO  │                   │
│                └─────────────────┘                   │
└─────────────────────────────────────────────────────┘
```

The 4 analyst agents run **in parallel**, reading your actual codebase. The Lead Synthesis agent (powered by Opus for deeper reasoning) waits for all analysts to complete, then produces the final report.

---

## Agents

| Agent | Model | Role |
|-------|-------|------|
| `business-product` | Sonnet | Market opportunity, product-market fit, competitive landscape, go-to-market |
| `financial-cost` | Sonnet | Infrastructure costs, TCO modeling, build-vs-buy, ROI projections |
| `technical-architecture` | Sonnet | Architecture scoring (scalability, reliability, security, maintainability, observability, operability) |
| `devils-advocate` | Sonnet | Stress-testing, assumption challenging, pre-mortem analysis, blind spot identification |
| `lead-synthesis` | **Opus** | Orchestration, convergence/divergence analysis, final OmniLabs Report |

---

## Quick Start

### Option 1: One-Line Install

```bash
curl -sL https://raw.githubusercontent.com/Viniciuscarvalho/OmniLabs/main/install.sh | bash
```

### Option 2: Manual Install

```bash
# Clone the repo
git clone https://github.com/Viniciuscarvalho/OmniLabs.git

# Copy .claude/ folder to your project
cp -r OmniLabs/.claude/ /path/to/your/project/.claude/
```

### Option 3: Cherry-Pick Agents

Copy individual agent files from `.claude/agents/` into your project's `.claude/agents/` directory.

---

## Usage

### Full Analysis

Open Claude Code in your project and paste:

```
Run a full OmniLabs strategic analysis of this project.

Create a team called "omnilabs-analysis" with 5 agents:

1. business-product (Sonnet) — Analyze market opportunity, product-market fit, competitive landscape, and go-to-market strategy.
2. financial-cost (Sonnet) — Model infrastructure costs, calculate TCO at different scales, evaluate build-vs-buy decisions, and project ROI.
3. technical-architecture (Sonnet) — Evaluate system architecture across 6 dimensions: scalability, reliability, maintainability, security, observability, and operability.
4. devils-advocate (Sonnet) — Stress-test all findings. Challenge assumptions with evidence from code.
5. lead-synthesis (Opus) — Wait for all 4 analysts, then synthesize the OmniLabs Report with GO/NO-GO decision.

Run analysts 1-4 in parallel. Agent 5 starts only after all 4 complete.
```

See [`agent-team-prompt.md`](agent-team-prompt.md) for individual agent prompts and more options.

### Individual Agents

For focused deep-dives, use the detailed prompt files — each contains comprehensive evaluation criteria and structured output expectations:

| Agent | Prompt File | What It Covers |
|-------|-------------|----------------|
| Business & Product | [`business-product-analysis.md`](business-product-analysis.md) | Product definition, market opportunity, PMF signals, competitive landscape, GTM, business model, risks |
| Financial & Cost | [`financial-cost-analysis.md`](financial-cost-analysis.md) | Infrastructure inventory, third-party costs, TCO at 4 scales, unit economics, optimization, runway |
| Technical Architecture | [`technical-architecture-review.md`](technical-architecture-review.md) | 6-dimension scoring (scalability, reliability, maintainability, security, observability, operability) |
| Devil's Advocate | [`devil-advocate-challenge.md`](devil-advocate-challenge.md) | Assumption deconstruction, architectural fragility, pre-mortem, competitor counterattack, uncomfortable questions |

Copy the contents of any prompt file and paste it into Claude Code.

---

## The OmniLabs Report

The final synthesis produces a structured report with:

- **Decision**: GO / NO-GO / CONDITIONAL GO with confidence level
- **Dimension Scores**: Quantitative ratings across all analysis dimensions
- **Consensus Findings**: Where 3+ analysts agree (high confidence)
- **Contested Findings**: Where analysts disagree (with evidence from both sides)
- **Blind Spots**: Issues no single analyst fully addressed
- **Risk Matrix**: Probability x Impact with mitigations
- **Implementation Roadmap**: 30/60/90-day phased action plan

---

## Examples

- [SaaS Product Evaluation](examples/saas-evaluation.md) — Should we launch this B2B analytics platform?
- [Technical Migration](examples/tech-migration.md) — Should we migrate from Rails monolith to Go microservices?
- [Market Entry](examples/market-entry.md) — Should we expand from individual devs to enterprise?

---

## Design Principles

1. **Code-first analysis** — Agents read the actual codebase, not just documentation
2. **Evidence over opinion** — Every finding must be traceable to code or data
3. **Constructive challenge** — The devil's advocate strengthens ideas, doesn't kill them
4. **Actionable output** — Every report includes a clear decision and implementation roadmap
5. **Language-agnostic** — Works with any tech stack, any language, any framework

---

## Requirements

- [Claude Code](https://claude.com/claude-code) CLI
- Agent teams support (enabled via settings.json)

---

## Project Structure

```
OmniLabs/
├── .claude/
│   ├── agents/
│   │   ├── business-product.md
│   │   ├── financial-cost.md
│   │   ├── technical-architecture.md
│   │   ├── devils-advocate.md
│   │   └── lead-synthesis.md
│   ├── settings.json
│   └── CLAUDE.md
├── agent-team-prompt.md
├── business-product-analysis.md
├── financial-cost-analysis.md
├── technical-architecture-review.md
├── devil-advocate-challenge.md
├── examples/
│   ├── saas-evaluation.md
│   ├── tech-migration.md
│   └── market-entry.md
├── install.sh
├── README.md
└── LICENSE
```

---

## Contributing

Contributions welcome! Ideas for new agents, improved frameworks, or better prompts — open an issue or PR.

---

## License

MIT — see [LICENSE](LICENSE)
