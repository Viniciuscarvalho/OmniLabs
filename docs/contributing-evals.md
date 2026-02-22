# Contributing Evaluations

This guide explains how to add new eval tasks, grader checks, and model-based rubric dimensions to the OmniLabs evaluation framework.

## Adding a New Task

### 1. Choose the Agent Directory

Tasks live under `evaluation/tasks/<agent-name>/`. Pick the agent this task evaluates.

### 2. Create the Task File

Use the naming convention `task-<descriptive-name>.md`. The name should indicate the **scenario**, not the expected outcome.

```markdown
---
agent: business-product
type: happy-path
description: SaaS analytics platform with clear revenue model
expected_outcome: pass
---

# Task: SaaS Analytics Platform

## Context
Brief description of what this scenario tests and why.

## Input
The actual project description to feed to the agent. Include:
- Project overview
- Tech stack and dependencies
- File structure
- Key features (present and missing)
- Any relevant configs

## Expected Behaviors
- Agent should identify X
- Agent should flag Y
- Agent should recommend Z

## Success Criteria
- [ ] Section X is present in output
- [ ] Score is within expected range
- [ ] Specific finding Z appears

## Anti-Criteria (Agent Should NOT)
- [ ] Should NOT fabricate features
- [ ] Should NOT give perfect scores
```

### 3. Task Types

| Type | Purpose | Example |
|------|---------|---------|
| `happy-path` | Agent should produce complete, well-structured output | Well-built SaaS project |
| `edge-case` | Agent should adapt to unusual or limited input | Empty repo, minimal info |
| `negative` | Agent should flag issues or handle what's missing | No revenue model, no tests |

### 4. Writing Good Tasks

- **Be unambiguous**: Two reviewers should independently agree on pass/fail
- **Include enough input detail**: The agent needs realistic context to produce meaningful output
- **Define anti-criteria**: Specify what the agent should NOT do (prevents false positives)
- **Test one thing well**: Don't overload a task with too many expectations
- **Balance the suite**: Each agent should have a mix of happy-path, edge-case, and negative tasks

## Adding a New Grader Check

### Code-Based Graders

Code-based graders are bash scripts in `evaluation/graders/code-based/`.

#### Using Common Utilities

Source `common.sh` for shared validation functions:

```bash
source "$(dirname "$0")/common.sh"

# Available functions:
check_section_present "$file" "Section Name"      # Heading exists
check_score_format "$file" "Score.*[0-9]+/10"     # Score in valid range
check_table_present "$file" "Header.*Pattern"     # Table with matching header
check_table_columns "$file" "Header" 4            # Min column count
check_checklist_present "$file"                   # Has checklist items
check_bullet_count "$file" "Section" 3            # Min bullets under heading
check_word_count "$file" 500                      # Min word count
check_no_placeholder "$file"                      # No [TODO], $X, etc.
check_contains "$file" "pattern" "name" "msg"     # Regex pattern match
```

#### Adding a Check to an Existing Grader

1. Open `evaluation/graders/code-based/grade-<agent>.sh`
2. Add your check using the common functions
3. Run syntax check: `bash -n grade-<agent>.sh`
4. Test against a known-good output file

#### Adding a Reusable Check to common.sh

If your check is useful across multiple agents:

1. Add the function to `evaluation/graders/code-based/common.sh`
2. Follow the naming convention: `check_<what_it_validates>`
3. Use `check_pass`/`check_fail` for result tracking
4. Test with `bash -n common.sh`

## Modifying a Model-Based Rubric

Model-based rubrics are markdown files in `evaluation/graders/model-based/`.

### Rubric Structure

Each rubric has 5 weighted dimensions scored 1-5:

```markdown
## Dimension N: Name (Weight: XX%)

Description of what this dimension measures.

- **5**: Excellence criteria
- **4**: Good criteria
- **3**: Adequate criteria
- **2**: Below adequate criteria
- **1**: Failure criteria

### Good Example
> Concrete example of 4-5 quality output

### Bad Example
> Concrete example of 1-2 quality output
```

### Rules

- Weights must sum to 100%
- Each dimension needs clear 1-5 score anchors
- Include at least one Good Example and one Bad Example per dimension
- Pass threshold: >= 3.5, Marginal: 2.5-3.49, Fail: < 2.5

### Adding a Dimension

If replacing an existing dimension, maintain the same weight distribution principle. If you need more than 5 dimensions, consider splitting into sub-dimensions within an existing one.

## Running Your Eval Locally

```bash
# Grade an existing output file
bash evaluation/harness/run-eval.sh \
  --agent business-product \
  --task evaluation/tasks/business-product/task-saas-happy-path.md \
  --grader-only \
  --output path/to/agent-output.md

# Run all tasks for one agent (requires claude CLI)
bash evaluation/harness/run-all.sh --agent business-product

# Run the full suite
bash evaluation/harness/run-all.sh

# Generate a report
bash evaluation/harness/report.sh
```

## Checklist Before Submitting

- [ ] Task file has valid YAML frontmatter (agent, type, description, expected_outcome)
- [ ] Task has all required sections (Context, Input, Expected Behaviors, Success Criteria, Anti-Criteria)
- [ ] Grader scripts pass syntax check (`bash -n`)
- [ ] Rubric weights sum to 100%
- [ ] Good/Bad examples provided for rubric dimensions
- [ ] Tested locally with at least one output file
