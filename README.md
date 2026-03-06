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
# Agents only
curl -sL https://raw.githubusercontent.com/Viniciuscarvalho/OmniLabs/main/install.sh | bash

# With evaluation framework
curl -sL https://raw.githubusercontent.com/Viniciuscarvalho/OmniLabs/main/install.sh | bash -s -- --with-evals

# With continuous learning
curl -sL https://raw.githubusercontent.com/Viniciuscarvalho/OmniLabs/main/install.sh | bash -s -- --with-learning

# Everything
curl -sL https://raw.githubusercontent.com/Viniciuscarvalho/OmniLabs/main/install.sh | bash -s -- --with-evals --with-learning
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

## Dashboard

Every analysis automatically generates a **visual dashboard** that opens in your browser — no more losing results inside conversation history.

<p align="center">
  <img src="assets/dashboard-preview.png" alt="OmniLabs Dashboard" width="100%" style="border-radius: 12px;">
</p>

The dashboard shows:

- **Stats bar** — total analyses, GO/NO-GO/CONDITIONAL counts at a glance
- **Latest analysis** — decision, composite score, dimension scores, conditions, and consensus findings
- **Agent reports** — status and score for each of the 5 agents
- **Analysis history** — every past analysis with scores and decisions
- **Knowledge base** — memory files and Ollama status

### How it works

After the lead-synthesis agent completes the OmniLabs Report, it automatically:

1. Saves a structured `summary.json` to `reports/<timestamp>/`
2. Runs `scripts/generate-dashboard.sh --open`
3. The dashboard opens in your default browser

### Manual usage

```bash
# Regenerate and open the dashboard
bash scripts/generate-dashboard.sh --open

# Just regenerate (no browser)
bash scripts/generate-dashboard.sh
```

The dashboard is a **self-contained HTML file** generated from `dashboard/template.html`. Report data is embedded at generation time — no server needed.

---

## Examples

| Scenario | Description |
|----------|-------------|
| [SaaS Product Evaluation](examples/saas-evaluation.md) | Should we launch this B2B analytics platform? |
| [Technical Migration](examples/tech-migration.md) | Should we migrate from Rails monolith to Go microservices? |
| [Market Entry](examples/market-entry.md) | Should we expand from individual devs to enterprise? |

---

## Evaluation Framework

**Evals are the tests for prompts.** Just like unit tests validate code, evals validate that agent behavior stays correct as prompts evolve. OmniLabs ships with a complete, shell-only evaluation framework — no Python, no Node, no runtime dependencies.

### Why Agent Evals?

Agent outputs are non-deterministic. The same prompt can produce different results across runs. Without evals, you can't know if a prompt change improved or regressed agent quality. OmniLabs evals solve this with two layers:

- **Code-based graders** (deterministic) — bash scripts that validate structural contracts: required sections exist, scores are in range, tables have correct columns, cross-references are present. These run in CI on every PR.
- **Model-based rubrics** (qualitative) — LLM-as-Judge scoring across 5 weighted dimensions per agent. These measure depth, evidence grounding, actionability, and intellectual honesty. Run manually with Claude.

### What Gets Evaluated

Each of the 5 agents has its own eval suite:

| Agent | Tasks | Code Grader Checks | Rubric Dimensions |
|-------|-------|--------------------|-------------------|
| `business-product` | 4 (SaaS, marketplace, empty repo, OSS tool) | Score format, 7 sections, moat label, TAM/SAM/SOM, competitors | Analysis Depth, Code Grounding, Actionability, Risk Awareness, Honesty |
| `financial-cost` | 4 (AWS stack, serverless, no infra, multi-cloud) | Score format, 6 sections, cost table, scaling table, 4 scale tiers | Financial Rigor, Code Grounding, Scaling Accuracy, Optimization, Risk |
| `technical-architecture` | 4 (monolith, microservices, no tests, legacy PHP) | Score format, 6 dimension scores, severity labels, timeline sections | Technical Accuracy, Code Grounding, Coverage, Prioritization, Constructiveness |
| `devils-advocate` | 4 (overconfident analysts, minimal findings, strong project, no competitors) | Score format, 7 sections, risk heat map, failure scenarios, cross-references | Challenge Thoroughness, Evidence Quality, Cross-References, Blind Spots, Strengthening |
| `lead-synthesis` | 3 (consensus, conflicting signals, mixed signals) | GO/NO-GO decision, confidence, composite score, 4 analyst references, roadmap | Synthesis Quality, Decision Clarity, Conflict Resolution, Completeness, Actionability |

**19 tasks total** — covering happy-path, edge-case, and negative scenarios.
**3 golden datasets** — reference projects (SaaS, high-risk DeFi, pre-MVP) with expected analysis patterns per agent.

### Quick Start

```bash
# Install evals (if not already installed)
bash install.sh --with-evals

# Run all evaluations
bash evaluation/harness/run-all.sh

# Run for a single agent
bash evaluation/harness/run-all.sh --agent business-product

# Grade an existing output file (skip agent execution)
bash evaluation/harness/run-eval.sh --agent technical-architecture \
  --grader-only --output path/to/output.md

# Generate a report with pass rates and regressions
bash evaluation/harness/report.sh
```

### Automated Test Coverage

The grader test suite validates that graders work correctly in both directions:

```bash
# Run the grader test suite
bash evaluation/tests/test-graders.sh
```

**Phase 1 (positive tests)** — golden outputs must PASS all grader checks:

| Agent | Golden Output | Checks |
|-------|--------------|--------|
| `business-product` | `golden-outputs/golden-business-product.md` | 15 |
| `financial-cost` | `golden-outputs/golden-financial-cost.md` | 17 |
| `technical-architecture` | `golden-outputs/golden-technical-arch.md` | 19 |
| `devils-advocate` | `golden-outputs/golden-devils-advocate.md` | 17 |
| `lead-synthesis` | `golden-outputs/golden-lead-synthesis.md` | 19 |

**Phase 2 (negative tests)** — broken outputs must FAIL:
- Empty files fail all 5 graders
- Missing sections detected (business-product)
- Missing scores detected (financial-cost)
- Placeholder text detected (`[TODO]`, `[TBD]`)
- Missing cross-references detected (devils-advocate)
- Missing decision detected (lead-synthesis)

**15 tests total, 87 grader checks validated.**

### Eval Architecture

```
evaluation/
├── tasks/                    19 test scenarios (4 per analyst + 3 for synthesis)
│   ├── business-product/     Happy-path, marketplace edge, empty repo, no revenue
│   ├── financial-cost/       AWS stack, serverless, no infra, multi-cloud
│   ├── technical-architecture/  Monolith, microservices, no tests, legacy
│   ├── devils-advocate/      Overconfident, minimal, strong project, no competitors
│   └── lead-synthesis/       Consensus, conflicting, mixed signals
├── graders/
│   ├── code-based/           Deterministic bash graders (CI-ready)
│   │   ├── common.sh         Shared utilities (check_section, check_score, etc.)
│   │   └── grade-*.sh        One grader per agent
│   └── model-based/          LLM-as-Judge rubrics (manual)
│       └── rubric-*.md       5 dimensions per agent, weighted scoring
├── datasets/                 Golden reference projects
│   ├── golden-saas-project.md       B2B SaaS — balanced analysis expected
│   ├── golden-risky-project.md      DeFi — NO-GO expected
│   └── golden-early-stage.md        Pre-MVP — conditional analysis expected
├── harness/                  Orchestration scripts
│   ├── run-eval.sh           Single task runner
│   ├── run-all.sh            Suite runner with aggregation
│   └── report.sh             Report generator with regression detection
└── results/                  Output directory
```

See [docs/evaluation-guide.md](docs/evaluation-guide.md) for the full guide, [docs/architecture.md](docs/architecture.md) for system design, and [docs/contributing-evals.md](docs/contributing-evals.md) for adding new evals.

---

## Continuous Learning (Optional)

OmniLabs can learn from your analysis sessions. The continuous learning system captures patterns, decisions, and findings into a local knowledge base, then retrieves them via semantic search at the start of future sessions.

### How It Works

```
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                        CONTINUOUS LEARNING LOOP                         │
  │                                                                         │
  │  ┌─────────────┐     ┌──────────────────┐     ┌─────────────────────┐  │
  │  │  📡 Ollama   │────▶│  🔍 docs-mcp     │────▶│  📂 .claude/        │  │
  │  │  localhost   │     │  server           │     │  memories/          │  │
  │  │  :11434      │     │  (semantic search) │     │                     │  │
  │  │  nomic-      │◀────│                   │◀────│  learning_*.md      │  │
  │  │  embed-text  │ idx │                   │ r/w │  decision_*.md      │  │
  │  └─────────────┘     └──────────────────┘     └─────────────────────┘  │
  │         │                     ▲  │                       ▲              │
  │         │                     │  │ search                │ save         │
  │         │                     │  ▼                       │              │
  │  ┌──────▼──────────────────────────────────────────────────────────┐   │
  │  │                      ANALYSIS SESSION                           │   │
  │  │                                                                 │   │
  │  │  1. 🚀 Session Start                                           │   │
  │  │     └─ ollama-status.sh → check health, sync memories          │   │
  │  │                                                                 │   │
  │  │  2. 🔎 Search KB                                               │   │
  │  │     └─ search_docs("omnilabs-memories", "<task keywords>")     │   │
  │  │     └─ Review prior patterns, decisions, findings              │   │
  │  │                                                                 │   │
  │  │  3. 📊 Run Analysis                                            │   │
  │  │     └─ Agents analyze codebase (enriched by KB context)        │   │
  │  │     └─ activator hook → reminds about knowledge capture        │   │
  │  │                                                                 │   │
  │  │  4. 💾 Capture Knowledge                                       │   │
  │  │     └─ continuous-learning skill                               │   │
  │  │     └─ Evaluate → Search existing → Structure → Save           │   │
  │  │                                                                 │   │
  │  │  5. 🔄 Next session → memories indexed → searchable            │   │
  │  └─────────────────────────────────────────────────────────────────┘   │
  └─────────────────────────────────────────────────────────────────────────┘
```

### Memory Types

Two types of memories, organized across 6 domains:

```
  .claude/memories/
  ├── learning_analysis_tam-estimation-saas.md        # 💡 Discovery
  ├── learning_evaluation_false-positive-moat.md      # 💡 Eval insight
  ├── learning_debugging_grader-exit-codes.md         # 💡 Workaround
  ├── decision_agent_score-range-calibration.md       # 📌 Choice
  ├── decision_framework_hook-registration.md         # 📌 Architecture
  └── decision_tooling_embedding-model-choice.md      # 📌 Tool selection
```

| Type | Pattern | When to capture |
|------|---------|-----------------|
| **Learnings** | `learning_<topic>_<specific>.md` | Debugging discoveries, analysis patterns, workarounds, non-obvious findings |
| **Decisions** | `decision_<domain>_<topic>.md` | Architecture choices, conventions, scoring calibration, methodology |

Domains: `analysis` · `evaluation` · `agent` · `framework` · `tooling` · `debugging`

### Stack

| Layer | Component | Purpose |
|-------|-----------|---------|
| Embeddings | [Ollama](https://ollama.com) + `nomic-embed-text` | Local vector embeddings — no API keys, no cloud |
| Search | [docs-mcp-server](https://github.com/arabold/docs-mcp-server) | Semantic search MCP over `.claude/memories/` |
| Capture | `continuous-learning` skill | 4 templates: Learning, Decision, Analysis Pattern, Eval Finding |
| Activation | `continuous-learning-activator.sh` | PreToolUse hook — reminds about knowledge capture |
| Sync | `ollama-status.sh` | SessionStart hook — health check + memory indexing |

### Prerequisites

```bash
brew install ollama              # or download from https://ollama.com
ollama pull nomic-embed-text     # embedding model (~274MB)
ollama serve                     # start the server
```

Node.js is also required (for `npx` to run docs-mcp-server).

The system **degrades gracefully** — if Ollama is not running, analysis works normally without KB search. Memories are still saved as files and will be indexed the next time Ollama is available.

See [docs/continuous-learning.md](docs/continuous-learning.md) for the full guide.

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
│   ├── skills/continuous-learning/      # Knowledge capture skill
│   │   ├── SKILL.md
│   │   └── references/templates.md
│   ├── hooks/                           # Session & tool hooks
│   │   ├── ollama-status.sh
│   │   └── continuous-learning-activator.sh
│   ├── memories/                        # Knowledge base (markdown files)
│   ├── settings.json
│   └── CLAUDE.md
├── dashboard/
│   └── template.html                    # Dashboard HTML template
├── scripts/
│   ├── generate-dashboard.sh            # Generates dashboard from reports
│   └── save-report.sh                   # Saves agent reports as JSON
├── reports/                             # Analysis reports (auto-generated)
├── evaluation/
│   ├── tasks/                           # Eval test cases per agent
│   ├── graders/
│   │   ├── code-based/                  # Deterministic bash graders
│   │   └── model-based/                 # LLM-as-Judge rubrics
│   ├── golden-outputs/                  # Reference outputs that pass all graders
│   ├── tests/
│   │   └── test-graders.sh             # Automated grader test suite
│   ├── datasets/                        # Golden reference projects
│   ├── harness/                         # Eval runner scripts
│   └── results/                         # Eval output
├── docs/
│   ├── architecture.md                  # System architecture
│   ├── contributing-evals.md            # Guide for adding evals
│   ├── evaluation-guide.md             # How to run and interpret evals
│   └── continuous-learning.md          # Continuous learning guide
├── .github/workflows/                   # CI: lint + eval validation
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
