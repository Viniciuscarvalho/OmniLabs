# OmniLabs — Agent Team Prompt

Copy and paste the prompt below into Claude Code to launch a full multi-perspective analysis of your project.

---

## Full Analysis Prompt

```
Run a full OmniLabs strategic analysis of this project.

Create a team called "omnilabs-analysis" with 5 agents:

1. **business-product** (Sonnet) — Analyze market opportunity, product-market fit, competitive landscape, and go-to-market strategy. Read the codebase to understand what the product actually does.

2. **financial-cost** (Sonnet) — Model infrastructure costs, calculate TCO at different scales (1K/10K/100K/1M users), evaluate build-vs-buy decisions, and project ROI. Examine package manifests, configs, and env vars for cost signals.

3. **technical-architecture** (Sonnet) — Evaluate system architecture across 6 dimensions: scalability, reliability, maintainability, security, observability, and operability. Score each 1-10 with evidence from code.

4. **devils-advocate** (Sonnet) — Stress-test all findings from the other 3 analysts. Challenge assumptions with evidence from code. Run pre-mortem analysis, identify blind spots, and strengthen recommendations through constructive challenge.

5. **lead-synthesis** (Opus) — Wait for all 4 analysts to complete. Then synthesize their findings into the OmniLabs Report: GO/NO-GO/CONDITIONAL GO decision, dimension scores, consensus vs contested findings, risk matrix, and 30/60/90-day implementation roadmap.

Run analysts 1-4 in parallel. Agent 5 (lead-synthesis) should start only after all 4 analysts have completed their reports. The devil's advocate should specifically reference and challenge findings from the other 3 analysts.

IMPORTANT: After the lead-synthesis agent produces the final OmniLabs Report, it MUST also save a structured JSON summary to the dashboard by running `bash scripts/save-report.sh "<project-name>"` and writing the summary.json to the returned directory. Then run `bash scripts/generate-dashboard.sh --open` to update and open the dashboard in the browser.
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
