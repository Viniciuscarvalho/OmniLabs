# OmniLabs Architecture

## System Overview

OmniLabs is a multi-perspective strategic analysis framework for Claude Code. It deploys 5 specialized agents that analyze a project from business, financial, technical, and adversarial perspectives, then synthesizes findings into a single actionable report.

The framework is **prompt-based** — no runtime code, no dependencies beyond Claude Code and bash. All agent behavior is defined in markdown files with YAML frontmatter.

## Agent Dependency Graph

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ business-product │  │  financial-cost  │  │    technical-    │
│    (Sonnet)      │  │    (Sonnet)      │  │  architecture    │
│                  │  │                  │  │    (Sonnet)      │
└────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘
         │                     │                      │
         │         ┌───────────┴───────────┐          │
         │         │                       │          │
         ▼         ▼                       ▼          ▼
    ┌──────────────────────────────────────────────────────┐
    │              devils-advocate (Sonnet)                 │
    │  Reads outputs from business, financial, technical   │
    └──────────────────────┬───────────────────────────────┘
                           │
                           ▼
    ┌──────────────────────────────────────────────────────┐
    │              lead-synthesis (Opus)                    │
    │  Reads ALL 4 analyst outputs, produces final report  │
    └──────────────────────────────────────────────────────┘
```

### Execution Flow

1. **Parallel Phase**: Agents 1-3 (business, financial, technical) run simultaneously. Each reads the target project's codebase independently.
2. **Challenge Phase**: Devil's advocate runs after agents 1-3 complete. It reads their outputs and challenges findings with evidence.
3. **Synthesis Phase**: Lead synthesis runs last. It reads all 4 outputs and produces the OmniLabs Report with a GO/NO-GO decision.

## Agent File Format

Each agent is defined in `.claude/agents/<name>.md` with:

```yaml
---
name: agent-name              # Must match filename
description: |                # Shown in Claude Code agent picker
  Description with examples
model: sonnet | opus          # LLM model
color: yellow | green | blue  # UI color
tools: Read, Grep, Glob, Bash # Available tools (analysts are read-only)
---
```

Followed by markdown sections:

| Section | Purpose |
|---------|---------|
| **Persona** | Role definition, experience level, approach |
| **Analysis Framework** | Numbered evaluation dimensions/criteria |
| **Methodology** | How the agent should gather evidence |
| **Output Format** | Expected structure of the output (the eval contract) |
| **Quality Checklist** | Self-validation items |
| **Guiding Principle** | Core philosophy quote |

## Output Format Contracts

Each agent's Output Format section defines the structural contract that the evaluation framework validates against. This is the key interface:

| Agent | Primary Score | Key Structural Elements |
|-------|--------------|------------------------|
| business-product | Market Opportunity Score: X/10 | TAM/SAM/SOM, competitors, moat strength, GTM plan |
| financial-cost | Financial Health Score: X/10 | Cost table, scaling table (4 tiers), dollar amounts |
| technical-architecture | Architecture Health Score: X/10 | 6 dimension scores, severity labels, timeline |
| devils-advocate | Risk Score: X/10 | Risk heat map, 3 failure scenarios, assumption verdicts |
| lead-synthesis | Composite Score: X/10 | GO/NO-GO decision, consensus/contested findings, roadmap |

## Evaluation Framework

```
evaluation/
├── tasks/          ← Test scenarios per agent (input + expected behaviors)
├── graders/
│   ├── code-based/ ← Deterministic bash scripts (validate structure)
│   └── model-based/← LLM-as-Judge rubrics (assess quality)
├── datasets/       ← Golden reference project descriptions
├── harness/        ← Shell scripts to orchestrate eval runs
└── results/        ← Output from eval runs
```

### Grading Pipeline

```
Task File ──→ Agent Execution ──→ Output File ──→ Code-Based Grader ──→ PASS/FAIL
                  (optional)                           │
                                                       ▼
                                              Model-Based Grader ──→ Score/5
                                                  (manual)
```

Code-based graders run in CI (deterministic, fast). Model-based graders run manually with Claude (qualitative assessment).

## Extension Points

### Adding a New Agent

1. Create `.claude/agents/<name>.md` following the format above
2. Create `evaluation/tasks/<name>/` with task files
3. Create `evaluation/graders/code-based/grade-<name>.sh`
4. Create `evaluation/graders/model-based/rubric-<name>.md`
5. Update the agent team prompt in `agent-team-prompt.md`
6. Update the dependency graph if the new agent has dependencies

### Adding a New Evaluation Dimension

1. Add task files testing the new dimension
2. Add grader checks in the relevant `grade-*.sh`
3. Add a rubric dimension in the relevant `rubric-*.md`

### Customizing for a Specific Project

1. Copy `.claude/` into your project
2. Optionally modify agent personas or frameworks for your domain
3. Run the team prompt to analyze your project
4. Use evals to validate output quality
