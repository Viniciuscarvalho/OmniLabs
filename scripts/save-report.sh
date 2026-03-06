#!/usr/bin/env bash
# OmniLabs Report Saver
# Called by agents to save analysis results in structured format.
# Usage: bash scripts/save-report.sh <project-name>
# Creates reports/<timestamp>/ with summary.json
# After saving, automatically regenerates the dashboard.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

project_name="${1:-$(basename "$(pwd)")}"
timestamp=$(date '+%Y-%m-%d-%H%M%S')
report_dir="$PROJECT_ROOT/reports/$timestamp"

mkdir -p "$report_dir"

# Read from stdin (piped JSON) or create empty template
if [ ! -t 0 ]; then
  cat > "$report_dir/summary.json"
else
  cat > "$report_dir/summary.json" << EOF
{
  "project": "$project_name",
  "date": "$(date '+%Y-%m-%d %H:%M')",
  "decision": "",
  "confidence": "",
  "composite_score": 0,
  "scores": {
    "market": 0,
    "financial": 0,
    "architecture": 0,
    "risk": 0
  },
  "conditions": [],
  "consensus": [],
  "contested": [],
  "agents": {}
}
EOF
fi

echo "$report_dir"

# Auto-regenerate dashboard
bash "$SCRIPT_DIR/generate-dashboard.sh" 2>/dev/null || true
