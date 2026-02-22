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

EVAL_GRADERS=(
  "common.sh"
  "grade-business-product.sh"
  "grade-financial-cost.sh"
  "grade-technical-arch.sh"
  "grade-devils-advocate.sh"
  "grade-lead-synthesis.sh"
)

EVAL_RUBRICS=(
  "rubric-business-product.md"
  "rubric-financial-cost.md"
  "rubric-technical-arch.md"
  "rubric-devils-advocate.md"
  "rubric-lead-synthesis.md"
)

EVAL_HARNESS=(
  "run-eval.sh"
  "run-all.sh"
  "report.sh"
)

EVAL_DATASETS=(
  "golden-saas-project.md"
  "golden-risky-project.md"
  "golden-early-stage.md"
)

DOCS_FILES=(
  "architecture.md"
  "contributing-evals.md"
  "evaluation-guide.md"
)

SETTINGS_FILE='.claude/settings.json'
WITH_EVALS=0

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

print_help() {
  echo "Usage: bash install.sh [--with-evals] [--help]"
  echo ""
  echo "Options:"
  echo "  --with-evals   Also install the evaluation framework (graders, tasks, datasets, docs)"
  echo "  --help         Show this help message"
}

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

install_evals() {
  print_info "Installing evaluation framework..."

  # Create directories
  mkdir -p evaluation/graders/code-based
  mkdir -p evaluation/graders/model-based
  mkdir -p evaluation/harness
  mkdir -p evaluation/datasets
  mkdir -p evaluation/results
  mkdir -p docs

  # Download code-based graders
  for grader in "${EVAL_GRADERS[@]}"; do
    if [ -f "evaluation/graders/code-based/${grader}" ]; then
      print_warning "Skipping ${grader} (already exists)"
    else
      print_info "Downloading grader: ${grader}..."
      curl -sL "${OMNILABS_REPO}/evaluation/graders/code-based/${grader}" -o "evaluation/graders/code-based/${grader}"
      chmod +x "evaluation/graders/code-based/${grader}"
      print_success "Installed ${grader}"
    fi
  done

  # Download model-based rubrics
  for rubric in "${EVAL_RUBRICS[@]}"; do
    if [ -f "evaluation/graders/model-based/${rubric}" ]; then
      print_warning "Skipping ${rubric} (already exists)"
    else
      print_info "Downloading rubric: ${rubric}..."
      curl -sL "${OMNILABS_REPO}/evaluation/graders/model-based/${rubric}" -o "evaluation/graders/model-based/${rubric}"
      print_success "Installed ${rubric}"
    fi
  done

  # Download harness scripts
  for script in "${EVAL_HARNESS[@]}"; do
    if [ -f "evaluation/harness/${script}" ]; then
      print_warning "Skipping ${script} (already exists)"
    else
      print_info "Downloading harness: ${script}..."
      curl -sL "${OMNILABS_REPO}/evaluation/harness/${script}" -o "evaluation/harness/${script}"
      chmod +x "evaluation/harness/${script}"
      print_success "Installed ${script}"
    fi
  done

  # Download golden datasets
  for dataset in "${EVAL_DATASETS[@]}"; do
    if [ -f "evaluation/datasets/${dataset}" ]; then
      print_warning "Skipping ${dataset} (already exists)"
    else
      print_info "Downloading dataset: ${dataset}..."
      curl -sL "${OMNILABS_REPO}/evaluation/datasets/${dataset}" -o "evaluation/datasets/${dataset}"
      print_success "Installed ${dataset}"
    fi
  done

  # Download docs
  for doc in "${DOCS_FILES[@]}"; do
    if [ -f "docs/${doc}" ]; then
      print_warning "Skipping ${doc} (already exists)"
    else
      print_info "Downloading doc: ${doc}..."
      curl -sL "${OMNILABS_REPO}/docs/${doc}" -o "docs/${doc}"
      print_success "Installed ${doc}"
    fi
  done

  # Download eval README
  if [ ! -f "evaluation/README.md" ]; then
    curl -sL "${OMNILABS_REPO}/evaluation/README.md" -o "evaluation/README.md"
    print_success "Installed evaluation/README.md"
  fi

  # Create .gitkeep in results
  touch evaluation/results/.gitkeep

  print_success "Evaluation framework installed!"
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

  if [ "$WITH_EVALS" -eq 1 ]; then
    local eval_ok=1
    [ -f "evaluation/graders/code-based/common.sh" ] || { print_error "Missing: common.sh"; eval_ok=0; }
    [ -f "evaluation/harness/run-eval.sh" ] || { print_error "Missing: run-eval.sh"; eval_ok=0; }
    [ -d "docs" ] || { print_error "Missing: docs/"; eval_ok=0; }
    if [ "$eval_ok" -eq 1 ]; then
      print_success "Evaluation framework present"
    fi
  fi

  echo ""
  echo -e "${GREEN}Installation complete!${NC}"
  echo ""
  echo "Next steps:"
  echo "  1. Open Claude Code in this project"
  echo "  2. Copy the prompt from agent-team-prompt.md (or use the README)"
  echo "  3. Paste it to launch your OmniLabs analysis"
  if [ "$WITH_EVALS" -eq 1 ]; then
    echo "  4. Run evals: bash evaluation/harness/run-all.sh"
  else
    echo ""
    echo "To also install the evaluation framework, re-run with --with-evals"
  fi
  echo ""
}

# --- Parse Arguments ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    --with-evals) WITH_EVALS=1; shift ;;
    --help) print_help; exit 0 ;;
    *) echo "Unknown option: $1"; print_help; exit 1 ;;
  esac
done

# Main
print_banner
check_dependencies

MODE=$(detect_install_mode)

if [ "$MODE" = "fresh" ]; then
  install_fresh
else
  install_merge
fi

if [ "$WITH_EVALS" -eq 1 ]; then
  echo ""
  install_evals
fi

verify_installation
