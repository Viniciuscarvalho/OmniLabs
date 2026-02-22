# Model-Based Grader: Lead Synthesis Agent

## Instructions

You are evaluating the output of an OmniLabs Lead Synthesis agent. This agent orchestrates and synthesizes findings from all 4 analyst agents into the final OmniLabs Report with a GO/NO-GO/CONDITIONAL GO decision, dimension scores, consensus/contested findings, risk matrix, and implementation roadmap.

Score each dimension 1-5. Provide a brief justification for each score. Then compute the weighted average.

---

## Dimension 1: Synthesis Quality (Weight: 30%)

Does the agent genuinely synthesize across analysts or merely summarize?

- **5**: Finds patterns and insights that emerge from combining multiple analyst perspectives. Convergence/divergence analysis reveals non-obvious connections. Composite score weighting is transparent and justified. The whole is greater than the sum of its parts.
- **4**: Good synthesis with some original cross-cutting insights. Weighting explained.
- **3**: Mostly summarizes each analyst's findings sequentially. Some synthesis attempts.
- **2**: Pure summary — reads like a table of contents of the 4 reports.
- **1**: Missing or incoherent synthesis.

### Good Example
> "Convergence: All 4 analysts agree that observability is the critical gap — Business flagged it as churn risk, Financial identified $0 current monitoring spend (technical debt accumulating), Technical scored it 2/10, and Devil's Advocate identified it as the most likely failure trigger. This convergence makes observability the highest-priority investment with cross-dimensional ROI."

### Bad Example
> "The business analyst found market opportunity. The financial analyst modeled costs. The technical analyst scored the architecture. The devil's advocate identified risks."

---

## Dimension 2: Decision Clarity (Weight: 25%)

Is the GO/NO-GO/CONDITIONAL GO decision clearly stated with rationale?

- **5**: Decision is unambiguous. Rationale directly connects to analyst findings. Conditions for CONDITIONAL GO are specific, measurable, and verifiable. Confidence level is calibrated to the strength of evidence.
- **4**: Clear decision with good rationale. Conditions mostly specific.
- **3**: Decision present but rationale is thin. Conditions are vague.
- **2**: Decision stated without meaningful rationale.
- **1**: No clear decision or contradictory signals.

---

## Dimension 3: Conflict Resolution (Weight: 20%)

How well does the agent handle disagreements between analysts?

- **5**: Contested findings identify the stronger argument using the evidence hierarchy (code > quantitative > qualitative > industry patterns). Does not dodge disagreements or present false consensus. Explains why one analyst's position is favored.
- **4**: Most conflicts addressed with reasoning. Some are left unresolved.
- **3**: Conflicts acknowledged but resolved by splitting the difference or averaging.
- **2**: Conflicts minimized or ignored.
- **1**: No awareness of disagreements between analysts.

---

## Dimension 4: Completeness (Weight: 15%)

Are all analyst perspectives represented in the synthesis?

- **5**: All 4 analyst reports are referenced. No analyst's findings are ignored. Roadmap covers critical findings from all analysts. Blind spots section adds genuinely new observations.
- **4**: All analysts referenced. Most critical findings included.
- **3**: One analyst's perspective underrepresented.
- **2**: One or more analysts effectively ignored.
- **1**: Synthesis based on fewer than 3 analysts.

---

## Dimension 5: Actionability (Weight: 10%)

Is the implementation roadmap specific and executable?

- **5**: Roadmap items are SMART (Specific, Measurable, Achievable, Relevant, Time-bound). Metrics to track are specific and measurable. Clear ownership suggested. Phasing is logical with dependencies.
- **4**: Good roadmap with mostly specific items. Some metrics defined.
- **3**: Roadmap exists but items are vague. No metrics.
- **2**: Generic action items ("improve security", "add monitoring").
- **1**: No roadmap or clearly infeasible plan.

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
Dimension 1 (Synthesis Quality):    X/5 — [justification]
Dimension 2 (Decision Clarity):     X/5 — [justification]
Dimension 3 (Conflict Resolution):  X/5 — [justification]
Dimension 4 (Completeness):         X/5 — [justification]
Dimension 5 (Actionability):        X/5 — [justification]

Weighted Score: X.XX/5
Verdict: PASS / MARGINAL / FAIL
Key Strength: [one sentence]
Key Weakness: [one sentence]
```
