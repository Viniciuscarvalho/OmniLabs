#!/usr/bin/env bash
# OmniLabs Evaluation Harness — Run Single Eval
# Runs a single eval task against an agent and grades the output.
#
# Usage:
#   bash run-eval.sh --agent <name> --task <path> [options]
#   bash run-eval.sh --agent <name> --task <path> --grader-only --output <file>
#
# Options:
#   --agent NAME       Agent name (must match .claude/agents/<name>.md)
#   --task PATH        Path to task .md file
#   --output-dir DIR   Where to write results (default: evaluation/results/)
#   --grader-only      Skip agent execution, grade existing output file
#   --output FILE      Path to existing output file (for --grader-only mode)
#   --verbose          Print all grader check details
#   --help             Show this help message

set -euo pipefail

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# --- Defaults ---
AGENT=""
TASK_FILE=""
OUTPUT_DIR=""
GRADER_ONLY=0
OUTPUT_FILE=""
VERBOSE=0

# --- Find project root ---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

print_usage() {
  echo "Usage: bash run-eval.sh --agent <name> --task <path> [options]"
  echo ""
  echo "Options:"
  echo "  --agent NAME       Agent name (e.g., business-product)"
  echo "  --task PATH        Path to task .md file"
  echo "  --output-dir DIR   Results directory (default: evaluation/results/)"
  echo "  --grader-only      Skip agent execution, grade existing output"
  echo "  --output FILE      Existing output file (requires --grader-only)"
  echo "  --verbose          Show all grader check details"
  echo "  --help             Show this help"
}

# --- Parse Arguments ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent) AGENT="$2"; shift 2 ;;
    --task) TASK_FILE="$2"; shift 2 ;;
    --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
    --grader-only) GRADER_ONLY=1; shift ;;
    --output) OUTPUT_FILE="$2"; shift 2 ;;
    --verbose) VERBOSE=1; shift ;;
    --help) print_usage; exit 0 ;;
    *) echo "Unknown option: $1"; print_usage; exit 1 ;;
  esac
done

# --- Validate ---
if [[ -z "$AGENT" ]]; then
  echo -e "${RED}Error${NC}: --agent is required"
  print_usage
  exit 1
fi

if [[ -z "$TASK_FILE" ]]; then
  echo -e "${RED}Error${NC}: --task is required"
  print_usage
  exit 1
fi

if [[ ! -f "$TASK_FILE" ]]; then
  echo -e "${RED}Error${NC}: Task file not found: ${TASK_FILE}"
  exit 2
fi

# Set defaults
OUTPUT_DIR="${OUTPUT_DIR:-${PROJECT_ROOT}/evaluation/results}"
mkdir -p "$OUTPUT_DIR"

# --- Map agent name to grader script ---
resolve_grader() {
  local agent="$1"
  local grader_dir="${PROJECT_ROOT}/evaluation/graders/code-based"

  case "$agent" in
    business-product)       echo "${grader_dir}/grade-business-product.sh" ;;
    financial-cost)         echo "${grader_dir}/grade-financial-cost.sh" ;;
    technical-architecture) echo "${grader_dir}/grade-technical-arch.sh" ;;
    devils-advocate)        echo "${grader_dir}/grade-devils-advocate.sh" ;;
    lead-synthesis)         echo "${grader_dir}/grade-lead-synthesis.sh" ;;
    *)
      echo -e "${RED}Error${NC}: Unknown agent '${agent}'" >&2
      echo "Valid agents: business-product, financial-cost, technical-architecture, devils-advocate, lead-synthesis" >&2
      exit 1
      ;;
  esac
}

GRADER_SCRIPT=$(resolve_grader "$AGENT")
if [[ ! -f "$GRADER_SCRIPT" ]]; then
  echo -e "${RED}Error${NC}: Grader script not found: ${GRADER_SCRIPT}"
  exit 2
fi

# --- Parse Task File ---
parse_task_input() {
  local file="$1"
  # Extract content between "## Input" and next "##" heading
  awk '
    /^## Input/ { in_section=1; next }
    /^## / { if (in_section) exit }
    in_section { print }
  ' "$file"
}

TASK_NAME=$(basename "$TASK_FILE" .md)
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

echo -e "${BLUE}OmniLabs Eval Runner${NC}"
echo "═══════════════════════════════════════════"
echo -e "  Agent:  ${AGENT}"
echo -e "  Task:   ${TASK_NAME}"
echo -e "  Mode:   $([ "$GRADER_ONLY" -eq 1 ] && echo 'grader-only' || echo 'full (agent + grader)')"
echo "═══════════════════════════════════════════"
echo ""

# --- Run Agent or Use Existing Output ---
if [[ "$GRADER_ONLY" -eq 1 ]]; then
  if [[ -z "$OUTPUT_FILE" ]]; then
    echo -e "${RED}Error${NC}: --output is required with --grader-only"
    exit 1
  fi
  if [[ ! -f "$OUTPUT_FILE" ]]; then
    echo -e "${RED}Error${NC}: Output file not found: ${OUTPUT_FILE}"
    exit 2
  fi
  echo -e "${BLUE}Using existing output:${NC} ${OUTPUT_FILE}"
else
  # Execute agent via claude CLI
  OUTPUT_FILE="${OUTPUT_DIR}/${TIMESTAMP}-${AGENT}-${TASK_NAME}.md"
  TASK_INPUT=$(parse_task_input "$TASK_FILE")

  if [[ -z "$TASK_INPUT" ]]; then
    echo -e "${RED}Error${NC}: No input found in task file (missing '## Input' section)"
    exit 2
  fi

  echo -e "${BLUE}Running agent...${NC}"
  if command -v claude &>/dev/null; then
    echo "$TASK_INPUT" | claude --agent "$AGENT" --print > "$OUTPUT_FILE" 2>/dev/null
    echo -e "${GREEN}Agent output saved:${NC} ${OUTPUT_FILE}"
  else
    echo -e "${YELLOW}Warning${NC}: 'claude' CLI not found. Cannot execute agent."
    echo "Install Claude Code or use --grader-only mode with an existing output file."
    exit 3
  fi
fi

echo ""

# --- Run Code-Based Grader ---
echo -e "${BLUE}Running code-based grader...${NC}"
echo ""

GRADER_EXIT=0
if [[ "$VERBOSE" -eq 1 ]]; then
  export VERBOSE=1
fi

bash "$GRADER_SCRIPT" "$OUTPUT_FILE" $([ "$VERBOSE" -eq 1 ] && echo "--verbose") || GRADER_EXIT=$?

# --- Write Result File ---
RESULT_FILE="${OUTPUT_DIR}/${TIMESTAMP}-${AGENT}-${TASK_NAME}-result.md"

{
  echo "# Eval Result: ${AGENT} / ${TASK_NAME}"
  echo ""
  echo "- **Date**: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "- **Agent**: ${AGENT}"
  echo "- **Task**: ${TASK_NAME}"
  echo "- **Task File**: ${TASK_FILE}"
  echo "- **Output File**: ${OUTPUT_FILE}"
  echo "- **Mode**: $([ "$GRADER_ONLY" -eq 1 ] && echo 'grader-only' || echo 'full')"
  echo "- **Verdict**: $([ "$GRADER_EXIT" -eq 0 ] && echo 'PASS' || echo 'FAIL')"
  echo ""
  echo "## Grader Output"
  echo ""
  echo '```'
  bash "$GRADER_SCRIPT" "$OUTPUT_FILE" 2>&1 || true
  echo '```'
} > "$RESULT_FILE"

echo ""
echo -e "${BLUE}Result saved:${NC} ${RESULT_FILE}"

exit "$GRADER_EXIT"
