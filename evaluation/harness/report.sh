#!/usr/bin/env bash
# OmniLabs Evaluation Harness — Report Generator
# Generates a human-readable evaluation report from result files.
#
# Usage:
#   bash report.sh [--results-dir DIR] [--compare FILE]
#
# Options:
#   --results-dir DIR   Results directory (default: evaluation/results/)
#   --compare FILE      Previous summary file to compare against for regressions
#   --help              Show this help message

set -euo pipefail

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# --- Defaults ---
RESULTS_DIR=""
COMPARE_FILE=""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

print_usage() {
  echo "Usage: bash report.sh [options]"
  echo ""
  echo "Options:"
  echo "  --results-dir DIR   Results directory (default: evaluation/results/)"
  echo "  --compare FILE      Previous summary for regression detection"
  echo "  --help              Show this help"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --results-dir) RESULTS_DIR="$2"; shift 2 ;;
    --compare) COMPARE_FILE="$2"; shift 2 ;;
    --help) print_usage; exit 0 ;;
    *) echo "Unknown option: $1"; print_usage; exit 1 ;;
  esac
done

RESULTS_DIR="${RESULTS_DIR:-${PROJECT_ROOT}/evaluation/results}"

if [[ ! -d "$RESULTS_DIR" ]]; then
  echo -e "${RED}Error${NC}: Results directory not found: ${RESULTS_DIR}"
  exit 1
fi

# --- Find latest summary ---
LATEST_SUMMARY=$(find "$RESULTS_DIR" -name 'summary-*.md' -type f | sort -r | head -1)

if [[ -z "$LATEST_SUMMARY" ]]; then
  echo -e "${YELLOW}No evaluation summaries found.${NC}"
  echo "Run evaluations first: bash evaluation/harness/run-all.sh"
  exit 0
fi

echo -e "${PURPLE}╔══════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║       OmniLabs Evaluation Report         ║${NC}"
echo -e "${PURPLE}╚══════════════════════════════════════════╝${NC}"
echo ""

# --- Parse latest summary ---
echo -e "${BLUE}Latest Summary:${NC} $(basename "$LATEST_SUMMARY")"
echo ""

# Extract date
date_line=$(grep "Date" "$LATEST_SUMMARY" | head -1 | sed 's/.*: //')
echo -e "  Date: ${date_line}"
echo ""

# --- Per-Agent Statistics ---
echo -e "${BLUE}Per-Agent Results:${NC}"
echo ""

for agent in "business-product" "financial-cost" "technical-architecture" "devils-advocate" "lead-synthesis"; do
  pass=$(grep -c "| PASS | ${agent}" "$LATEST_SUMMARY" 2>/dev/null || echo "0")
  fail=$(grep -c "| FAIL | ${agent}" "$LATEST_SUMMARY" 2>/dev/null || echo "0")
  skip=$(grep -c "| SKIP | ${agent}" "$LATEST_SUMMARY" 2>/dev/null || echo "0")
  total=$((pass + fail + skip))

  if [[ "$total" -eq 0 ]]; then
    continue
  fi

  run=$((total - skip))
  if [[ "$run" -gt 0 ]]; then
    pct=$((pass * 100 / run))
  else
    pct=0
  fi

  # Color-code pass rate
  if [[ "$pct" -ge 80 ]]; then
    color="$GREEN"
  elif [[ "$pct" -ge 50 ]]; then
    color="$YELLOW"
  else
    color="$RED"
  fi

  printf "  %-25s ${color}%3d%%${NC}  (%d/%d passed, %d skipped)\n" "$agent" "$pct" "$pass" "$run" "$skip"
done

echo ""

# --- Regression Detection ---
if [[ -n "$COMPARE_FILE" ]] && [[ -f "$COMPARE_FILE" ]]; then
  echo -e "${BLUE}Regression Analysis:${NC}"
  echo -e "  Comparing against: $(basename "$COMPARE_FILE")"
  echo ""

  # Find tasks that were PASS before but FAIL now
  regressions=0
  while IFS= read -r line; do
    task=$(echo "$line" | awk -F'|' '{gsub(/ /, "", $4); print $3 "/" $4}')
    # Check if this task was PASS in previous summary
    agent_name=$(echo "$line" | awk -F'|' '{gsub(/ /, "", $3); print $3}')
    task_name=$(echo "$line" | awk -F'|' '{gsub(/ /, "", $4); print $4}')
    if grep -q "| PASS | ${agent_name} | ${task_name}" "$COMPARE_FILE" 2>/dev/null; then
      echo -e "  ${RED}REGRESSION${NC}: ${agent_name} / ${task_name} (was PASS, now FAIL)"
      regressions=$((regressions + 1))
    fi
  done < <(grep "| FAIL |" "$LATEST_SUMMARY" 2>/dev/null || true)

  # Find tasks that were FAIL before but PASS now
  improvements=0
  while IFS= read -r line; do
    agent_name=$(echo "$line" | awk -F'|' '{gsub(/ /, "", $3); print $3}')
    task_name=$(echo "$line" | awk -F'|' '{gsub(/ /, "", $4); print $4}')
    if grep -q "| FAIL | ${agent_name} | ${task_name}" "$COMPARE_FILE" 2>/dev/null; then
      echo -e "  ${GREEN}IMPROVEMENT${NC}: ${agent_name} / ${task_name} (was FAIL, now PASS)"
      improvements=$((improvements + 1))
    fi
  done < <(grep "| PASS |" "$LATEST_SUMMARY" 2>/dev/null || true)

  if [[ "$regressions" -eq 0 ]] && [[ "$improvements" -eq 0 ]]; then
    echo -e "  ${GREEN}No regressions or improvements detected.${NC}"
  else
    echo ""
    echo -e "  Regressions: ${regressions}  Improvements: ${improvements}"
  fi
  echo ""
fi

# --- Overall Summary ---
total_pass=$(grep -c "| PASS |" "$LATEST_SUMMARY" 2>/dev/null || echo "0")
total_fail=$(grep -c "| FAIL |" "$LATEST_SUMMARY" 2>/dev/null || echo "0")
total_skip=$(grep -c "| SKIP |" "$LATEST_SUMMARY" 2>/dev/null || echo "0")
total=$((total_pass + total_fail + total_skip))
total_run=$((total - total_skip))

echo "═══════════════════════════════════════════"
if [[ "$total_run" -gt 0 ]]; then
  overall_pct=$((total_pass * 100 / total_run))
  echo -e "  Overall: ${total_pass}/${total_run} passed (${overall_pct}%)"
else
  echo -e "  Overall: No tasks executed"
fi
echo "═══════════════════════════════════════════"
