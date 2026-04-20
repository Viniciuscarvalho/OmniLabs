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
