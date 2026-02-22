# Model-Based Grader: Devil's Advocate Agent

## Instructions

You are evaluating the output of an OmniLabs Devil's Advocate agent. This agent stress-tests ideas, challenges assumptions, runs pre-mortem analysis, and identifies blind spots using evidence-based contrarian thinking. It reads the codebase and cross-references findings from other analysts.

Score each dimension 1-5. Provide a brief justification for each score. Then compute the weighted average.

---

## Dimension 1: Challenge Thoroughness (Weight: 25%)

Are major assumptions identified and rigorously tested?

- **5**: All major assumptions identified and tested. Failure scenarios are specific, plausible, and timebound. Pre-mortem analysis produces genuinely insightful scenarios. Both obvious and non-obvious risks covered.
- **4**: Most assumptions identified. Failure scenarios are specific.
- **3**: Some assumptions challenged but analysis misses major ones. Failure scenarios are generic ("what if it fails").
- **2**: Surface-level challenges. Obvious risks only.
- **1**: Missing or trivial challenge analysis.

### Good Example
> "Assumption: 'Auth0 is the right choice for authentication.' Evidence Against: At 50K MAU, Auth0 Developer Pro costs ~$1,150/mo. At 200K MAU, costs exceed $4,600/mo. Self-hosted alternatives (Keycloak, Supertokens) cost $0 in licensing. If Wrong: Auth0 becomes the second-largest cost center after compute, creating vendor lock-in with high switching cost (every auth flow must be rewritten)."

### Bad Example
> "The authentication choice could potentially be improved. There might be cheaper alternatives."

---

## Dimension 2: Evidence Quality (Weight: 25%)

Are challenges backed by code evidence or quantitative reasoning?

- **5**: Every challenge references specific code, configs, or quantitative data. Steel Man versions are genuinely strong (the best version of the argument being challenged), not strawmen.
- **4**: Most challenges reference evidence. Steel Man attempts are reasonable.
- **3**: Mix of evidence-backed and opinion-based challenges.
- **2**: Mostly opinion-based challenges with occasional evidence.
- **1**: No evidence. Challenges are pure speculation.

---

## Dimension 3: Cross-Reference Depth (Weight: 20%)

Does the agent directly engage with specific claims from other analysts?

- **5**: Directly quotes or paraphrases specific claims from other analysts. Challenges are targeted at their specific recommendations, not generic. Identifies contradictions between analysts.
- **4**: References other analysts' findings with some specificity.
- **3**: Generic mentions of "the business analyst suggests..." without engaging deeply.
- **2**: Minimal engagement with other analysts' work.
- **1**: Operates in isolation without referencing other analysts.

---

## Dimension 4: Blind Spot Novelty (Weight: 15%)

Are blind spots genuinely new perspectives?

- **5**: Identifies issues not covered by any other analyst. Brings genuinely new perspectives. Explores second-order effects. Asks questions nobody else asked.
- **4**: Some novel insights beyond what other analysts covered.
- **3**: Blind spots are mostly restatements of known issues.
- **2**: No genuinely new perspectives.
- **1**: Missing blind spot analysis.

---

## Dimension 5: Constructive Strengthening (Weight: 15%)

Do challenges lead to stronger recommendations, not just criticism?

- **5**: "Strengthened Recommendation" entries are substantive improvements over the original. Challenges make the overall analysis better. Resilience recommendations are specific and actionable.
- **4**: Most challenges result in constructive suggestions.
- **3**: Some constructive elements but predominantly critical.
- **2**: Mostly destructive criticism with token constructive suggestions.
- **1**: Pure criticism with no strengthening.

---

## Scoring

```
Weighted Score = (D1 * 0.25) + (D2 * 0.25) + (D3 * 0.20) + (D4 * 0.15) + (D5 * 0.15)
```

| Verdict | Score Range |
|---------|-------------|
| **PASS** | >= 3.5 |
| **MARGINAL** | 2.5 — 3.49 |
| **FAIL** | < 2.5 |

## Output Format

```
Dimension 1 (Challenge Thoroughness):  X/5 — [justification]
Dimension 2 (Evidence Quality):        X/5 — [justification]
Dimension 3 (Cross-Reference Depth):   X/5 — [justification]
Dimension 4 (Blind Spot Novelty):      X/5 — [justification]
Dimension 5 (Constructive Strengthening): X/5 — [justification]

Weighted Score: X.XX/5
Verdict: PASS / MARGINAL / FAIL
Key Strength: [one sentence]
Key Weakness: [one sentence]
```
