#!/usr/bin/env bash
# OmniLabs Code-Based Grader: Business & Product Agent
# Validates structural correctness of business-product agent output.
#
# Usage: bash grade-business-product.sh <output-file> [--verbose]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

OUTPUT_FILE="${1:?Usage: grade-business-product.sh <output-file> [--verbose]}"
[[ "${2:-}" == "--verbose" ]] && VERBOSE=1

if [[ ! -f "$OUTPUT_FILE" ]]; then
  echo "Error: File not found: ${OUTPUT_FILE}"
  exit 2
fi

echo "Grading business-product output: ${OUTPUT_FILE}"
echo ""

# 1. Primary score
check_score_format "$OUTPUT_FILE" "Market Opportunity.*Score.*[0-9]+/10"

# 2. Required sections
check_section_present "$OUTPUT_FILE" "Executive Summary"
check_section_present "$OUTPUT_FILE" "Market Analysis"
check_section_present "$OUTPUT_FILE" "Product.Market Fit"
check_section_present "$OUTPUT_FILE" "Competitive Position"
check_section_present "$OUTPUT_FILE" "Revenue Model"
check_section_present "$OUTPUT_FILE" "Go.to.Market"
check_section_present "$OUTPUT_FILE" "Risks"

# 3. Moat strength classification
check_contains "$OUTPUT_FILE" \
  "Moat.*:.*\b(None|Weak|Moderate|Strong)\b" \
  "moat_strength" \
  "Missing Moat Strength classification (None/Weak/Moderate/Strong)"

# 4. TAM/SAM/SOM analysis present
check_contains "$OUTPUT_FILE" "TAM" "tam_present" "Missing TAM (Total Addressable Market)"
check_contains "$OUTPUT_FILE" "SAM" "sam_present" "Missing SAM (Serviceable Addressable Market)"
check_contains "$OUTPUT_FILE" "SOM" "som_present" "Missing SOM (Serviceable Obtainable Market)"

# 5. Named competitors (not just generic mentions)
check_bullet_count "$OUTPUT_FILE" "Competitive Position" 3

# 6. No placeholder text
check_no_placeholder "$OUTPUT_FILE"

# 7. Minimum word count
check_word_count "$OUTPUT_FILE" 500

# Report
print_grade_report "business-product"
