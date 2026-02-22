# Evaluation Guide

## Overview

OmniLabs uses evaluations (evals) to validate that agents produce correct, well-structured, and insightful output. Evals are the tests for prompts — they verify that agent behavior remains correct as prompts evolve.

### Why Evals Matter

- **Regression detection**: Catch when a prompt change breaks existing behavior
- **Quality baseline**: Know the current quality level of each agent
- **Improvement tracking**: Measure whether changes actually improve output
- **Confidence to iterate**: Change prompts without fear of hidden degradation

## Running Evaluations

### Single Task

Run one eval task against an agent:

```bash
bash evaluation/harness/run-eval.sh \
  --agent business-product \
  --task evaluation/tasks/business-product/task-saas-happy-path.md
```

This will:
1. Extract the input from the task file
2. Run the agent via `claude` CLI
3. Save the output to `evaluation/results/`
4. Run the code-based grader
5. Produce a PASS/FAIL verdict

### Grade Existing Output

Skip agent execution and grade an existing output file:

```bash
bash evaluation/harness/run-eval.sh \
  --agent technical-architecture \
  --task evaluation/tasks/technical-architecture/task-monolith-happy.md \
  --grader-only \
  --output path/to/output.md
```

### All Tasks for One Agent

```bash
bash evaluation/harness/run-all.sh --agent financial-cost
```

### Full Suite

```bash
bash evaluation/harness/run-all.sh
```

### Generate Report

```bash
bash evaluation/harness/report.sh
```

With regression comparison:

```bash
bash evaluation/harness/report.sh --compare evaluation/results/summary-previous.md
```

## Understanding Results

### Code-Based Grader Results

Code-based graders validate **structural correctness**: required sections, score formats, table structure, cross-references.

```
═══════════════════════════════════════════
 Grade Report: business-product
═══════════════════════════════════════════
  PASS score_format — Score 7/10 found
  PASS section_executive_summary — Section 'Executive Summary' found
  PASS section_market_analysis — Section 'Market Analysis' found
  FAIL section_competitive_position — Missing section matching 'Competitive Position'
  PASS moat_strength —
  PASS word_count — 823 words (min: 500)
───────────────────────────────────────────
  Passed: 5  Failed: 1  Warnings: 0  Total: 6
  Pass Rate: 83%
═══════════════════════════════════════════
```

- Each check is PASS, FAIL, or WARN
- A task passes when **all checks pass** (WARN doesn't fail)
- Failed checks include a description of what's missing

### Model-Based Grader Results

Model-based graders assess **output quality** using LLM-as-Judge rubrics. To use them:

1. Copy the rubric from `evaluation/graders/model-based/rubric-<agent>.md`
2. Paste it into Claude along with the agent's output
3. Ask Claude to score the output using the rubric

Scoring thresholds:

| Verdict | Score Range |
|---------|-------------|
| **PASS** | >= 3.5/5 |
| **MARGINAL** | 2.5 — 3.49/5 |
| **FAIL** | < 2.5/5 |

### Interpreting Failures

| Failure Type | Likely Cause | Fix |
|-------------|-------------|-----|
| Missing section | Agent prompt's Output Format needs reinforcement | Add explicit section requirement in agent's Output Format |
| Wrong score format | Agent used different scoring convention | Standardize scoring instructions in agent prompt |
| Missing cross-references | Devil's advocate not engaging with other analysts | Strengthen Challenge Protocol instructions |
| Low word count | Agent produced stub output | Add minimum depth requirements to agent prompt |
| Placeholder text | Agent used template without filling in | Strengthen "no placeholder" instruction |

## Improving Agent Prompts Based on Eval Results

### The Improvement Loop

```
Run Evals → Identify Failures → Trace to Prompt Section → Strengthen Instruction → Re-run Evals
```

### Step-by-Step

1. **Run evals** and identify which checks fail most frequently
2. **Trace back** to the agent prompt section that governs the failing behavior
3. **Strengthen the instruction**: Be more specific, add examples, or restructure
4. **Re-run evals** to verify the fix works
5. **Check for regressions**: Make sure the fix didn't break other checks

### Avoiding Over-Fitting

- Don't optimize for specific eval tasks at the expense of general capability
- If a fix helps one task but hurts another, the prompt change is too narrow
- Add more diverse tasks rather than tuning for existing ones
- Balance specificity (precise instructions) with generality (flexible application)

## CI/CD Integration

Code-based graders run automatically in GitHub Actions on PRs that modify:
- `.claude/agents/` (agent prompt changes)
- `evaluation/graders/` (grader changes)
- `evaluation/tasks/` (task changes)

The CI workflow (`eval.yml`) validates:
- Grader script syntax
- Rubric structure (dimensions, weights, verdicts)
- Agent frontmatter consistency

Full agent execution is **not run in CI** (requires Claude API access). Run full evals locally before submitting PRs that modify agent prompts.

## Golden Datasets

Three reference datasets in `evaluation/datasets/` serve as standardized project descriptions:

| Dataset | Scenario | Use For |
|---------|----------|---------|
| `golden-saas-project.md` | Well-structured B2B SaaS | Baseline testing, happy-path validation |
| `golden-risky-project.md` | Problematic Crypto/DeFi project | Negative testing, risk detection |
| `golden-early-stage.md` | Pre-MVP with minimal code | Edge-case testing, graceful adaptation |

Use these datasets as input for manual agent testing when developing new eval tasks or modifying agent prompts.
