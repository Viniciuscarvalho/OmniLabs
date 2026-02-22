#!/usr/bin/env bash
# OmniLabs Evaluation Framework — Common Grader Utilities
# Source this file in all code-based graders: source "$(dirname "$0")/common.sh"

set -euo pipefail

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# --- Result Tracking ---
PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0
TOTAL_COUNT=0
RESULTS=()

check_pass() {
  local name="$1"
  local msg="${2:-}"
  PASS_COUNT=$((PASS_COUNT + 1))
  TOTAL_COUNT=$((TOTAL_COUNT + 1))
  RESULTS+=("PASS|${name}|${msg}")
  if [[ "${VERBOSE:-0}" == "1" ]]; then
    echo -e "  ${GREEN}PASS${NC} ${name}${msg:+ — $msg}"
  fi
}

check_fail() {
  local name="$1"
  local msg="${2:-}"
  FAIL_COUNT=$((FAIL_COUNT + 1))
  TOTAL_COUNT=$((TOTAL_COUNT + 1))
  RESULTS+=("FAIL|${name}|${msg}")
  echo -e "  ${RED}FAIL${NC} ${name}${msg:+ — $msg}"
}

check_warn() {
  local name="$1"
  local msg="${2:-}"
  WARN_COUNT=$((WARN_COUNT + 1))
  RESULTS+=("WARN|${name}|${msg}")
  if [[ "${VERBOSE:-0}" == "1" ]]; then
    echo -e "  ${YELLOW}WARN${NC} ${name}${msg:+ — $msg}"
  fi
}

# --- Section Validators ---

# Check if a markdown section heading exists in the file
# Usage: check_section_present <file> <heading_regex>
check_section_present() {
  local file="$1"
  local heading="$2"
  local check_name="section_$(echo "$heading" | tr ' /' '_' | tr -cd '[:alnum:]_' | tr '[:upper:]' '[:lower:]')"

  if grep -qiE "^#{1,4}\s+.*${heading}" "$file" 2>/dev/null; then
    check_pass "$check_name" "Section '${heading}' found"
  else
    check_fail "$check_name" "Missing section matching '${heading}'"
  fi
}

# Check if a score in X/10 format exists matching a pattern
# Usage: check_score_format <file> <pattern>
check_score_format() {
  local file="$1"
  local pattern="$2"

  if grep -qiE "${pattern}" "$file" 2>/dev/null; then
    # Extract the score value and validate range 1-10
    local score
    score=$(grep -oiE "${pattern}" "$file" | head -1 | grep -oE '[0-9]+/10' | head -1 | cut -d'/' -f1)
    if [[ -n "$score" ]] && [[ "$score" -ge 1 ]] && [[ "$score" -le 10 ]]; then
      check_pass "score_format" "Score ${score}/10 found"
    else
      check_fail "score_format" "Score out of valid range (1-10): ${score:-empty}"
    fi
  else
    check_fail "score_format" "No score matching pattern '${pattern}'"
  fi
}

# Check if a markdown table exists with a header matching the pattern
# Usage: check_table_present <file> <header_pattern>
check_table_present() {
  local file="$1"
  local header_pattern="$2"
  local check_name="table_$(echo "$header_pattern" | tr ' |.*' '_' | tr -cd '[:alnum:]_' | head -c 30)"

  if grep -qiE "\|.*${header_pattern}.*\|" "$file" 2>/dev/null; then
    check_pass "$check_name" "Table with '${header_pattern}' found"
  else
    check_fail "$check_name" "Missing table matching '${header_pattern}'"
  fi
}

# Check that a table has the expected number of columns
# Usage: check_table_columns <file> <header_pattern> <expected_min_columns>
check_table_columns() {
  local file="$1"
  local header_pattern="$2"
  local expected="$3"
  local check_name="table_cols_${expected}"

  local header_line
  header_line=$(grep -iE "\|.*${header_pattern}.*\|" "$file" 2>/dev/null | head -1)
  if [[ -z "$header_line" ]]; then
    check_fail "$check_name" "Table header not found for column count check"
    return
  fi

  # Count pipes (columns = pipes - 1, accounting for leading/trailing pipes)
  local pipe_count
  pipe_count=$(echo "$header_line" | tr -cd '|' | wc -c | tr -d ' ')
  local col_count=$((pipe_count - 1))

  if [[ "$col_count" -ge "$expected" ]]; then
    check_pass "$check_name" "Table has ${col_count} columns (expected >= ${expected})"
  else
    check_fail "$check_name" "Table has ${col_count} columns (expected >= ${expected})"
  fi
}

# Check if checklist items (- [ ] or - [x]) exist
# Usage: check_checklist_present <file>
check_checklist_present() {
  local file="$1"

  if grep -qE '- \[[ x]\]' "$file" 2>/dev/null; then
    check_pass "checklist_present" "Checklist items found"
  else
    check_fail "checklist_present" "No checklist items found"
  fi
}

# Count bullet points under a section heading
# Usage: check_bullet_count <file> <section_heading> <min_count>
check_bullet_count() {
  local file="$1"
  local section="$2"
  local min_count="$3"
  local check_name="bullets_$(echo "$section" | tr ' /' '_' | tr -cd '[:alnum:]_' | tr '[:upper:]' '[:lower:]')"

  # Find the section, then count bullets until next heading
  local count
  count=$(awk -v section="$section" '
    BEGIN { in_section=0; count=0 }
    /^#{1,4} / {
      if (in_section) exit
      if (tolower($0) ~ tolower(section)) in_section=1
      next
    }
    in_section && /^[[:space:]]*[-*]/ { count++ }
    END { print count }
  ' "$file")

  if [[ "$count" -ge "$min_count" ]]; then
    check_pass "$check_name" "${count} bullets found (min: ${min_count})"
  else
    check_fail "$check_name" "${count} bullets found (min: ${min_count})"
  fi
}

# Validate minimum word count
# Usage: check_word_count <file> <min_words>
check_word_count() {
  local file="$1"
  local min_words="$2"

  local count
  count=$(wc -w < "$file" | tr -d ' ')

  if [[ "$count" -ge "$min_words" ]]; then
    check_pass "word_count" "${count} words (min: ${min_words})"
  else
    check_fail "word_count" "${count} words (min: ${min_words})"
  fi
}

# Check for placeholder text that indicates incomplete output
# Usage: check_no_placeholder <file>
check_no_placeholder() {
  local file="$1"
  local found=0

  for pattern in '\[TODO\]' '\[TBD\]' 'lorem ipsum' '\$X[^0-9]' '\.\.\.\.' 'PLACEHOLDER'; do
    if grep -qiE "$pattern" "$file" 2>/dev/null; then
      check_fail "no_placeholder" "Found placeholder text matching '${pattern}'"
      found=1
    fi
  done

  if [[ "$found" -eq 0 ]]; then
    check_pass "no_placeholder" "No placeholder text found"
  fi
}

# Check that the output contains a specific keyword or pattern
# Usage: check_contains <file> <pattern> <check_name> [<fail_msg>]
check_contains() {
  local file="$1"
  local pattern="$2"
  local check_name="$3"
  local fail_msg="${4:-Pattern '${pattern}' not found}"

  if grep -qiE "$pattern" "$file" 2>/dev/null; then
    check_pass "$check_name"
  else
    check_fail "$check_name" "$fail_msg"
  fi
}

# --- Report ---

print_grade_report() {
  local agent="${1:-unknown}"
  echo ""
  echo "═══════════════════════════════════════════"
  echo " Grade Report: ${agent}"
  echo "═══════════════════════════════════════════"

  for result in "${RESULTS[@]}"; do
    local status check msg
    status=$(echo "$result" | cut -d'|' -f1)
    check=$(echo "$result" | cut -d'|' -f2)
    msg=$(echo "$result" | cut -d'|' -f3)

    case "$status" in
      PASS) echo -e "  ${GREEN}PASS${NC} ${check}${msg:+ — $msg}" ;;
      FAIL) echo -e "  ${RED}FAIL${NC} ${check}${msg:+ — $msg}" ;;
      WARN) echo -e "  ${YELLOW}WARN${NC} ${check}${msg:+ — $msg}" ;;
    esac
  done

  echo ""
  echo "───────────────────────────────────────────"
  echo -e "  ${GREEN}Passed${NC}: ${PASS_COUNT}  ${RED}Failed${NC}: ${FAIL_COUNT}  ${YELLOW}Warnings${NC}: ${WARN_COUNT}  Total: ${TOTAL_COUNT}"

  if [[ "$TOTAL_COUNT" -gt 0 ]]; then
    local pct=$((PASS_COUNT * 100 / TOTAL_COUNT))
    echo "  Pass Rate: ${pct}%"
  fi

  echo "═══════════════════════════════════════════"

  if [[ "$FAIL_COUNT" -gt 0 ]]; then
    return 1
  fi
  return 0
}
