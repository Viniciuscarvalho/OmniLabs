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
  <strong>Plug-and-play subagent framework for Claude Code.</strong><br>
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

The **main Claude Code conversation** orchestrates everything — it launches 4 analyst subagents in parallel, waits for results, then delegates to the Lead Synthesis subagent (powered by **Opus**) which produces the final report. Subagents cannot spawn other subagents; this follows the [official Claude Code subagent spec](https://code.claude.com/docs/en/sub-agents).

---

## Agents

| | Agent | Model | Role |
|---|-------|-------|------|
| 🟡 | `business-product` | Sonnet | Market opportunity, product-market fit, competitive landscape, go-to-market |
| 🟢 | `financial-cost` | Sonnet | Infrastructure costs, TCO modeling, build-vs-buy, ROI projections |
| 🔵 | `technical-architecture` | Sonnet | Architecture scoring across 6 dimensions (scalability, reliability, security, maintainability, observability, operability) |
| 🔴 | `devils-advocate` | Sonnet | Stress-testing, assumption challenging, pre-mortem analysis, blind spot identification |
| 🟣 | `lead-synthesis` | **Opus** | Synthesis, convergence/divergence analysis, final OmniLabs Report |

The 4 analysts use **read-only tools** (Read, Grep, Glob, Bash). The lead-synthesis also has Write for saving dashboard reports. All subagents are defined in `.claude/agents/` as Markdown files with YAML frontmatter.

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

## Running an Analysis

### Step 1: Open Claude Code in your project

```bash
cd /path/to/your/project
claude
```

Make sure the `.claude/agents/` folder from OmniLabs is in your project (see [Install](#install)).

### Step 2: Run the full analysis

Paste this into Claude Code:

```
Run a full OmniLabs strategic analysis of this project.
```

That's it. Claude Code will:

1. Launch **4 analyst agents in parallel** (business, financial, technical, devil's advocate)
2. Each agent reads your actual codebase — source files, configs, dependencies, tests
3. Wait for all 4 to complete
4. Launch the **lead-synthesis agent** (Opus) to synthesize findings
5. Produce the **OmniLabs Report** with a GO / NO-GO / CONDITIONAL GO decision
6. Save results and **open the dashboard** in your browser

### What happens during the analysis

```
You paste the prompt
        |
        v
  ┌─────┼─────┬──────────┐
  v     v     v          v
 🟡    🟢    🔵         🔴
 Business  Financial  Technical  Devil's
 Product   Cost       Arch       Advocate
 (Sonnet)  (Sonnet)   (Sonnet)   (Sonnet)
  │     │     │          │
  │  reads code, configs, deps, tests
  │     │     │          │
  └─────┴─────┴──────┬───┘
                      v
                 🟣 Lead Synthesis (Opus)
                      │
                      v
              OmniLabs Report
            + Dashboard opens
```

Each agent has **read-only access** to your codebase (Read, Grep, Glob, Bash). They examine:
- Source code and architecture patterns
- `package.json`, `Dockerfile`, `terraform`, CI configs
- Test coverage and quality
- Environment variables and infrastructure signals
- README, docs, and business context

### Alternative: Run individual agents

For a focused deep-dive on one dimension, run a single agent:

```
Run the business-product analysis on this project.
```

```
Run the technical-architecture review on this project.
```

```
Run the financial-cost analysis on this project.
```

```
Run the devils-advocate challenge on this project.
```

Each agent has a dedicated prompt file with detailed evaluation criteria:

| | Agent | Prompt File | What It Analyzes |
|---|-------|-------------|------------------|
| 🟡 | Business & Product | [`business-product-analysis.md`](business-product-analysis.md) | Market opportunity, PMF, competitive landscape, GTM, business model |
| 🟢 | Financial & Cost | [`financial-cost-analysis.md`](financial-cost-analysis.md) | Infrastructure costs, TCO at 4 scales, build-vs-buy, unit economics |
| 🔵 | Technical Architecture | [`technical-architecture-review.md`](technical-architecture-review.md) | 6 dimensions: scalability, reliability, maintainability, security, observability, operability |
| 🔴 | Devil's Advocate | [`devil-advocate-challenge.md`](devil-advocate-challenge.md) | Assumption stress-testing, pre-mortem, blind spots, failure scenarios |

### The OmniLabs Report

The lead-synthesis agent produces a structured executive report:

| Section | Description |
|---------|-------------|
| **Decision** | GO / NO-GO / CONDITIONAL GO with confidence level |
| **Dimension Scores** | Quantitative ratings across all analysis dimensions |
| **Consensus Findings** | Where 3+ analysts agree (high confidence) |
| **Contested Findings** | Where analysts disagree, with evidence from both sides |
| **Blind Spots** | Issues no single analyst fully addressed |
| **Risk Matrix** | Probability x Impact with mitigations |
| **Implementation Roadmap** | 30/60/90-day phased action plan |

See [`agent-team-prompt.md`](agent-team-prompt.md) for the full orchestration prompt with all configuration options.

---

## Dashboard

Analysis results are persisted in a **visual dashboard** that opens in your browser — no more losing findings inside conversation history. Every analysis accumulates in the dashboard, giving you a historical view of all evaluations.

<p align="center">
  <img src="assets/dashboard-preview.png" alt="OmniLabs Dashboard" width="100%" style="border-radius: 12px;">
</p>

### What the dashboard shows

| Section | Description |
|---------|-------------|
| **Stats bar** | Total analyses, GO / NO-GO / CONDITIONAL counts |
| **Latest analysis** | Decision, composite score, dimension scores, conditions, consensus |
| **Agent reports** | Status and score for each of the 5 agents |
| **Analysis history** | Every past analysis with scores and decisions |
| **Knowledge base** | Memory file count and Ollama connection status |

### Automatic flow

When you run a full OmniLabs analysis, the dashboard is generated automatically:

```
You run analysis in Claude Code
        |
        v
4 agents analyze in parallel (Sonnet)
        |
        v
Lead Synthesis produces report (Opus)
        |
        v
Saves summary.json to reports/<timestamp>/    <-- persistent data
        |
        v
Runs: bash scripts/generate-dashboard.sh --open
        |
        v
Dashboard opens in your browser
```

You don't need to do anything extra — the lead-synthesis agent handles saving and opening.

### Manual usage

If you want to open the dashboard outside of an analysis (e.g., to review past results):

```bash
# Generate the dashboard and open it in your browser
bash scripts/generate-dashboard.sh --open

# Generate without opening (useful in CI or scripts)
bash scripts/generate-dashboard.sh
```

### How it works under the hood

```
dashboard/template.html     <-- HTML template (committed to git)
        +
reports/*/summary.json      <-- analysis data (one per run)
        |
        v
scripts/generate-dashboard.sh
        |
        v
dashboard/index.html        <-- generated file (gitignored)
```

1. **`dashboard/template.html`** is the HTML template with a `__DASHBOARD_DATA__` placeholder
2. **`scripts/generate-dashboard.sh`** reads all `reports/*/summary.json` files, collects memory files from `.claude/memories/`, checks Ollama status, and injects all data into the template
3. **`dashboard/index.html`** is the generated output — a self-contained HTML file with all data embedded. No server needed, just open in any browser
4. **`scripts/save-report.sh`** is called by the lead-synthesis agent to create the report directory and trigger dashboard regeneration

### Adding reports manually

If you want to add a report without running a full analysis (e.g., from a previous session):

```bash
# Create a report directory
bash scripts/save-report.sh "My Project"
# This prints the path, e.g.: reports/2026-03-06-153000/

# Edit the summary.json in that directory with your data
# Then regenerate the dashboard
bash scripts/generate-dashboard.sh --open
```

The `summary.json` format:

```json
{
  "project": "Project Name",
  "date": "2026-03-06 15:30",
  "decision": "GO | NO-GO | CONDITIONAL GO",
  "confidence": "Low | Medium | High | Very High",
  "composite_score": 7.5,
  "scores": { "market": 8, "financial": 7, "architecture": 8, "risk": 6 },
  "conditions": ["condition if CONDITIONAL GO"],
  "consensus": ["high-confidence finding"],
  "agents": {
    "business_product": { "score": 8, "summary": "one-line summary" },
    "financial_cost": { "score": 7, "summary": "one-line summary" },
    "technical_architecture": { "score": 8, "summary": "one-line summary" },
    "devils_advocate": { "score": 6, "summary": "one-line summary" },
    "lead_synthesis": { "score": 7.5, "summary": "one-line summary" }
  }
}
```

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
- Subagents defined in `.claude/agents/` (loaded automatically by Claude Code)

---

## Contributing

Contributions welcome — new agents, improved frameworks, better prompts. Open an issue or PR.

---

<p align="center">
  <sub>MIT License — see <a href="LICENSE">LICENSE</a></sub>
</p>
