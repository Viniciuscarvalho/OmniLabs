"""
Hook recorder — called by Claude Code hooks: omnilabs record <EventType>

Reads JSON payload from stdin, writes to SQLite (~/.omnilabs/db.sqlite).
Outputs approve decision for blocking hooks (PreToolUse, PostToolUse).
Always exits 0 — a recorder crash must never affect Claude Code.
"""

from __future__ import annotations

import json
import os
import sys
import time

_BLOCKING = {"PreToolUse", "PostToolUse"}


def main() -> None:
    event_type = sys.argv[1] if len(sys.argv) > 1 else "Unknown"

    # Approve blocking events immediately — don't make Claude Code wait on DB I/O
    if event_type in _BLOCKING:
        sys.stdout.write('{"decision":"approve"}\n')
        sys.stdout.flush()

    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        payload = {}

    try:
        _record(event_type, payload)
    except Exception:
        pass  # never surface recorder errors to Claude Code


def _record(event_type: str, payload: dict) -> None:
    from . import store

    store.init_db()

    claude_session_id = payload.get("session_id", "unknown")
    project_path = payload.get("cwd") or os.getcwd()
    ts = time.time()

    if event_type == "SessionStart":
        store.ensure_session(claude_session_id, project_path)
        # Run discovery in the background — never block the hook
        try:
            from .discovery import scan, save
            found = scan(project_path)
            save(found, project_path)
        except Exception:
            pass
        return

    if event_type == "Stop":
        store.close_session(claude_session_id)
        return

    # Ensure session + resolve which agent_run this event belongs to
    session_id = store.ensure_session(claude_session_id, project_path)

    claude_agent_id = payload.get("agent_id") or "__root__"
    agent_type = payload.get("agent_type")

    if claude_agent_id == "__root__":
        run_id = store.get_run_id(session_id, "__root__")
    else:
        run_id = store.upsert_agent_run(session_id, claude_agent_id, agent_type)

    if event_type == "PreToolUse":
        tool_use_id = payload.get("tool_use_id", f"noid_{int(ts * 1000)}")
        tool_name = payload.get("tool_name", "Unknown")
        tool_input = payload.get("tool_input") or {}
        args_json = json.dumps(tool_input, separators=(",", ":")) if tool_input else None
        store.insert_pre_tool(run_id, tool_use_id, tool_name, args_json, ts)
        # Capture file edits from Edit/Write tool_input
        if tool_name in ("Edit", "Write", "MultiEdit"):
            _capture_file_edit(run_id, f"evt_{tool_use_id}", tool_name, tool_input)

    elif event_type == "PostToolUse":
        tool_use_id = payload.get("tool_use_id", "")
        if not tool_use_id:
            return
        tool_response = payload.get("tool_response")
        if tool_response is not None:
            raw = str(tool_response)
            result_summary = raw[:500] if len(raw) > 500 else raw
        else:
            result_summary = None
        store.update_post_tool(tool_use_id, result_summary, ts)


def _capture_file_edit(run_id: str, tool_event_id: str, tool_name: str, tool_input: dict) -> None:
    """Store diff/content for Edit and Write tool calls."""
    from . import store

    file_path = tool_input.get("file_path", "")
    if not file_path:
        return

    if tool_name == "Edit":
        old_str = tool_input.get("old_string", "")
        new_str = tool_input.get("new_string", "")
        import difflib
        diff = "".join(difflib.unified_diff(
            old_str.splitlines(keepends=True),
            new_str.splitlines(keepends=True),
            fromfile="before",
            tofile="after",
            n=2,
        ))
        store.insert_file_edit(run_id, tool_event_id, file_path, "edit", diff or "(no diff)")

    elif tool_name == "Write":
        content = tool_input.get("content", "")
        store.insert_file_edit(run_id, tool_event_id, file_path, "write", content[:3000])

    elif tool_name == "MultiEdit":
        edits = tool_input.get("edits") or []
        for i, edit in enumerate(edits):
            old_str = edit.get("old_string", "")
            new_str = edit.get("new_string", "")
            import difflib
            diff = "".join(difflib.unified_diff(
                old_str.splitlines(keepends=True),
                new_str.splitlines(keepends=True),
                fromfile="before",
                tofile="after",
                n=2,
            ))
            store.insert_file_edit(run_id, f"{tool_event_id}_{i}", file_path, "edit", diff)
