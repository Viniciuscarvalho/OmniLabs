# OmniLabs — Agent Observatory for Claude Code

## What is OmniLabs?

OmniLabs is a **hook-based agent observatory**: it discovers every agent, skill, and subagent
in your Claude Code project, captures every tool call via Claude Code hooks, and shows it all
live in a local dashboard at `http://localhost:3141`.

No MCP configuration required. Install as a Python package and run `/omnilabs watch`.

## Architecture

```
src/omnilabs/
├── cli.py                      # omnilabs CLI entry point
├── observatory/
│   ├── store.py                # SQLite store (~/.omnilabs/db.sqlite, WAL mode)
│   ├── recorder.py             # Called by hooks: omnilabs record <Event>
│   ├── hooks.py                # Install/uninstall hooks in settings.json (idempotent, .bak)
│   ├── discovery.py            # Scan .claude/agents/, .claude/skills/, packs
│   └── server.py               # HTTP + SSE server at :3141
├── dashboard/
│   └── index.html              # Live / Timeline / Replay dashboard
├── agents/
│   ├── spec.py                 # AgentSpec dataclass
│   └── registry.py             # Pack discovery
├── packs/
│   └── strategic_analysis/     # business / financial / technical / adversarial YAMLs
└── skill/
    └── SKILL.md                # /omnilabs Claude Code skill
```

## Capture Flow

1. Claude Code fires a hook (e.g. `PreToolUse`)
2. Hook calls `omnilabs record PreToolUse` (stdin = JSON payload)
3. Recorder writes to `~/.omnilabs/db.sqlite` in <50ms
4. Dashboard SSE endpoint polls for new rows and streams them to the browser

## Hook Events Captured

| Event              | What it records                                   |
| ------------------ | ------------------------------------------------- |
| `SessionStart`     | New session + project path + agent discovery      |
| `PreToolUse`       | Tool name, args, agent_id, tool_use_id            |
| `PostToolUse`      | Result summary, computed duration via tool_use_id |
| `Stop`             | Session close                                     |
| `UserPromptSubmit` | Session marker                                    |

## SQLite Schema

```
sessions         — id, project_path, claude_session_id, started_at, ended_at
agent_runs       — id, session_id, claude_agent_id, agent_type, started_at, ended_at
tool_events      — id, run_id, tool_use_id, tool_name, args_json, result_summary, duration_ms
file_edits       — id, run_id, file_path, edit_type, diff_text
discovered_agents — project_path, agent_id, source_type, source_path, last_seen
```

## How to Use

```bash
pip install -e .
omnilabs hooks install --project   # installs capture hooks
# restart Claude Code
omnilabs watch                     # starts server + opens http://localhost:3141
```

### CLI Reference

```
omnilabs watch                     # start observatory dashboard
omnilabs hooks install --project   # install capture hooks
omnilabs hooks uninstall --project # restore original settings.json
omnilabs hooks status              # check hook installation
omnilabs agents list               # show discovered agents/skills/packs
omnilabs pack list                 # show available packs
omnilabs pack install <name>       # install pack agents into .claude/agents/
omnilabs sessions list             # list captured sessions
omnilabs events list <session>     # list tool events for a session
omnilabs gc --older-than 30d       # prune old events
```

## Strategic-Analysis Pack

The 4 core OmniLabs analysis agents ship as an optional pack in
`src/omnilabs/packs/strategic_analysis/`. Install them with:

```bash
omnilabs pack install strategic-analysis
```

This drops subagent markdown files into `.claude/agents/` so they are
discoverable by the observatory and invocable via Claude Code's Task() tool.

## Design Principles

- **No external dependencies** — stdlib only (sqlite3, http.server, json, argparse)
- **Non-blocking hooks** — recorder always outputs `{"decision":"approve"}` before any DB I/O
- **Safe hook installer** — idempotent, `.bak` sidecar, clean uninstall
- **Code-first discovery** — scans the actual project structure, not a manifest

## Knowledge Base Search Protocol

Before starting any analysis task, search the knowledge base for relevant prior findings:

1. Use `mcp__docs-mcp-server__search_docs` with library `omnilabs-memories`
2. Search with 2-3 keyword variations
3. Review top results for applicable patterns

Use the `continuous-learning` skill to capture reusable knowledge to `.claude/memories/`.
