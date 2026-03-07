# OmniLabs — Analysis Prompt

Copy and paste the prompt below into Claude Code to launch a full multi-perspective analysis of your project.

---

## How it works

Claude Code orchestrates 5 subagents defined in `.claude/agents/`. The main conversation delegates to each subagent, which runs in its own context with read-only access to your codebase. Subagents cannot spawn other subagents — Claude Code handles all orchestration.

```
Claude Code (main conversation = orchestrator)
    |
    |-- delegates to 4 analyst subagents in parallel:
    |       business-product (Sonnet)
    |       financial-cost (Sonnet)
    |       technical-architecture (Sonnet)
    |       devils-advocate (Sonnet)
    |
    |-- waits for all 4 to return results
    |
    |-- delegates to lead-synthesis (Opus) with all 4 reports as context
    |
    |-- lead-synthesis produces the OmniLabs Report + saves dashboard
```

---

## Full Analysis Prompt

```
Run a full OmniLabs strategic analysis of this project.

Use the following subagents from .claude/agents/:

1. Launch these 4 subagents IN PARALLEL to analyze the codebase:
   - business-product — Market opportunity, PMF, competitive landscape, GTM
   - financial-cost — Infrastructure costs, TCO at 1K/10K/100K/1M users, ROI
   - technical-architecture — Architecture scoring across 6 dimensions (1-10)
   - devils-advocate — Stress-test findings, challenge assumptions, pre-mortem

2. WAIT for all 4 subagents to complete and collect their full reports.

3. Launch the lead-synthesis subagent, passing it ALL 4 analyst reports as context. It will:
   - Synthesize findings into the OmniLabs Report
   - Make a GO / NO-GO / CONDITIONAL GO decision
   - Score all dimensions and produce a 30/60/90-day roadmap
   - Save results to the dashboard (scripts/save-report.sh + scripts/generate-dashboard.sh --open)

The devil's advocate should specifically reference and challenge findings from the other 3 analysts.
```

---

## Individual Agent Prompts

For deeper, more detailed individual analyses, use the dedicated prompt files below. Each contains a comprehensive, structured prompt with specific evaluation criteria and output expectations.

| Agent | Prompt File |
|-------|-------------|
| Business & Product | [`business-product-analysis.md`](business-product-analysis.md) |
| Financial & Cost | [`financial-cost-analysis.md`](financial-cost-analysis.md) |
| Technical Architecture | [`technical-architecture-review.md`](technical-architecture-review.md) |
| Devil's Advocate | [`devil-advocate-challenge.md`](devil-advocate-challenge.md) |

Copy the contents of any prompt file above and paste it into Claude Code for a focused deep-dive on that dimension.

---

## Tips

- **First run**: Start with the full analysis to get a comprehensive baseline
- **Focused deep-dives**: Use individual agent prompts when you need depth in one dimension
- **Iterative analysis**: After making changes, re-run specific agents to validate improvements
- **Custom context**: Add specific questions or concerns to the prompts for targeted analysis
