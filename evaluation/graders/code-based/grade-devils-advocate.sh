#!/usr/bin/env bash
# OmniLabs Code-Based Grader: Devil's Advocate Agent
# Validates structural correctness of devils-advocate agent output.
#
# Usage: bash grade-devils-advocate.sh <output-file> [--verbose]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

OUTPUT_FILE="${1:?Usage: grade-devils-advocate.sh <output-file> [--verbose]}"
[[ "${2:-}" == "--verbose" ]] && VERBOSE=1

if [[ ! -f "$OUTPUT_FILE" ]]; then
  echo "Error: File not found: ${OUTPUT_FILE}"
  exit 2
fi

echo "Grading devils-advocate output: ${OUTPUT_FILE}"
echo ""

# 1. Risk score
check_score_format "$OUTPUT_FILE" "Risk Score.*[0-9]+/10"

# 2. Required sections
check_section_present "$OUTPUT_FILE" "Executive Summary"
check_section_present "$OUTPUT_FILE" "Risk Heat Map"
check_section_present "$OUTPUT_FILE" "Assumption Audit"
check_section_present "$OUTPUT_FILE" "Failure Scenarios"
check_section_present "$OUTPUT_FILE" "Counter.Arguments"
check_section_present "$OUTPUT_FILE" "Blind Spots"
check_section_present "$OUTPUT_FILE" "Resilience Recommendations"

# 3. Risk Heat Map table
check_table_present "$OUTPUT_FILE" "Risk.*Probability.*Impact"

# 4. Failure scenarios coverage (3 types)
check_contains "$OUTPUT_FILE" "Most Likely" "failure_most_likely" "Missing 'Most Likely Failure' scenario"
check_contains "$OUTPUT_FILE" "Most Damaging" "failure_most_damaging" "Missing 'Most Damaging Failure' scenario"
check_contains "$OUTPUT_FILE" "Black Swan" "failure_black_swan" "Missing 'Black Swan' scenario"

# 5. Assumption verdicts
check_contains "$OUTPUT_FILE" \
  "\b(Valid|Questionable|Unfounded)\b" \
  "assumption_verdicts" \
  "Missing assumption verdicts (Valid/Questionable/Unfounded)"

# 6. Confidence labels in counter-arguments
check_contains "$OUTPUT_FILE" \
  "Confidence.*:.*\b(Low|Medium|High)\b" \
  "confidence_labels" \
  "Missing confidence labels in counter-arguments"

# 7. Cross-references to other analysts
cross_ref_count=0
for analyst in "business" "financial" "technical" "architect"; do
  if grep -qiE "\b${analyst}\b" "$OUTPUT_FILE" 2>/dev/null; then
    cross_ref_count=$((cross_ref_count + 1))
  fi
done
if [[ "$cross_ref_count" -ge 2 ]]; then
  check_pass "cross_references" "References ${cross_ref_count} other analysts"
else
  check_fail "cross_references" "Only ${cross_ref_count} cross-references to other analysts (min: 2)"
fi

# 8. No placeholder text
check_no_placeholder "$OUTPUT_FILE"

# 9. Minimum word count
check_word_count "$OUTPUT_FILE" 800

# Report
print_grade_report "devils-advocate"
