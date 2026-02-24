#!/usr/bin/env bash
# OmniLabs Continuous Learning Activator
# Hook: PreToolUse — reminds the assistant to capture knowledge after completing work
# Registered in .claude/settings.json

set -euo pipefail

# Read hook input from stdin (PreToolUse receives JSON with tool info)
INPUT=$(cat 2>/dev/null || true)

# Always approve — never block tool use. Only append a knowledge capture reminder.
cat << 'EOF'
{
  "decision": "approve",
  "message": "[OmniLabs KB] After completing this task, evaluate if it produced reusable knowledge. Learnings (debugging, patterns, workarounds) → learning_<topic>_<specific>. Decisions (architecture, conventions, methodology) → decision_<domain>_<topic>. Domains: analysis, evaluation, agent, framework, tooling, debugging. Use continuous-learning skill to save to .claude/memories/. Search KB first to avoid duplicates."
}
EOF
