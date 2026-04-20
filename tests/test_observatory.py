"""Observatory core tests — store, recorder, hooks, discovery."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

import pytest

# ── Fixtures ──────────────────────────────────────────────

@pytest.fixture(autouse=True)
def tmp_db(monkeypatch, tmp_path):
    """Redirect DB to a temp file so tests don't touch ~/.omnilabs."""
    db = tmp_path / "test.db"
    import omnilabs.observatory.store as store
    monkeypatch.setattr(store, "DB_PATH", db)
    store.init_db()
    return db


@pytest.fixture()
def tmp_settings(tmp_path):
    """Temp settings.json for hooks tests."""
    f = tmp_path / "settings.json"
    f.write_text('{"hooks":{"PreToolUse":[{"hooks":[{"type":"command","command":"existing"}]}]}}')
    return f


# ── Store ─────────────────────────────────────────────────

def test_ensure_session_creates_row():
    from omnilabs.observatory.store import ensure_session, _connect
    sid = ensure_session("sess-abc", "/proj")
    with _connect() as conn:
        row = conn.execute("SELECT * FROM sessions WHERE id=?", (sid,)).fetchone()
    assert row["claude_session_id"] == "sess-abc"
    assert row["project_path"] == "/proj"


def test_ensure_session_idempotent():
    from omnilabs.observatory.store import ensure_session
    sid1 = ensure_session("sess-abc", "/proj")
    sid2 = ensure_session("sess-abc", "/proj")
    assert sid1 == sid2


def test_ensure_session_creates_root_run():
    from omnilabs.observatory.store import ensure_session, get_run_id
    sid = ensure_session("sess-xyz", "/proj")
    run_id = get_run_id(sid, "__root__")
    assert run_id is not None


def test_insert_and_update_tool_event():
    from omnilabs.observatory.store import (
        ensure_session, get_run_id, insert_pre_tool, update_post_tool, list_events
    )
    ts = time.time()
    sid = ensure_session("sess-tool", "/proj")
    run = get_run_id(sid, "__root__")
    insert_pre_tool(run, "use_001", "Read", '{"file_path":"x.py"}', ts)
    update_post_tool("use_001", "ok", ts + 0.05)

    events = list_events(sid)
    assert len(events) == 1
    assert events[0]["tool_name"] == "Read"
    assert events[0]["duration_ms"] == pytest.approx(50, abs=10)


def test_subagent_run_tracked_separately():
    from omnilabs.observatory.store import (
        ensure_session, upsert_agent_run, get_run_id, insert_pre_tool,
        list_agent_runs, list_events
    )
    ts = time.time()
    sid = ensure_session("sess-sub", "/proj")
    root = get_run_id(sid, "__root__")
    sub  = upsert_agent_run(sid, "agent-explore", "Explore")

    insert_pre_tool(root, "u1", "Read",  '{}', ts)
    insert_pre_tool(sub,  "u2", "Grep",  '{}', ts + 0.01)

    runs = list_agent_runs(sid)
    assert len(runs) == 2
    events = list_events(sid)
    assert len(events) == 2


def test_close_session():
    from omnilabs.observatory.store import ensure_session, close_session, _connect
    ensure_session("sess-close", "/proj")
    close_session("sess-close")
    with _connect() as conn:
        row = conn.execute(
            "SELECT status FROM sessions WHERE claude_session_id=?", ("sess-close",)
        ).fetchone()
    assert row["status"] == "completed"


def test_file_edit_inserted():
    from omnilabs.observatory.store import ensure_session, get_run_id, insert_file_edit, list_file_edits
    sid = ensure_session("sess-edit", "/proj")
    run = get_run_id(sid, "__root__")
    insert_file_edit(run, "evt_u1", "foo.py", "edit", "--- a\n+++ b\n- old\n+ new")
    edits = list_file_edits(sid)
    assert len(edits) == 1
    assert edits[0]["file_path"] == "foo.py"


# ── Hooks installer ───────────────────────────────────────

def test_hooks_install_preserves_existing(tmp_settings, monkeypatch):
    from omnilabs.observatory import hooks
    monkeypatch.chdir(tmp_settings.parent)

    # Write the settings file where hooks.install expects it
    dot_claude = tmp_settings.parent / ".claude"
    dot_claude.mkdir()
    settings = dot_claude / "settings.json"
    settings.write_text('{"hooks":{"PreToolUse":[{"hooks":[{"type":"command","command":"existing"}]}]}}')

    hooks.install(project=True)
    data = json.loads(settings.read_text())
    pre = data["hooks"]["PreToolUse"]
    # Existing entry preserved
    assert any(e.get("hooks", [{}])[0].get("command") == "existing" for e in pre)
    # OmniLabs entry added
    assert any(e.get("_omnilabs") for e in pre)


def test_hooks_install_idempotent(tmp_path, monkeypatch):
    from omnilabs.observatory import hooks
    dot_claude = tmp_path / ".claude"
    dot_claude.mkdir()
    settings = dot_claude / "settings.json"
    settings.write_text("{}")
    monkeypatch.chdir(tmp_path)

    hooks.install(project=True)
    hooks.install(project=True)

    data = json.loads(settings.read_text())
    for event in hooks._EVENTS:
        omnilabs_count = sum(1 for e in data["hooks"].get(event, []) if e.get("_omnilabs"))
        assert omnilabs_count == 1, f"{event} has {omnilabs_count} omnilabs entries"


def test_hooks_uninstall_restores(tmp_path, monkeypatch):
    from omnilabs.observatory import hooks
    dot_claude = tmp_path / ".claude"
    dot_claude.mkdir()
    original = '{"custom":"value"}'
    settings = dot_claude / "settings.json"
    settings.write_text(original)
    monkeypatch.chdir(tmp_path)

    hooks.install(project=True)
    hooks.uninstall(project=True)

    # Backup removed, settings restored
    assert not settings.with_suffix(".json.omnilabs.bak").exists()
    assert json.loads(settings.read_text()) == {"custom": "value"}


# ── Recorder ─────────────────────────────────────────────

def test_recorder_pre_post(monkeypatch, tmp_path):
    """Full round-trip: pipe hook payloads through recorder, verify DB."""
    import omnilabs.observatory.store as store
    db = tmp_path / "rec.db"
    monkeypatch.setattr(store, "DB_PATH", db)

    import io
    from omnilabs.observatory import recorder

    def pipe(event_type, payload):
        monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
        monkeypatch.setattr(sys, "argv", ["omnilabs", event_type])
        out = io.StringIO()
        monkeypatch.setattr(sys, "stdout", out)
        recorder.main()
        return out.getvalue()

    cwd = str(tmp_path)
    base = {"session_id": "rec-sess", "cwd": cwd}

    pipe("SessionStart", base)
    pipe("PreToolUse", {**base, "tool_name": "Read", "tool_input": {"file_path": "f.py"}, "tool_use_id": "u1"})
    out = pipe("PreToolUse", {**base, "tool_name": "Grep", "tool_input": {"pattern": "x"}, "tool_use_id": "u2"})
    assert '{"decision":"approve"}' in out

    pipe("PostToolUse", {**base, "tool_name": "Read", "tool_use_id": "u1", "tool_response": "content"})

    store.init_db()
    events = store.list_events(store.ensure_session("rec-sess", cwd))
    assert len(events) == 2
    read_evt = next(e for e in events if e["tool_name"] == "Read")
    assert read_evt["result_summary"] == "content"


def test_recorder_never_crashes_on_bad_input(monkeypatch, tmp_path):
    import omnilabs.observatory.store as store
    monkeypatch.setattr(store, "DB_PATH", tmp_path / "x.db")
    import io
    from omnilabs.observatory import recorder

    monkeypatch.setattr(sys, "stdin", io.StringIO("NOT JSON {{{"))
    monkeypatch.setattr(sys, "argv", ["omnilabs", "PreToolUse"])
    out = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out)
    recorder.main()   # must not raise
    assert "approve" in out.getvalue()


# ── Discovery ─────────────────────────────────────────────

def test_discovery_finds_subagents(tmp_path):
    from omnilabs.observatory.discovery import scan

    agents_dir = tmp_path / ".claude" / "agents"
    agents_dir.mkdir(parents=True)
    (agents_dir / "my-agent.md").write_text("# My Agent\nDoes stuff.")

    found = scan(str(tmp_path))
    ids = [a["agent_id"] for a in found]
    assert "my-agent" in ids
    assert any(a["source_type"] == "subagent" for a in found if a["agent_id"] == "my-agent")


def test_discovery_finds_skills(tmp_path):
    from omnilabs.observatory.discovery import scan

    skill_dir = tmp_path / ".claude" / "skills" / "my-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("---\nname: My Skill\n---\nDoes stuff.")

    found = scan(str(tmp_path))
    ids = [a["agent_id"] for a in found]
    assert "my-skill" in ids


# ── Hook perf benchmark ───────────────────────────────────

def test_hook_recorder_perf(monkeypatch, tmp_path):
    """Each recorder invocation must complete in under 100ms (budget: 50ms p95)."""
    import omnilabs.observatory.store as store
    monkeypatch.setattr(store, "DB_PATH", tmp_path / "perf.db")
    store.init_db()

    import io
    from omnilabs.observatory import recorder

    timings = []
    for i in range(20):
        payload = {
            "session_id": "perf-sess",
            "cwd": str(tmp_path),
            "tool_name": "Read",
            "tool_input": {"file_path": f"file_{i}.py"},
            "tool_use_id": f"u_{i}",
        }
        monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
        monkeypatch.setattr(sys, "argv", ["omnilabs", "PreToolUse"])
        monkeypatch.setattr(sys, "stdout", io.StringIO())

        t0 = time.perf_counter()
        recorder.main()
        timings.append((time.perf_counter() - t0) * 1000)

    timings.sort()
    p95 = timings[int(len(timings) * 0.95)]
    assert p95 < 100, f"p95 hook overhead {p95:.1f}ms exceeds 100ms budget"
