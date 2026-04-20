<p align="center">
  <img src="assets/omnilabs-banner.svg" alt="OmniLabs Banner" width="100%">
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-ffd60a?style=flat-square" alt="MIT License"></a>
  <a href="https://claude.com/claude-code"><img src="https://img.shields.io/badge/Claude_Code-skill-a855f7?style=flat-square" alt="Claude Code"></a>
  <a href="#capture"><img src="https://img.shields.io/badge/Capture-hooks-22c55e?style=flat-square" alt="Hooks-based capture"></a>
  <a href="#replay"><img src="https://img.shields.io/badge/Replay-session_diff-3b82f6?style=flat-square" alt="Session replay"></a>
  <a href="#packs"><img src="https://img.shields.io/badge/Packs-YAML-9ca3af?style=flat-square" alt="YAML packs"></a>
  <a href="https://github.com/sponsors/Viniciuscarvalho"><img src="https://img.shields.io/badge/Sponsor-%E2%9D%A4-ea4aaa?style=flat-square&logo=github-sponsors&logoColor=white" alt="Sponsor"></a>
</p>

<p align="center">
  <strong>The agent observatory for Claude Code.</strong><br>
  See every agent, skill, and subagent running in your project — live, replayable, diffable.
</p>

---

## What It Does

OmniLabs watches the agents already living in your project and shows you exactly what they're doing. When Claude Code fans out subagents in parallel, invokes a skill, or edits files across a long session, your terminal hides most of it. OmniLabs surfaces it.

- **Discovers** every subagent, skill, and YAML pack in your project
- **Captures** every tool call, file edit, and subagent fan-out via Claude Code hooks
- **Streams** activity live to a local dashboard at `:3141`
- **Replays** any session — scrub the timeline, see what each agent did, diff the files
- **Packs** — optional YAML agent bundles (strategic-analysis ships with 4 core agents)
- **No MCP required** — installs as a Claude Code skill

---

## Quick Start

```bash
pip install omnilabs
cd your-project
/omnilabs watch
```

That's it. The first run installs Claude Code hooks into your settings (with a backup), opens the dashboard at `http://localhost:3141`, and starts capturing. Every time Claude Code runs a tool, spawns a subagent, or invokes a skill, you see it.

To stop: `/omnilabs stop` or `omnilabs hooks uninstall` (restores `settings.json` byte-identical).

---

## What You'll See

### Live view

- Real-time tree of agents currently running, with parallel branches when Claude Code fans out
- Every tool call (Read, Edit, Write, Bash, Task, Skill) with args, result, duration
- Tailing stdout for long-running Bash commands
- Cost + token accounting per agent run

### Timeline

- Every past session in your project
- Gantt-style view of agent runs with tool events overlaid
- Filter by agent, tool, file, or time range

### Replay

- Scrub bar over any session
- At each position: which agents were running, the latest tool call, and the cumulative set of file changes
- Per-file diff rendered from content-addressed blob storage

---

## Discovery

On session start (and any time you run `omnilabs agents list`), OmniLabs scans:

```
./.claude/agents/*.md              ← project subagents
./.claude/skills/*/SKILL.md        ← project skills
~/.claude/skills/*/SKILL.md        ← user skills
~/.omnilabs/packs/                 ← installed YAML packs
```

Whatever it finds populates the "discovered agents" panel. No configuration, no manifest.

---

## Capture

OmniLabs installs these Claude Code hooks into your `settings.json`:

| Hook               | What it records                                 |
| ------------------ | ----------------------------------------------- |
| `SessionStart`     | Project root, Claude Code session id, timestamp |
| `UserPromptSubmit` | Prompt text, session marker                     |
| `PreToolUse`       | Tool name, args, parent agent                   |
| `PostToolUse`      | Tool result, duration, file hashes if edit      |
| `SubagentStart`    | Child run linked to parent (parallel fan-out)   |
| `SubagentStop`     | Completion, status, token usage                 |
| `Stop`             | Session close                                   |

Events land in `~/.omnilabs/db.sqlite`. File content is stored once per unique hash in `~/.omnilabs/blobs/`. Hook overhead budget: <50ms p95.

Uninstall is clean: a `.bak` sidecar is written on first install, and `omnilabs hooks uninstall` restores the original file.

---

## Packs

Packs are optional bundles of agents the observatory can invoke. They drop subagent markdown into your `.claude/agents/` so they're discovered like any other subagent — there's no special runtime.

### Install the strategic-analysis pack

```bash
omnilabs pack install strategic-analysis
```

Ships 4 agents: `business`, `financial`, `technical`, `adversarial`. Full docs in `packs/strategic-analysis/README.md`.

### Create your own pack

A pack is a directory of `.yaml` agent specs and a `pack.yaml` manifest. The YAML format stays the same:

```yaml
id: security
name: Security Audit
icon: "🛡️"
focus: Vulnerability assessment, auth review, OWASP Top 10
tags: [engineering, compliance]
key_outputs:
  - Vulnerability inventory by severity
  - Auth & authorization audit
system_prompt: |
  You are a senior application security engineer...
```

Drop the directory in `~/.omnilabs/packs/` and `omnilabs pack install <name>` materializes it into your project's `.claude/agents/`.

See [`examples/TEMPLATE.yaml`](examples/TEMPLATE.yaml) for a starter.

---

## CLI

| Command                              | Description                                    |
| ------------------------------------ | ---------------------------------------------- |
| `omnilabs watch`                     | Start observer + dashboard for current project |
| `omnilabs stop`                      | Stop observer (leaves hooks installed)         |
| `omnilabs agents list`               | Show discovered agents/skills/packs            |
| `omnilabs sessions list`             | Past sessions for this project                 |
| `omnilabs replay <session-id>`       | Open replay view for a session                 |
| `omnilabs pack list`                 | Available packs                                |
| `omnilabs pack install <name>`       | Install a pack into `.claude/agents/`          |
| `omnilabs hooks install [--project]` | Install capture hooks (user or project scope)  |
| `omnilabs hooks uninstall`           | Restore original `settings.json`               |
| `omnilabs gc --older-than 30d`       | Prune old events and blobs                     |

---

## Project Structure

```
OmniLabs/
├── src/omnilabs/
│   ├── cli.py                          # CLI entry point
│   ├── observatory/
│   │   ├── hooks.py                    # Hook installer (idempotent + .bak)
│   │   ├── recorder.py                 # Fast event writer called by hooks
│   │   ├── store.py                    # SQLite schema + queries
│   │   ├── discovery.py                # Scan project for agents/skills/packs
│   │   ├── replay.py                   # Session replay assembly + diff
│   │   └── server.py                   # Local HTTP + SSE server (:3141)
│   ├── dashboard/                      # Live / timeline / replay views
│   ├── agents/
│   │   ├── spec.py                     # AgentSpec dataclass
│   │   └── registry.py                 # Pack + project-local discovery
│   ├── packs/
│   │   └── strategic_analysis/         # business / financial / technical / adversarial
│   └── skill/
│       └── SKILL.md                    # /omnilabs skill
├── examples/
├── tests/
├── evaluation/
├── docs/
├── pyproject.toml
└── LICENSE
```

---

## Requirements

- Python 3.11+
- [Claude Code](https://claude.com/claude-code) CLI (hooks require the Claude Code harness)
- SQLite (bundled with Python)

---

## Contributing

New packs and improvements welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

---

<p align="center">
  <sub>MIT License — see <a href="LICENSE">LICENSE</a></sub>
</p>
