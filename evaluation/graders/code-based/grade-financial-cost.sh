#!/usr/bin/env bash
# OmniLabs Code-Based Grader: Financial & Cost Agent
# Validates structural correctness of financial-cost agent output.
#
# Usage: bash grade-financial-cost.sh <output-file> [--verbose]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

OUTPUT_FILE="${1:?Usage: grade-financial-cost.sh <output-file> [--verbose]}"
[[ "${2:-}" == "--verbose" ]] && VERBOSE=1

if [[ ! -f "$OUTPUT_FILE" ]]; then
  echo "Error: File not found: ${OUTPUT_FILE}"
  exit 2
fi

echo "Grading financial-cost output: ${OUTPUT_FILE}"
echo ""

# 1. Primary score
check_score_format "$OUTPUT_FILE" "Financial Health.*Score.*[0-9]+/10"

# 2. Required sections
check_section_present "$OUTPUT_FILE" "Executive Summary"
check_section_present "$OUTPUT_FILE" "Current Cost Structure"
check_section_present "$OUTPUT_FILE" "Scaling Projections"
check_section_present "$OUTPUT_FILE" "ROI Analysis"
check_section_present "$OUTPUT_FILE" "Cost Optimization"
check_section_present "$OUTPUT_FILE" "Financial Risks"

# 3. Cost structure table (Category | Monthly | Annual | %)
check_table_present "$OUTPUT_FILE" "Category.*Monthly.*Annual"
check_table_columns "$OUTPUT_FILE" "Category.*Monthly.*Annual" 4

# 4. Scaling projections table (Users | Monthly | Annual | Cost)
check_table_present "$OUTPUT_FILE" "Users.*Monthly.*Annual"

# 5. Dollar amounts present (at least 3 distinct mentions)
dollar_count=$(grep -coE '\$[0-9][0-9,/.]*' "$OUTPUT_FILE" 2>/dev/null || echo "0")
if [[ "$dollar_count" -ge 3 ]]; then
  check_pass "dollar_amounts" "${dollar_count} dollar references found"
else
  check_fail "dollar_amounts" "Only ${dollar_count} dollar references (min: 3)"
fi

# 6. Scale points coverage (1K, 10K, 100K, 1M users)
check_contains "$OUTPUT_FILE" "1[,.]?000\b|1K\b" "scale_1k" "Missing 1K user scale point"
check_contains "$OUTPUT_FILE" "10[,.]?000\b|10K\b" "scale_10k" "Missing 10K user scale point"
check_contains "$OUTPUT_FILE" "100[,.]?000\b|100K\b" "scale_100k" "Missing 100K user scale point"
check_contains "$OUTPUT_FILE" "1[,.]?000[,.]?000\b|1M\b" "scale_1m" "Missing 1M user scale point"

# 7. No placeholder text
check_no_placeholder "$OUTPUT_FILE"

# 8. Minimum word count
check_word_count "$OUTPUT_FILE" 600

# Report
print_grade_report "financial-cost"
