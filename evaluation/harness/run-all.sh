#!/usr/bin/env bash
# OmniLabs Evaluation Harness — Run All Evals
# Discovers and runs all eval tasks for one or all agents.
#
# Usage:
#   bash run-all.sh [options]
#
# Options:
#   --agent NAME       Run only tasks for this agent (default: all agents)
#   --grader-only      Skip agent execution, grade existing outputs only
#   --output-dir DIR   Results directory (default: evaluation/results/)
#   --verbose          Show all grader check details
#   --help             Show this help message

set -euo pipefail

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# --- Defaults ---
AGENT=""
GRADER_ONLY=0
OUTPUT_DIR=""
VERBOSE=0

# --- Find project root ---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
TASKS_DIR="${PROJECT_ROOT}/evaluation/tasks"

print_usage() {
  echo "Usage: bash run-all.sh [options]"
  echo ""
  echo "Options:"
  echo "  --agent NAME       Run tasks for one agent (default: all)"
  echo "  --grader-only      Skip agent execution"
  echo "  --output-dir DIR   Results directory (default: evaluation/results/)"
  echo "  --verbose          Show grader details"
  echo "  --help             Show this help"
}

# --- Parse Arguments ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent) AGENT="$2"; shift 2 ;;
    --grader-only) GRADER_ONLY=1; shift ;;
    --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
    --verbose) VERBOSE=1; shift ;;
    --help) print_usage; exit 0 ;;
    *) echo "Unknown option: $1"; print_usage; exit 1 ;;
  esac
done

OUTPUT_DIR="${OUTPUT_DIR:-${PROJECT_ROOT}/evaluation/results}"
mkdir -p "$OUTPUT_DIR"

AGENTS=("business-product" "financial-cost" "technical-architecture" "devils-advocate" "lead-synthesis")

# Filter to single agent if specified
if [[ -n "$AGENT" ]]; then
  found=0
  for a in "${AGENTS[@]}"; do
    if [[ "$a" == "$AGENT" ]]; then found=1; break; fi
  done
  if [[ "$found" -eq 0 ]]; then
    echo -e "${RED}Error${NC}: Unknown agent '${AGENT}'"
    echo "Valid agents: ${AGENTS[*]}"
    exit 1
  fi
  AGENTS=("$AGENT")
fi

# --- Discover Tasks ---
discover_tasks() {
  local agent="$1"
  local task_dir="${TASKS_DIR}/${agent}"
  if [[ -d "$task_dir" ]]; then
    find "$task_dir" -name 'task-*.md' -type f | sort
  fi
}

# --- Run All ---
echo -e "${PURPLE}╔══════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║       OmniLabs Evaluation Suite          ║${NC}"
echo -e "${PURPLE}╚══════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Mode:   $([ "$GRADER_ONLY" -eq 1 ] && echo 'grader-only' || echo 'full (agent + grader)')"
echo -e "  Agents: ${AGENTS[*]}"
echo -e "  Output: ${OUTPUT_DIR}"
echo ""

TOTAL_TASKS=0
TOTAL_PASS=0
TOTAL_FAIL=0
TOTAL_SKIP=0
SUMMARY_LINES=()

for agent in "${AGENTS[@]}"; do
  echo -e "${BLUE}━━━ Agent: ${agent} ━━━${NC}"

  tasks=$(discover_tasks "$agent")
  if [[ -z "$tasks" ]]; then
    echo -e "  ${YELLOW}No tasks found${NC}"
    echo ""
    continue
  fi

  while IFS= read -r task_file; do
    task_name=$(basename "$task_file" .md)
    TOTAL_TASKS=$((TOTAL_TASKS + 1))

    # Build arguments
    args=(--agent "$agent" --task "$task_file" --output-dir "$OUTPUT_DIR")
    if [[ "$GRADER_ONLY" -eq 1 ]]; then
      # In grader-only mode without a specific output file, skip execution
      echo -e "  ${YELLOW}SKIP${NC} ${task_name} (grader-only requires --output per task)"
      TOTAL_SKIP=$((TOTAL_SKIP + 1))
      SUMMARY_LINES+=("SKIP|${agent}|${task_name}|N/A")
      continue
    fi
    if [[ "$VERBOSE" -eq 1 ]]; then
      args+=(--verbose)
    fi

    echo -e "  ${BLUE}RUN${NC}  ${task_name}"

    eval_exit=0
    bash "${SCRIPT_DIR}/run-eval.sh" "${args[@]}" > /dev/null 2>&1 || eval_exit=$?

    if [[ "$eval_exit" -eq 0 ]]; then
      echo -e "  ${GREEN}PASS${NC} ${task_name}"
      TOTAL_PASS=$((TOTAL_PASS + 1))
      SUMMARY_LINES+=("PASS|${agent}|${task_name}|0")
    elif [[ "$eval_exit" -eq 3 ]]; then
      echo -e "  ${YELLOW}SKIP${NC} ${task_name} (claude CLI not available)"
      TOTAL_SKIP=$((TOTAL_SKIP + 1))
      SUMMARY_LINES+=("SKIP|${agent}|${task_name}|3")
    else
      echo -e "  ${RED}FAIL${NC} ${task_name}"
      TOTAL_FAIL=$((TOTAL_FAIL + 1))
      SUMMARY_LINES+=("FAIL|${agent}|${task_name}|${eval_exit}")
    fi
  done <<< "$tasks"

  echo ""
done

# --- Summary ---
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
SUMMARY_FILE="${OUTPUT_DIR}/summary-${TIMESTAMP}.md"

{
  echo "# OmniLabs Evaluation Summary"
  echo ""
  echo "- **Date**: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "- **Mode**: $([ "$GRADER_ONLY" -eq 1 ] && echo 'grader-only' || echo 'full')"
  echo "- **Agents**: ${AGENTS[*]}"
  echo ""
  echo "## Results"
  echo ""
  echo "| Status | Agent | Task | Exit Code |"
  echo "|--------|-------|------|-----------|"
  for line in "${SUMMARY_LINES[@]}"; do
    status=$(echo "$line" | cut -d'|' -f1)
    agent=$(echo "$line" | cut -d'|' -f2)
    task=$(echo "$line" | cut -d'|' -f3)
    code=$(echo "$line" | cut -d'|' -f4)
    echo "| ${status} | ${agent} | ${task} | ${code} |"
  done
  echo ""
  echo "## Summary"
  echo ""
  echo "| Metric | Count |"
  echo "|--------|-------|"
  echo "| Total Tasks | ${TOTAL_TASKS} |"
  echo "| Passed | ${TOTAL_PASS} |"
  echo "| Failed | ${TOTAL_FAIL} |"
  echo "| Skipped | ${TOTAL_SKIP} |"
  if [[ "$TOTAL_TASKS" -gt 0 ]]; then
    pct=$(( (TOTAL_PASS * 100) / (TOTAL_TASKS - TOTAL_SKIP > 0 ? TOTAL_TASKS - TOTAL_SKIP : 1) ))
    echo "| Pass Rate | ${pct}% |"
  fi
} > "$SUMMARY_FILE"

echo "═══════════════════════════════════════════"
echo -e "  ${GREEN}Passed${NC}: ${TOTAL_PASS}  ${RED}Failed${NC}: ${TOTAL_FAIL}  ${YELLOW}Skipped${NC}: ${TOTAL_SKIP}  Total: ${TOTAL_TASKS}"
echo "═══════════════════════════════════════════"
echo -e "Summary saved: ${SUMMARY_FILE}"

[[ "$TOTAL_FAIL" -eq 0 ]] && exit 0 || exit 1
