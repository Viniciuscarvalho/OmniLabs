#!/usr/bin/env bash
set -euo pipefail

# OmniLabs Installer
# Installs the OmniLabs agent team into your project's .claude/ directory

OMNILABS_REPO="https://raw.githubusercontent.com/Viniciuscarvalho/OmniLabs/main"

AGENTS=(
  "business-product.md"
  "financial-cost.md"
  "technical-architecture.md"
  "devils-advocate.md"
  "lead-synthesis.md"
)

SETTINGS_FILE='.claude/settings.json'

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

print_banner() {
  echo ""
  echo -e "${PURPLE}╔══════════════════════════════════════════╗${NC}"
  echo -e "${PURPLE}║          OmniLabs Installer              ║${NC}"
  echo -e "${PURPLE}║   Multi-Perspective Strategic Analysis   ║${NC}"
  echo -e "${PURPLE}╚══════════════════════════════════════════╝${NC}"
  echo ""
}

print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
print_info()    { echo -e "${BLUE}→${NC} $1"; }
print_error()   { echo -e "${RED}✗${NC} $1"; }

check_dependencies() {
  if ! command -v curl &> /dev/null; then
    print_error "curl is required but not installed."
    exit 1
  fi
}

detect_install_mode() {
  if [ -d ".claude" ]; then
    echo "merge"
  else
    echo "fresh"
  fi
}

install_fresh() {
  print_info "Fresh install — creating .claude/ directory structure"

  mkdir -p .claude/agents

  # Download agents
  for agent in "${AGENTS[@]}"; do
    print_info "Downloading ${agent}..."
    curl -sL "${OMNILABS_REPO}/.claude/agents/${agent}" -o ".claude/agents/${agent}"
    print_success "Installed ${agent}"
  done

  # Download settings.json
  print_info "Creating settings.json..."
  curl -sL "${OMNILABS_REPO}/.claude/settings.json" -o "${SETTINGS_FILE}"
  print_success "Created settings.json with agent teams enabled"

  # Download CLAUDE.md
  print_info "Downloading CLAUDE.md..."
  curl -sL "${OMNILABS_REPO}/.claude/CLAUDE.md" -o ".claude/CLAUDE.md"
  print_success "Installed CLAUDE.md"
}

install_merge() {
  print_warning "Existing .claude/ directory detected — running in merge mode"

  mkdir -p .claude/agents

  # Install agents (skip existing)
  for agent in "${AGENTS[@]}"; do
    if [ -f ".claude/agents/${agent}" ]; then
      print_warning "Skipping ${agent} (already exists)"
    else
      print_info "Downloading ${agent}..."
      curl -sL "${OMNILABS_REPO}/.claude/agents/${agent}" -o ".claude/agents/${agent}"
      print_success "Installed ${agent}"
    fi
  done

  # Handle settings.json
  if [ -f "${SETTINGS_FILE}" ]; then
    if grep -q "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS" "${SETTINGS_FILE}" 2>/dev/null; then
      print_success "Agent teams already enabled in settings.json"
    else
      print_warning "settings.json exists but agent teams may not be enabled"
      print_warning "Add this to your .claude/settings.json manually:"
      echo ""
      echo '  "env": {'
      echo '    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"'
      echo '  }'
      echo ""
    fi
  else
    print_info "Creating settings.json..."
    curl -sL "${OMNILABS_REPO}/.claude/settings.json" -o "${SETTINGS_FILE}"
    print_success "Created settings.json with agent teams enabled"
  fi

  # Handle CLAUDE.md
  if [ -f ".claude/CLAUDE.md" ]; then
    print_warning "Skipping CLAUDE.md (already exists)"
    print_info "You can append OmniLabs instructions manually from:"
    print_info "${OMNILABS_REPO}/.claude/CLAUDE.md"
  else
    print_info "Downloading CLAUDE.md..."
    curl -sL "${OMNILABS_REPO}/.claude/CLAUDE.md" -o ".claude/CLAUDE.md"
    print_success "Installed CLAUDE.md"
  fi
}

verify_installation() {
  echo ""
  print_info "Verifying installation..."

  local count=0
  for agent in "${AGENTS[@]}"; do
    if [ -f ".claude/agents/${agent}" ]; then
      count=$((count + 1))
    else
      print_error "Missing: ${agent}"
    fi
  done

  echo ""
  if [ "$count" -eq "${#AGENTS[@]}" ]; then
    print_success "All ${count} agents installed successfully!"
  else
    print_warning "${count}/${#AGENTS[@]} agents installed"
  fi

  if [ -f "${SETTINGS_FILE}" ]; then
    print_success "settings.json present"
  else
    print_error "settings.json missing"
  fi

  echo ""
  echo -e "${GREEN}Installation complete!${NC}"
  echo ""
  echo "Next steps:"
  echo "  1. Open Claude Code in this project"
  echo "  2. Copy the prompt from agent-team-prompt.md (or use the README)"
  echo "  3. Paste it to launch your OmniLabs analysis"
  echo ""
}

# Main
print_banner
check_dependencies

MODE=$(detect_install_mode)

if [ "$MODE" = "fresh" ]; then
  install_fresh
else
  install_merge
fi

verify_installation
