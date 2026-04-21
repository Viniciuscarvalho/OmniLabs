"""Agent registry — auto-discovers YAML agent definitions from packs.

Discovery order (later overrides earlier):
  1. src/omnilabs/packs/strategic_analysis/*.yaml  (shipped strategic-analysis pack)
  2. ~/.omnilabs/packs/*/                          (user-installed packs)
  3. ~/.omnilabs/agents/*.yaml                     (legacy user-local overrides)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterator

from .spec import AgentSpec

BUILTIN_PACK_DIR = Path(__file__).parent.parent / "packs" / "strategic_analysis"
USER_PACKS_DIR = Path.home() / ".omnilabs" / "packs"
USER_AGENTS_DIR = Path.home() / ".omnilabs" / "agents"


class AgentRegistry:
    """Central registry. Immutable after startup."""

    def __init__(self) -> None:
        self._agents: dict[str, AgentSpec] = {}

    def register(self, spec: AgentSpec) -> None:
        self._agents[spec.id] = spec

    def get(self, agent_id: str) -> AgentSpec | None:
        return self._agents.get(agent_id)

    def all(self) -> list[AgentSpec]:
        return list(self._agents.values())

    def ids(self) -> list[str]:
        return list(self._agents.keys())

    def __len__(self) -> int:
        return len(self._agents)

    def __contains__(self, agent_id: str) -> bool:
        return agent_id in self._agents

    def __iter__(self) -> Iterator[AgentSpec]:
        return iter(self._agents.values())


# ──────────────────────────────────────────────
# YAML parser (no PyYAML dependency)
# ──────────────────────────────────────────────

def _parse_yaml(text: str) -> dict:
    """Minimal YAML parser for agent definitions."""
    data: dict = {}
    lines = text.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]

        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue

        match = re.match(r'^(\w[\w-]*)\s*:\s*(.*)', line)
        if not match:
            i += 1
            continue

        key = match.group(1)
        value = match.group(2).strip()

        if value == "|":
            block: list[str] = []
            i += 1
            while i < len(lines):
                if lines[i] == "" or lines[i][0] in (" ", "\t"):
                    block.append(lines[i])
                    i += 1
                else:
                    break
            if block:
                indent = len(block[0]) - len(block[0].lstrip())
                data[key] = "\n".join(
                    line[indent:] if len(line) > indent else line for line in block
                ).strip()
            continue

        elif value.startswith("[") and value.endswith("]"):
            inner = value[1:-1]
            data[key] = [s.strip().strip("\"'") for s in inner.split(",") if s.strip()]

        elif value == "":
            items: list[str] = []
            i += 1
            while i < len(lines):
                stripped = lines[i].strip()
                if stripped.startswith("- "):
                    items.append(stripped[2:].strip().strip("\"'"))
                    i += 1
                elif stripped == "" or stripped.startswith("#"):
                    i += 1
                else:
                    break
            if items:
                data[key] = items
            continue

        else:
            if (value.startswith('"') and value.endswith('"')) or \
               (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            data[key] = value

        i += 1

    return data


def _load_yaml_agent(path: Path) -> AgentSpec:
    data = _parse_yaml(path.read_text(encoding="utf-8"))

    key_outputs = data.get("key_outputs", [])
    if isinstance(key_outputs, str):
        key_outputs = [key_outputs]

    tags = data.get("tags", [])
    if isinstance(tags, str):
        tags = [tags]

    return AgentSpec(
        id=data["id"],
        name=data["name"],
        icon=data.get("icon", "\U0001f916"),
        focus=data["focus"],
        key_outputs=key_outputs,
        system_prompt=data["system_prompt"],
        tags=tags,
    )


def _discover_from_dir(registry: AgentRegistry, directory: Path, label: str) -> None:
    if not directory.is_dir():
        return
    for path in sorted(directory.glob("*.yaml")):
        try:
            spec = _load_yaml_agent(path)
            registry.register(spec)
        except Exception as e:
            print(f"Warning: failed to load {label} agent from {path.name}: {e}", file=sys.stderr)


def build_registry() -> AgentRegistry:
    """Build the global registry from all YAML sources."""
    registry = AgentRegistry()
    _discover_from_dir(registry, BUILTIN_PACK_DIR, "strategic-analysis")
    # User packs: each subdirectory is a pack
    if USER_PACKS_DIR.is_dir():
        for pack_dir in sorted(USER_PACKS_DIR.iterdir()):
            if pack_dir.is_dir():
                _discover_from_dir(registry, pack_dir, f"pack:{pack_dir.name}")
    _discover_from_dir(registry, USER_AGENTS_DIR, "user")
    return registry


registry = build_registry()
