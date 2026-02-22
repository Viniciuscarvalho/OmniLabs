# OmniLabs — Multi-Perspective Strategic Analysis Framework

## What is OmniLabs?

OmniLabs is a plug-and-play agent teams framework for Claude Code that provides multi-perspective strategic analysis for any project. It deploys 5 specialized agents that analyze your project from business, financial, technical, and adversarial perspectives, then synthesizes everything into a single actionable report.

## Agent Team

| Agent | Role | Model |
|-------|------|-------|
| `business-product` | Market opportunity, PMF, competitive analysis, GTM | Sonnet |
| `financial-cost` | Cost modeling, TCO, ROI, build-vs-buy | Sonnet |
| `technical-architecture` | Scalability, reliability, security, maintainability | Sonnet |
| `devils-advocate` | Risk assessment, assumption challenging, blind spots | Sonnet |
| `lead-synthesis` | Orchestration, synthesis, final OmniLabs Report | **Opus** |

## How to Use

1. Copy the `.claude/` folder into your project root
2. Open Claude Code in your project
3. Use the prompt from `agent-team-prompt.md` to launch the full analysis
4. Or invoke individual agents directly for focused analysis

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
