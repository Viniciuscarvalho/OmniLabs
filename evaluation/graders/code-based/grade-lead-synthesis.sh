#!/usr/bin/env bash
# OmniLabs Code-Based Grader: Lead Synthesis Agent
# Validates structural correctness of lead-synthesis agent output.
#
# Usage: bash grade-lead-synthesis.sh <output-file> [--verbose]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

OUTPUT_FILE="${1:?Usage: grade-lead-synthesis.sh <output-file> [--verbose]}"
[[ "${2:-}" == "--verbose" ]] && VERBOSE=1

if [[ ! -f "$OUTPUT_FILE" ]]; then
  echo "Error: File not found: ${OUTPUT_FILE}"
  exit 2
fi

echo "Grading lead-synthesis output: ${OUTPUT_FILE}"
echo ""

# 1. Decision present (GO / NO-GO / CONDITIONAL GO)
check_contains "$OUTPUT_FILE" \
  "\b(GO|NO-GO|CONDITIONAL GO)\b" \
  "decision_present" \
  "Missing GO/NO-GO/CONDITIONAL GO decision"

# 2. Confidence level
check_contains "$OUTPUT_FILE" \
  "Confidence.*:.*\b(Low|Medium|High|Very High)\b" \
  "confidence_level" \
  "Missing confidence level (Low/Medium/High/Very High)"

# 3. Composite score
check_score_format "$OUTPUT_FILE" "Composite.*Score.*[0-9]+/10"

# 4. Dimension scores table with analyst attribution
check_table_present "$OUTPUT_FILE" "Dimension.*Score.*Analyst"

# 5. Required sections
check_section_present "$OUTPUT_FILE" "Consensus Findings"
check_section_present "$OUTPUT_FILE" "Contested Findings"
check_section_present "$OUTPUT_FILE" "Blind Spots"
check_section_present "$OUTPUT_FILE" "Risk Matrix"
check_section_present "$OUTPUT_FILE" "Implementation Roadmap"

# 6. Roadmap phases (Phase 1, 2, 3)
check_contains "$OUTPUT_FILE" "Phase 1" "roadmap_phase1" "Missing Phase 1 in roadmap"
check_contains "$OUTPUT_FILE" "Phase 2" "roadmap_phase2" "Missing Phase 2 in roadmap"
check_contains "$OUTPUT_FILE" "Phase 3" "roadmap_phase3" "Missing Phase 3 in roadmap"

# 7. References to all 4 analyst types
check_contains "$OUTPUT_FILE" "\bBusiness\b" "xref_business" "Missing reference to Business analyst"
check_contains "$OUTPUT_FILE" "\bFinancial\b" "xref_financial" "Missing reference to Financial analyst"
check_contains "$OUTPUT_FILE" "\bTechnical\b" "xref_technical" "Missing reference to Technical analyst"
check_contains "$OUTPUT_FILE" "\bDevil\b|\bAdvocat" "xref_devils_advocate" "Missing reference to Devil's Advocate"

# 8. Risk Matrix table
check_table_present "$OUTPUT_FILE" "Risk.*Probability.*Impact"

# 9. No placeholder text
check_no_placeholder "$OUTPUT_FILE"

# 10. Minimum word count
check_word_count "$OUTPUT_FILE" 1000

# Report
print_grade_report "lead-synthesis"
