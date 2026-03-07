# OmniLabs — Multi-Perspective Strategic Analysis Framework

## What is OmniLabs?

OmniLabs is a plug-and-play subagent framework for Claude Code that provides multi-perspective strategic analysis for any project. It deploys 5 specialized subagents that analyze your project from business, financial, technical, and adversarial perspectives, then synthesizes everything into a single actionable report.

## Subagents

| Agent | Role | Model |
|-------|------|-------|
| `business-product` | Market opportunity, PMF, competitive analysis, GTM | Sonnet |
| `financial-cost` | Cost modeling, TCO, ROI, build-vs-buy | Sonnet |
| `technical-architecture` | Scalability, reliability, security, maintainability | Sonnet |
| `devils-advocate` | Risk assessment, assumption challenging, blind spots | Sonnet |
| `lead-synthesis` | Synthesis, final OmniLabs Report with GO/NO-GO decision | **Opus** |

All subagents are defined in `.claude/agents/` and follow the official Claude Code subagent spec. The main Claude Code conversation orchestrates them — subagents do not spawn other subagents.

## How to Use

1. Copy the `.claude/` folder into your project root
2. Open Claude Code in your project
3. Paste: `Run a full OmniLabs strategic analysis of this project.`
4. Claude Code launches 4 analysts in parallel, then passes results to lead-synthesis
5. Or invoke individual subagents directly for focused analysis

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
