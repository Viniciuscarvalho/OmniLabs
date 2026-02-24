#!/usr/bin/env bash
# OmniLabs Ollama Status & Memory Sync Hook
# Hook: SessionStart — checks Ollama availability and reports KB status
# Registered in .claude/settings.json

set -euo pipefail
trap 'exit 0' ERR

OLLAMA_URL="http://localhost:11434"
MEMORIES_DIR=".claude/memories"
LIBRARY_NAME="omnilabs-memories"
EMBEDDING_MODEL="openai:nomic-embed-text"

# --- Check Ollama status ---
ollama_running=false
model_available=false

if curl -s --max-time 5 "${OLLAMA_URL}/api/tags" >/dev/null 2>&1; then
  ollama_running=true
  if curl -s --max-time 5 "${OLLAMA_URL}/api/tags" 2>/dev/null | grep -q "nomic-embed-text"; then
    model_available=true
  fi
fi

# --- Count available memories ---
memory_count=0
if [ -d "$MEMORIES_DIR" ]; then
  memory_count=$(find "$MEMORIES_DIR" -name '*.md' -type f 2>/dev/null | wc -l | tr -d ' ')
fi

# --- Sync memories to docs-mcp-server (background) ---
if [ "$ollama_running" = true ] && [ -d "$MEMORIES_DIR" ] && [ "$memory_count" -gt 0 ]; then
  repo_name=$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "")
  if [ -n "$repo_name" ]; then
    memories_path="$(git rev-parse --show-toplevel 2>/dev/null)/.claude/memories"

    # Background sync with 120s watchdog to prevent hangs.
    # Redirect all output so the hook's pipe closes immediately.
    (
      trap 'kill 0 2>/dev/null' TERM
      export OPENAI_API_KEY=ollama
      export OPENAI_API_BASE="${OLLAMA_URL}/v1"

      if npx -y @arabold/docs-mcp-server@latest list --silent 2>/dev/null | grep -q "${LIBRARY_NAME}"; then
        npx -y @arabold/docs-mcp-server@latest refresh "${LIBRARY_NAME}" \
          --embedding-model "$EMBEDDING_MODEL" \
          --silent >/dev/null 2>&1
      else
        npx -y @arabold/docs-mcp-server@latest scrape "${LIBRARY_NAME}" \
          "file://${memories_path}" \
          --embedding-model "$EMBEDDING_MODEL" \
          --silent >/dev/null 2>&1
      fi
    ) >/dev/null 2>&1 &
    sync_pid=$!
    ( sleep 120 && kill "$sync_pid" 2>/dev/null ) >/dev/null 2>&1 &
  fi
fi

# --- Build status message ---
status_parts=()

if [ "$ollama_running" = true ]; then
  status_parts+=("Ollama: running")
  if [ "$model_available" = true ]; then
    status_parts+=("nomic-embed-text: ready")
  else
    status_parts+=("nomic-embed-text: missing (run: ollama pull nomic-embed-text)")
  fi
else
  status_parts+=("Ollama: not running (KB search unavailable, run: ollama serve)")
fi

status_parts+=("Memories: ${memory_count} files")

if [ "$memory_count" -gt 0 ] && [ "$ollama_running" = true ]; then
  status_parts+=("Search the KB before starting analysis tasks")
fi

# Join with " | "
message=""
for part in "${status_parts[@]}"; do
  if [ -n "$message" ]; then
    message="${message} | ${part}"
  else
    message="${part}"
  fi
done

echo "${message}"
