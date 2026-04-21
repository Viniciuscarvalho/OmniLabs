"""Scan a project directory for agents, skills, and OmniLabs packs."""

from __future__ import annotations

import os
import re
import time
from pathlib import Path


def _md_name(path: Path) -> str:
    """Extract first # heading from a markdown file."""
    try:
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    except OSError:
        pass
    return path.stem


def _skill_name(path: Path) -> str:
    """Extract name from SKILL.md frontmatter or first heading."""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r'^name:\s*(.+)$', text, re.MULTILINE)
        if m:
            return m.group(1).strip()
        for line in text.splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    except OSError:
        pass
    return path.parent.name


def scan(project_path: str | None = None) -> list[dict]:
    """Return all discoverable agents/skills for the project. Never raises."""
    root = Path(project_path or os.getcwd())
    found: list[dict] = []

    # .claude/agents/*.md — project subagents
    for f in sorted((root / ".claude" / "agents").glob("*.md")):
        found.append({
            "agent_id": f.stem,
            "source_type": "subagent",
            "source_path": str(f),
            "name": _md_name(f),
        })

    # .claude/skills/*/SKILL.md — project skills
    for f in sorted((root / ".claude" / "skills").glob("*/SKILL.md")):
        found.append({
            "agent_id": f.parent.name,
            "source_type": "project-skill",
            "source_path": str(f),
            "name": _skill_name(f),
        })

    # ~/.claude/skills/*/SKILL.md — user skills
    for f in sorted((Path.home() / ".claude" / "skills").glob("*/SKILL.md")):
        if not any(a["agent_id"] == f.parent.name for a in found):
            found.append({
                "agent_id": f.parent.name,
                "source_type": "user-skill",
                "source_path": str(f),
                "name": _skill_name(f),
            })

    # OmniLabs packs
    try:
        from ..agents.registry import build_registry
        for spec in build_registry():
            found.append({
                "agent_id": spec.id,
                "source_type": "omnilabs-pack",
                "source_path": f"packs/strategic_analysis/{spec.id}.yaml",
                "name": f"{spec.icon} {spec.name}",
            })
    except Exception:
        pass

    return found


def save(found: list[dict], project_path: str) -> None:
    """Persist discovered agents to the SQLite store."""
    from . import store
    store.init_db()
    now = time.time()
    with store._connect() as conn:
        for a in found:
            conn.execute(
                """INSERT OR REPLACE INTO discovered_agents
                   (project_path, agent_id, source_type, source_path, last_seen)
                   VALUES (?,?,?,?,?)""",
                (project_path, a["agent_id"], a["source_type"], a["source_path"], now),
            )
