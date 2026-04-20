"""
Install and uninstall OmniLabs capture hooks in Claude Code settings.json.

Safety guarantees:
- Idempotent: installing twice is identical to installing once
- Backup: a .bak sidecar is written before any mutation (never overwritten)
- Uninstall: removes exactly what was added, then removes the backup
- Non-clobbering: existing hooks in the same event slot are preserved
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

_MARKER = "_omnilabs"
_EVENTS = ["SessionStart", "PreToolUse", "PostToolUse", "Stop", "UserPromptSubmit"]


def _settings_path(project: bool = False) -> Path:
    if project:
        return Path(".claude") / "settings.json"
    return Path.home() / ".claude" / "settings.json"


def _hook_entry(event: str) -> dict:
    return {
        _MARKER: True,
        "hooks": [{"type": "command", "command": f"omnilabs record {event}"}],
    }


def _is_omnilabs(obj: object) -> bool:
    return isinstance(obj, dict) and bool(obj.get(_MARKER))


def install(project: bool = False) -> Path:
    """Install OmniLabs hooks. Returns the path modified."""
    path = _settings_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)

    data = json.loads(path.read_text()) if path.exists() else {}

    # Write backup once — never overwrite an existing backup
    bak = path.with_suffix(".json.omnilabs.bak")
    if not bak.exists():
        bak.write_text(json.dumps(data, indent=2) + "\n")

    hooks = data.setdefault("hooks", {})
    changed = False
    for event in _EVENTS:
        slot = hooks.setdefault(event, [])
        if not any(_is_omnilabs(e) for e in slot):
            slot.append(_hook_entry(event))
            changed = True

    if changed:
        path.write_text(json.dumps(data, indent=2) + "\n")

    return path


def uninstall(project: bool = False) -> Path:
    """Remove OmniLabs hooks. Restores from .bak if available."""
    path = _settings_path(project)
    bak = path.with_suffix(".json.omnilabs.bak")

    if bak.exists():
        shutil.copy2(bak, path)
        bak.unlink()
        return path

    if not path.exists():
        return path

    data = json.loads(path.read_text())
    hooks = data.get("hooks", {})

    for event in list(hooks.keys()):
        hooks[event] = [e for e in hooks[event] if not _is_omnilabs(e)]
        if not hooks[event]:
            del hooks[event]

    if not hooks:
        data.pop("hooks", None)

    path.write_text(json.dumps(data, indent=2) + "\n")
    return path


def status(project: bool = False) -> dict[str, bool]:
    """Return which events have OmniLabs hooks installed."""
    path = _settings_path(project)
    if not path.exists():
        return {e: False for e in _EVENTS}
    data = json.loads(path.read_text())
    hooks = data.get("hooks", {})
    return {
        event: any(_is_omnilabs(e) for e in hooks.get(event, []))
        for event in _EVENTS
    }
