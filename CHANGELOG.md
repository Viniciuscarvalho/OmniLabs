# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.1.0] - 2026-02-22

### Added

- Complete evaluation framework for validating agent output quality
- Code-based graders (bash) for all 5 agents with deterministic structural validation
- Model-based rubrics (LLM-as-Judge) with 5 weighted dimensions per agent
- 19 evaluation tasks across happy-path, edge-case, and negative scenarios
- 3 golden reference datasets (SaaS, high-risk DeFi, pre-MVP)
- Evaluation harness: `run-eval.sh`, `run-all.sh`, `report.sh` with regression detection
- Shared grader utilities in `common.sh` (section checks, score validation, table validation)
- Documentation: `architecture.md`, `evaluation-guide.md`, `contributing-evals.md`
- GitHub Actions CI workflows: `lint.yml` (agent/task frontmatter) and `eval.yml` (grader validation)
- `--with-evals` flag on `install.sh` for opt-in eval framework installation
- Expanded README with detailed evaluation framework section and eval architecture diagram

## [1.0.0] - 2026-02-21

### Added

- Initial release of OmniLabs agent teams framework
- 5 specialized agents: business-product, financial-cost, technical-architecture, devils-advocate, lead-synthesis
- Agent team orchestration prompt (`agent-team-prompt.md`)
- Individual agent deep-dive prompts (4 detailed prompt files)
- Smart installer with fresh/merge modes (`install.sh`)
- Project settings with agent teams enabled (`.claude/settings.json`)
- CLAUDE.md project instructions
- Example scenarios: SaaS evaluation, technical migration, market entry
- README with visual identity, banner, badges, and architecture diagram
