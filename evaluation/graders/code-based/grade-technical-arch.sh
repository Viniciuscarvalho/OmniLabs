#!/usr/bin/env bash
# OmniLabs Code-Based Grader: Technical Architecture Agent
# Validates structural correctness of technical-architecture agent output.
#
# Usage: bash grade-technical-arch.sh <output-file> [--verbose]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

OUTPUT_FILE="${1:?Usage: grade-technical-arch.sh <output-file> [--verbose]}"
[[ "${2:-}" == "--verbose" ]] && VERBOSE=1

if [[ ! -f "$OUTPUT_FILE" ]]; then
  echo "Error: File not found: ${OUTPUT_FILE}"
  exit 2
fi

echo "Grading technical-architecture output: ${OUTPUT_FILE}"
echo ""

# 1. Overall score
check_score_format "$OUTPUT_FILE" "Architecture Health.*Score.*[0-9]+/10"

# 2. All 6 dimension scores present
for dim in "Scalability" "Reliability" "Maintainability" "Security" "Observability" "Operability"; do
  check_contains "$OUTPUT_FILE" \
    "${dim}.*[0-9]+/10" \
    "dimension_$(echo "$dim" | tr '[:upper:]' '[:lower:]')" \
    "Missing ${dim} score (X/10)"
done

# 3. Dimension scores table
check_table_present "$OUTPUT_FILE" "Dimension.*Score"

# 4. Required sections
check_section_present "$OUTPUT_FILE" "Executive Summary"
check_section_present "$OUTPUT_FILE" "Critical Findings"
check_section_present "$OUTPUT_FILE" "Scalability Bottlenecks"
check_section_present "$OUTPUT_FILE" "Technical Debt"
check_section_present "$OUTPUT_FILE" "Recommended.*Architecture"

# 5. Severity labels
check_contains "$OUTPUT_FILE" \
  "\b(CRITICAL|HIGH|MEDIUM|LOW)\b" \
  "severity_labels" \
  "Missing severity labels (CRITICAL/HIGH/MEDIUM/LOW)"

# 6. Timeline recommendations (30/90/180 days)
check_contains "$OUTPUT_FILE" "30.days?\b|short.term" "timeline_30d" "Missing 30-day/short-term recommendations"
check_contains "$OUTPUT_FILE" "90.days?\b|medium.term" "timeline_90d" "Missing 90-day/medium-term recommendations"
check_contains "$OUTPUT_FILE" "180.days?\b|long.term" "timeline_180d" "Missing 180-day/long-term recommendations"

# 7. No placeholder text
check_no_placeholder "$OUTPUT_FILE"

# 8. Minimum word count
check_word_count "$OUTPUT_FILE" 700

# Report
print_grade_report "technical-architecture"
