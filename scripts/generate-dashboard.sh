#!/usr/bin/env bash
# OmniLabs Dashboard Generator
# Reads reports from reports/ and generates dashboard/index.html with embedded data.
# Usage: bash scripts/generate-dashboard.sh [--open]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPORTS_DIR="$PROJECT_ROOT/reports"
DASHBOARD_TEMPLATE="$PROJECT_ROOT/dashboard/template.html"
DASHBOARD_OUT="$PROJECT_ROOT/dashboard/index.html"
MEMORIES_DIR="$PROJECT_ROOT/.claude/memories"
OLLAMA_URL="http://localhost:11434"

# --- Check Ollama ---
ollama_running=false
if curl -s --max-time 3 "${OLLAMA_URL}/api/tags" >/dev/null 2>&1; then
  ollama_running=true
fi

# --- Collect memories ---
memories_json="[]"
if [ -d "$MEMORIES_DIR" ]; then
  mem_entries=()
  while IFS= read -r -d '' file; do
    fname=$(basename "$file" .md)
    fdate=$(date -r "$file" '+%Y-%m-%d' 2>/dev/null || echo "unknown")
    # Determine type from filename prefix
    if [[ "$fname" == learning_* ]]; then
      ftype="learning"
    elif [[ "$fname" == decision_* ]]; then
      ftype="decision"
    else
      ftype="other"
    fi
    mem_entries+=("{\"name\":\"$fname\",\"date\":\"$fdate\",\"type\":\"$ftype\"}")
  done < <(find "$MEMORIES_DIR" -name '*.md' -type f -print0 2>/dev/null || true)

  if [ ${#mem_entries[@]} -gt 0 ]; then
    memories_json="[$(IFS=,; echo "${mem_entries[*]}")]"
  fi
fi

# --- Collect analyses from reports/ ---
analyses_json="[]"
analysis_entries=()

if [ -d "$REPORTS_DIR" ]; then
  # Look for summary.json files in each report directory
  while IFS= read -r summary_file; do
    if [ -f "$summary_file" ]; then
      # Read the JSON directly
      content=$(cat "$summary_file")
      analysis_entries+=("$content")
    fi
  done < <(find "$REPORTS_DIR" -name 'summary.json' -type f 2>/dev/null | sort -r)
fi

if [ ${#analysis_entries[@]} -gt 0 ]; then
  analyses_json="[$(IFS=,; echo "${analysis_entries[*]}")]"
fi

# --- Build and inject data using Python (safe JSON handling) ---
if [ ! -f "$DASHBOARD_TEMPLATE" ]; then
  echo "Error: Template not found at $DASHBOARD_TEMPLATE" >&2
  exit 1
fi

generated_at=$(date '+%Y-%m-%d %H:%M')

TEMPLATE_PATH="$DASHBOARD_TEMPLATE" \
OUTPUT_PATH="$DASHBOARD_OUT" \
ANALYSES_JSON="$analyses_json" \
MEMORIES_JSON="$memories_json" \
OLLAMA_RUNNING="$ollama_running" \
GENERATED_AT="$generated_at" \
python3 << 'PYEOF'
import json, os, sys

template_path = os.environ.get("TEMPLATE_PATH")
output_path = os.environ.get("OUTPUT_PATH")
analyses_json = os.environ.get("ANALYSES_JSON", "[]")
memories_json = os.environ.get("MEMORIES_JSON", "[]")
ollama = os.environ.get("OLLAMA_RUNNING", "false") == "true"
generated_at = os.environ.get("GENERATED_AT", "")

data = {
    "generated_at": generated_at,
    "ollama_running": ollama,
    "memories": json.loads(memories_json),
    "analyses": json.loads(analyses_json),
}

with open(template_path) as f:
    template = f.read()

result = template.replace("__DASHBOARD_DATA__", json.dumps(data, ensure_ascii=False), 1)

with open(output_path, "w") as f:
    f.write(result)

print(f"Dashboard generated: {output_path}")
PYEOF

# --- Open in browser if --open flag ---
if [[ "${1:-}" == "--open" ]]; then
  if command -v open &>/dev/null; then
    open "$DASHBOARD_OUT"
  elif command -v xdg-open &>/dev/null; then
    xdg-open "$DASHBOARD_OUT"
  fi
fi
