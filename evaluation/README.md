# OmniLabs Evaluation Framework

This directory contains the evaluation infrastructure for validating OmniLabs agent output quality.

## Structure

```
evaluation/
├── tasks/                    # Test cases per agent
│   ├── business-product/     # 4 tasks
│   ├── financial-cost/       # 4 tasks
│   ├── technical-architecture/ # 4 tasks
│   ├── devils-advocate/      # 4 tasks
│   └── lead-synthesis/       # 3 tasks
├── graders/
│   ├── code-based/           # Deterministic shell script graders
│   │   ├── common.sh         # Shared utility functions
│   │   └── grade-*.sh        # Per-agent grader scripts
│   └── model-based/          # LLM-as-Judge rubrics (markdown)
│       └── rubric-*.md       # Per-agent scoring rubrics
├── datasets/                 # Golden reference project descriptions
│   ├── golden-saas-project.md
│   ├── golden-risky-project.md
│   └── golden-early-stage.md
├── harness/                  # Evaluation runner scripts
│   ├── run-eval.sh           # Run a single eval task
│   ├── run-all.sh            # Run all tasks for one/all agents
│   └── report.sh             # Generate evaluation report
└── results/                  # Output directory for eval runs
```

## Quick Start

```bash
# Run all evaluations (grader-only mode, no agent execution)
bash evaluation/harness/run-all.sh --grader-only

# Run evaluations for a single agent
bash evaluation/harness/run-all.sh --agent business-product

# Grade an existing output file
bash evaluation/harness/run-eval.sh --agent technical-architecture \
  --task evaluation/tasks/technical-architecture/task-monolith-happy.md \
  --grader-only --output path/to/output.md
```

## Grader Types

### Code-Based (Deterministic)
Shell scripts that validate structural correctness: required sections, score formats, table structure, cross-references. Run in CI without LLM access.

### Model-Based (LLM-as-Judge)
Markdown rubrics designed to be used with Claude for qualitative assessment: analysis depth, reasoning quality, actionability. Run manually.

## Adding Evaluations

See [docs/contributing-evals.md](../docs/contributing-evals.md) for the complete guide.
