# Model-Based Grader: Technical Architecture Agent

## Instructions

You are evaluating the output of an OmniLabs Technical Architecture agent. This agent evaluates system architecture across 6 dimensions (Scalability, Reliability, Maintainability, Security, Observability, Operability) by reading actual code, tracing request flows, and examining infrastructure configurations.

Score each dimension 1-5. Provide a brief justification for each score. Then compute the weighted average.

---

## Dimension 1: Technical Accuracy (Weight: 30%)

Are the dimension scores justified and accurate based on evidence?

- **5**: Scores match the actual evidence. No inflated scores for dimensions that clearly have issues. Correctly identifies patterns and anti-patterns. Trade-offs between dimensions are discussed.
- **4**: Scores are mostly accurate. Minor inflation in 1-2 dimensions.
- **3**: Some scores feel disconnected from the evidence. Mix of accurate and generous scoring.
- **2**: Multiple scores don't match the evidence. Consistently inflated or deflated.
- **1**: Scores appear arbitrary or disconnected from analysis.

### Good Example
> "Observability: 2/10 — No structured logging found (all `console.log` calls). No metrics collection, no distributed tracing, no error tracking service integration. The only monitoring is a basic health check endpoint at `/api/health` that returns `{status: 'ok'}` without checking dependencies."

### Bad Example
> "Observability: 6/10 — The application has some logging in place and could benefit from more monitoring."

---

## Dimension 2: Code Grounding (Weight: 25%)

Are findings traced to specific files and code patterns?

- **5**: Every finding cites specific files and line ranges. Identifies actual anti-patterns with code examples. Distinguishes real issues from hypothetical ones.
- **4**: Most findings reference specific files. Some general observations.
- **3**: Mix of specific references and generic statements.
- **2**: Few code references. Analysis reads as generic architecture review.
- **1**: No code references.

---

## Dimension 3: Dimension Coverage (Weight: 20%)

Are all 6 dimensions thoroughly evaluated?

- **5**: All 6 dimensions receive substantive analysis (not just a score and one sentence). Trade-offs between dimensions discussed. Sub-dimensions within each category are explored.
- **4**: All 6 dimensions covered. Most have detailed analysis.
- **3**: All dimensions scored but some get one-sentence treatment.
- **2**: 1-2 dimensions missing or perfunctory.
- **1**: Fewer than 4 dimensions meaningfully covered.

---

## Dimension 4: Prioritization Quality (Weight: 15%)

Are findings properly ranked and roadmap logically sequenced?

- **5**: Critical findings are correctly ranked by severity and impact. Effort/impact trade-offs are realistic. Roadmap is sequenced logically (prerequisites before dependents). Quick wins are genuinely quick.
- **4**: Good prioritization with minor sequencing issues.
- **3**: Findings listed but prioritization feels arbitrary.
- **2**: No clear prioritization. Everything seems equally important.
- **1**: No roadmap or clearly unrealistic prioritization.

---

## Dimension 5: Constructiveness (Weight: 10%)

Does the analysis provide solutions, not just problems?

- **5**: Every finding includes a concrete solution with alternatives. Trade-offs between solutions discussed. Acknowledges what is done well, not just what's broken.
- **4**: Most findings include solutions. Some acknowledgment of strengths.
- **3**: Solutions are generic. Focus is predominantly on problems.
- **2**: Problem-focused with minimal solutions.
- **1**: Pure criticism with no constructive guidance.

---

## Scoring

```
Weighted Score = (D1 * 0.30) + (D2 * 0.25) + (D3 * 0.20) + (D4 * 0.15) + (D5 * 0.10)
```

| Verdict | Score Range |
|---------|-------------|
| **PASS** | >= 3.5 |
| **MARGINAL** | 2.5 — 3.49 |
| **FAIL** | < 2.5 |

## Output Format

```
Dimension 1 (Technical Accuracy):    X/5 — [justification]
Dimension 2 (Code Grounding):        X/5 — [justification]
Dimension 3 (Dimension Coverage):    X/5 — [justification]
Dimension 4 (Prioritization Quality): X/5 — [justification]
Dimension 5 (Constructiveness):      X/5 — [justification]

Weighted Score: X.XX/5
Verdict: PASS / MARGINAL / FAIL
Key Strength: [one sentence]
Key Weakness: [one sentence]
```
