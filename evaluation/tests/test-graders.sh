#!/usr/bin/env bash
# OmniLabs Grader Test Suite
# Tests that graders correctly PASS golden outputs and FAIL broken outputs.
# Usage: bash evaluation/tests/test-graders.sh
#
# Exit codes: 0 = all tests pass, 1 = failures detected

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
GOLDEN_DIR="${PROJECT_ROOT}/evaluation/golden-outputs"
GRADER_DIR="${PROJECT_ROOT}/evaluation/graders/code-based"
BROKEN_DIR=$(mktemp -d)

trap 'rm -rf "$BROKEN_DIR"' EXIT

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

TOTAL=0
PASSED=0
FAILED=0

test_pass() {
  TOTAL=$((TOTAL + 1))
  PASSED=$((PASSED + 1))
  echo -e "  ${GREEN}PASS${NC} $1"
}

test_fail() {
  TOTAL=$((TOTAL + 1))
  FAILED=$((FAILED + 1))
  echo -e "  ${RED}FAIL${NC} $1"
}

# === PHASE 1: Golden outputs should PASS all graders ===
echo -e "${BLUE}Phase 1: Golden outputs should PASS${NC}"
echo "════════════════════════════════════════════"

run_golden_test() {
  local agent="$1"
  local grader_name="$2"
  local golden="${GOLDEN_DIR}/golden-${agent}.md"
  local grader="${GRADER_DIR}/${grader_name}"

  if [[ ! -f "$golden" ]]; then
    test_fail "${agent}: golden output missing (${golden})"
    return
  fi
  if [[ ! -f "$grader" ]]; then
    test_fail "${agent}: grader missing (${grader})"
    return
  fi

  if bash "$grader" "$golden" >/dev/null 2>&1; then
    test_pass "${agent}: golden output passes all checks"
  else
    test_fail "${agent}: golden output FAILED grader (should pass)"
  fi
}

run_golden_test "business-product" "grade-business-product.sh"
run_golden_test "financial-cost"   "grade-financial-cost.sh"
run_golden_test "technical-arch"   "grade-technical-arch.sh"
run_golden_test "devils-advocate"  "grade-devils-advocate.sh"
run_golden_test "lead-synthesis"   "grade-lead-synthesis.sh"

echo ""

# === PHASE 2: Broken outputs should FAIL ===
echo -e "${BLUE}Phase 2: Broken outputs should FAIL${NC}"
echo "════════════════════════════════════════════"

# --- 2a. Empty file should fail all graders ---
echo "" > "${BROKEN_DIR}/empty.md"

run_broken_test() {
  local agent="$1"
  local grader_name="$2"
  local broken_file="$3"
  local desc="$4"
  local grader="${GRADER_DIR}/${grader_name}"

  if bash "$grader" "$broken_file" >/dev/null 2>&1; then
    test_fail "${agent}: ${desc} should FAIL but PASSED"
  else
    test_pass "${agent}: ${desc} correctly fails"
  fi
}

run_broken_test "business-product" "grade-business-product.sh" "${BROKEN_DIR}/empty.md" "empty file"
run_broken_test "financial-cost"   "grade-financial-cost.sh"   "${BROKEN_DIR}/empty.md" "empty file"
run_broken_test "technical-arch"   "grade-technical-arch.sh"   "${BROKEN_DIR}/empty.md" "empty file"
run_broken_test "devils-advocate"  "grade-devils-advocate.sh"  "${BROKEN_DIR}/empty.md" "empty file"
run_broken_test "lead-synthesis"   "grade-lead-synthesis.sh"   "${BROKEN_DIR}/empty.md" "empty file"

echo ""

# --- 2b. Missing sections should fail ---
# Business: output with score but no sections
cat > "${BROKEN_DIR}/missing-sections-bp.md" << 'EOF'
# Analysis Report
Market Opportunity Score: 7/10
Moat: Moderate
TAM SAM SOM
This is a basic report without proper sections. The competitive position has multiple entries listed below in the Competitive Position section but the sections are missing the right headings.
## Competitive Position
- Competitor A
- Competitor B
- Competitor C
word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word
EOF

if bash "${GRADER_DIR}/grade-business-product.sh" "${BROKEN_DIR}/missing-sections-bp.md" >/dev/null 2>&1; then
  test_fail "business-product: missing sections should FAIL but PASSED"
else
  test_pass "business-product: missing sections correctly fails"
fi

# --- 2c. Missing score should fail ---
cat > "${BROKEN_DIR}/no-score-fc.md" << 'EOF'
# Financial Analysis Report
## Executive Summary
This report analyzes the costs.
## Current Cost Structure
| Category | Monthly | Annual | % |
|----------|---------|--------|---|
| Compute | $500 | $6,000 | 40% |
## Scaling Projections
| Users | Monthly | Annual |
|-------|---------|--------|
| 1K | $500 | $6,000 |
| 10K | $2,000 | $24,000 |
| 100K | $15,000 | $180,000 |
| 1M | $80,000 | $960,000 |
## ROI Analysis
Cost savings of $10,000 per year.
## Cost Optimization
Several optimization strategies exist.
## Financial Risks
Market volatility and vendor lock-in are primary concerns.
word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word
EOF

if bash "${GRADER_DIR}/grade-financial-cost.sh" "${BROKEN_DIR}/no-score-fc.md" >/dev/null 2>&1; then
  test_fail "financial-cost: missing score should FAIL but PASSED"
else
  test_pass "financial-cost: missing score correctly fails"
fi

# --- 2d. Placeholder text should fail ---
golden_bp="${GOLDEN_DIR}/golden-business-product.md"
if [[ -f "$golden_bp" ]]; then
  sed 's/market opportunity/[TODO] market opportunity/' "$golden_bp" > "${BROKEN_DIR}/placeholder-bp.md"
  if bash "${GRADER_DIR}/grade-business-product.sh" "${BROKEN_DIR}/placeholder-bp.md" >/dev/null 2>&1; then
    test_fail "business-product: placeholder text should FAIL but PASSED"
  else
    test_pass "business-product: placeholder text correctly fails"
  fi
fi

# --- 2e. Missing cross-references in devils-advocate ---
cat > "${BROKEN_DIR}/no-xref-da.md" << 'EOF'
# Devil's Advocate Challenge Report
Risk Score: 6/10
## Executive Summary
A thorough risk analysis.
## Risk Heat Map
| Risk | Probability | Impact |
|------|-------------|--------|
| Market shift | High | Critical |
## Assumption Audit
Assumption 1 is Questionable. Assumption 2 is Valid.
## Failure Scenarios
### Most Likely Failure
Market downturn impacts adoption.
### Most Damaging Failure
Core product fails to retain users.
### Black Swan
Regulatory change bans the category.
## Counter-Arguments
Confidence: High — the product has strong retention.
Confidence: Medium — market timing is uncertain.
## Blind Spots
Several unexplored areas remain.
## Resilience Recommendations
Strengthen the core value proposition.
word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word
EOF

if bash "${GRADER_DIR}/grade-devils-advocate.sh" "${BROKEN_DIR}/no-xref-da.md" >/dev/null 2>&1; then
  test_fail "devils-advocate: missing cross-references should FAIL but PASSED"
else
  test_pass "devils-advocate: missing cross-references correctly fails"
fi

# --- 2f. Missing decision in lead-synthesis ---
cat > "${BROKEN_DIR}/no-decision-ls.md" << 'EOF'
# OmniLabs Strategic Analysis Report
Confidence: High
Composite Score: 7/10
## Dimension Scores
| Dimension | Score | Analyst |
|-----------|-------|---------|
| Market | 8/10 | Business |
## Consensus Findings
The team agrees on key points.
## Contested Findings
Financial and Technical analysts disagree on cost projections.
## Blind Spots
No one considered regulatory risk.
## Risk Matrix
| Risk | Probability | Impact |
|------|-------------|--------|
| Churn | Medium | High |
## Implementation Roadmap
### Phase 1
First month focus.
### Phase 2
Second month focus.
### Phase 3
Third month focus.
The Devil's Advocate raised valid concerns about market timing.
word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word
EOF

if bash "${GRADER_DIR}/grade-lead-synthesis.sh" "${BROKEN_DIR}/no-decision-ls.md" >/dev/null 2>&1; then
  test_fail "lead-synthesis: missing decision should FAIL but PASSED"
else
  test_pass "lead-synthesis: missing decision correctly fails"
fi

# === SUMMARY ===
echo ""
echo "════════════════════════════════════════════"
echo -e "${BLUE}Test Suite Summary${NC}"
echo "════════════════════════════════════════════"
echo -e "  ${GREEN}Passed${NC}: ${PASSED}"
echo -e "  ${RED}Failed${NC}: ${FAILED}"
echo -e "  Total: ${TOTAL}"

if [[ "$TOTAL" -gt 0 ]]; then
  pct=$((PASSED * 100 / TOTAL))
  echo "  Pass Rate: ${pct}%"
fi

echo "════════════════════════════════════════════"

if [[ "$FAILED" -gt 0 ]]; then
  echo -e "${RED}TESTS FAILED${NC}"
  exit 1
else
  echo -e "${GREEN}ALL TESTS PASSED${NC}"
  exit 0
fi
