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
```

---

## Individual Agent Prompts

### Business & Product Analysis Only

```
Use the business-product agent to analyze this project's market opportunity, product-market fit, and competitive positioning. Read the codebase to understand what it actually does, then evaluate its business viability.
```

### Financial & Cost Analysis Only

```
Use the financial-cost agent to model the costs of this project. Examine the codebase for dependencies, infrastructure configs, and service integrations. Calculate TCO at 1K, 10K, 100K, and 1M user scales.
```

### Technical Architecture Review Only

```
Use the technical-architecture agent to evaluate this project's architecture. Score it across 6 dimensions (scalability, reliability, maintainability, security, observability, operability) with evidence from the actual code.
```

### Devil's Advocate Challenge Only

```
Use the devils-advocate agent to stress-test this project. Challenge assumptions baked into the architecture, identify blind spots, and run a pre-mortem analysis. Every challenge must be backed by evidence from the code.
```

---

## Tips

- **First run**: Start with the full analysis to get a comprehensive baseline
- **Focused deep-dives**: Use individual agent prompts when you need depth in one dimension
- **Iterative analysis**: After making changes, re-run specific agents to validate improvements
- **Custom context**: Add specific questions or concerns to the prompts for targeted analysis
