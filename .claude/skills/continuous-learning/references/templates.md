# Memory Templates

Reference file for the continuous-learning skill. Load this when creating or updating memories
to use the appropriate template structure.

---

## Learning Template

Use for debugging discoveries, workarounds, non-obvious patterns, and error resolutions.

```markdown
# Learning: [Title]

## Context
- **Date**: [YYYY-MM-DD]
- **Domain**: [analysis|evaluation|agent|framework|tooling|debugging]
- **Tags**: [comma-separated keywords]
- **Trigger**: [what led to this discovery]

## Problem
[Clear description of the problem encountered]

## Trigger Conditions
[When does this occur? Include exact error messages, symptoms, scenarios]

## Solution
[Step-by-step solution or workaround]

## Verification
[How to verify the solution worked]

## Example
[Concrete code example or analysis excerpt]

## Notes
[Caveats, edge cases, related considerations]

## References
[Links to documentation, articles, related memories]
```

---

## Decision Template (ADR-Inspired)

Use for architecture choices, methodology decisions, tool selections, or patterns with meaningful trade-offs.

```markdown
# Decision: [Title]

## Context
- **Date**: [YYYY-MM-DD]
- **Domain**: [analysis|evaluation|agent|framework|tooling|debugging]
- **Tags**: [comma-separated keywords]
- **Status**: [active|superseded|under-review]

## Decision
[One-sentence summary of what was decided]

## Background
[Why this decision was needed. What problem or question prompted it?]

## Options Considered
1. **[Option A]**: [Brief description] — Pros: [pros] / Cons: [cons]
2. **[Option B]**: [Brief description] — Pros: [pros] / Cons: [cons]

## Choice
[Which option was selected and why]

## Consequences
- **Positive**: [expected benefits]
- **Negative**: [known tradeoffs]

## Scope
[Where does this apply? Whole framework? Specific agents? Specific scenarios?]

## Examples
[Code or analysis examples showing the decision in practice]

## Review Trigger
[Conditions under which this decision should be revisited]
```

---

## Simplified Decision Template

Use for straightforward preferences without complex trade-offs.

```markdown
# Decision: [Title]

## Decision
[What was decided]

## Rationale
[Why this choice]

## Examples
[How to apply it]
```

---

## Analysis Pattern Template

Use for recurring strategic analysis approaches, scoring patterns, or methodology insights specific to OmniLabs.

```markdown
# Analysis Pattern: [Title]

## Context
- **Date**: [YYYY-MM-DD]
- **Domain**: analysis
- **Tags**: [comma-separated keywords]
- **Agent(s)**: [which OmniLabs agent(s) this applies to]
- **Scenario Type**: [happy-path|edge-case|negative]

## Pattern Description
[What pattern was observed in strategic analysis]

## When to Apply
[Specific conditions or project characteristics that trigger this pattern]

## Example Application
[Concrete example from an analysis session]

## Anti-Pattern
[What NOT to do — the mistake this pattern prevents]

## Impact on Scoring
[How this pattern affects agent scoring behavior, if applicable]
```

---

## Eval Finding Template

Use for evaluation insights about agent behavior, grader results, or rubric calibration.

```markdown
# Eval Finding: [Title]

## Context
- **Date**: [YYYY-MM-DD]
- **Domain**: evaluation
- **Tags**: [comma-separated keywords]
- **Agent**: [which agent was evaluated]
- **Task**: [which eval task surfaced this]

## Finding
[What the evaluation revealed]

## Root Cause
[Why the agent behaved this way — trace to prompt section if possible]

## Resolution
[What prompt change, grader update, or task modification fixes this]

## Verification
[How to verify the fix — specific eval commands]

## Regression Risk
[What could break if this fix is applied]
```
