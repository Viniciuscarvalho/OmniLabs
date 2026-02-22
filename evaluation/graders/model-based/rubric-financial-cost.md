# Model-Based Grader: Financial & Cost Agent

## Instructions

You are evaluating the output of an OmniLabs Financial & Cost agent. This agent models infrastructure costs, calculates TCO, evaluates build-vs-buy decisions, and projects ROI by examining actual codebase dependencies and configurations.

Score each dimension 1-5. Provide a brief justification for each score. Then compute the weighted average.

---

## Dimension 1: Financial Rigor (Weight: 30%)

How correctly and thoroughly are financial frameworks applied?

- **5**: Uses proper TCO methodology. NPV/IRR calculations with explicit discount rates. Cost categories are MECE (mutually exclusive, collectively exhaustive). Distinguishes CapEx from OpEx. Hidden costs (training, migration, on-call) explicitly included.
- **4**: Solid TCO breakdown. Most cost categories covered. Some hidden costs mentioned.
- **3**: Basic cost breakdown. Missing some categories. No NPV/IRR.
- **2**: Rough estimates without methodology. Major cost categories missing.
- **1**: No meaningful financial analysis.

### Good Example
> "Current monthly cost: $847 (Compute: $320 ECS Fargate, Storage: $187 RDS db.t3.medium + $40 S3, Network: $120 CloudFront + data transfer, Services: $180 Auth0 Developer Pro). Hidden costs add ~1.8x multiplier: $430/mo estimated for on-call engineering time (0.25 FTE at $200K loaded) and $90/mo CI/CD compute."

### Bad Example
> "Infrastructure costs are estimated at around $1,000 per month. This could increase at scale."

---

## Dimension 2: Code Grounding (Weight: 25%)

Are cost estimates derived from actual codebase artifacts?

- **5**: Every cost item traces to a specific config file, dependency, or infrastructure definition. References `package.json`, Dockerfiles, terraform files, CI configs, and environment variables by name.
- **4**: Most costs reference specific dependencies or configs.
- **3**: Some code references. Mix of actual and hypothetical costs.
- **2**: Mostly assumed costs with occasional reference to the codebase.
- **1**: No connection to the actual codebase.

---

## Dimension 3: Scaling Accuracy (Weight: 20%)

Are scaling projections realistic and non-linear?

- **5**: Models non-linear cost curves with inflection points. Identifies which components scale sub-linearly (storage), linearly (compute), and super-linearly (database connections). Distinguishes fixed from variable costs.
- **4**: Scaling projections show non-linear awareness. Some inflection points identified.
- **3**: Scaling projections exist but are mostly linear multipliers.
- **2**: Simple multiplication of base costs by user count.
- **1**: No scaling projections or clearly unrealistic numbers.

### Good Example
> "At 10K users, Postgres connections become the bottleneck (max_connections=100 on db.t3.medium). Options: upgrade to db.r5.large (+$280/mo) or add PgBouncer ($0/mo but requires ops effort). Cost curve inflects again at ~25K users where read replicas become necessary (+$400/mo)."

### Bad Example
> "At 100K users, costs will be approximately 100x the current costs."

---

## Dimension 4: Optimization Quality (Weight: 15%)

Are cost reduction recommendations specific and implementable?

- **5**: Specific strategies with estimated dollar savings. Distinguishes quick wins from strategic changes. Includes effort/impact trade-offs. Considers architectural alternatives.
- **4**: Clear recommendations with some savings estimates.
- **3**: Generic optimization suggestions without quantification.
- **2**: Vague suggestions ("use reserved instances", "optimize queries").
- **1**: No optimization recommendations.

---

## Dimension 5: Risk Calibration (Weight: 10%)

Are financial risks and uncertainties properly identified?

- **5**: Identifies cost variance ranges. Worst-case scenarios quantified. Vendor lock-in risks with switching cost estimates. Bear/base/bull projections.
- **4**: Key financial risks identified with some quantification.
- **3**: Risks mentioned but not quantified.
- **2**: Passing mention of cost risks.
- **1**: No financial risk discussion.

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
Dimension 1 (Financial Rigor):    X/5 — [justification]
Dimension 2 (Code Grounding):     X/5 — [justification]
Dimension 3 (Scaling Accuracy):   X/5 — [justification]
Dimension 4 (Optimization Quality): X/5 — [justification]
Dimension 5 (Risk Calibration):   X/5 — [justification]

Weighted Score: X.XX/5
Verdict: PASS / MARGINAL / FAIL
Key Strength: [one sentence]
Key Weakness: [one sentence]
```
