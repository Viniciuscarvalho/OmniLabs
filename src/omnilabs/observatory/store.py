"""SQLite-backed event store for OmniLabs observatory.

Schema lives in ~/.omnilabs/db.sqlite (WAL mode).
All writes are short-lived connections — safe for concurrent hook invocations.
"""

from __future__ import annotations

import sqlite3
import time
from pathlib import Path

DB_PATH = Path.home() / ".omnilabs" / "db.sqlite"

_SCHEMA = """\
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;

CREATE TABLE IF NOT EXISTS sessions (
    id                 TEXT PRIMARY KEY,
    project_path       TEXT NOT NULL,
    claude_session_id  TEXT UNIQUE NOT NULL,
    started_at         REAL NOT NULL,
    ended_at           REAL,
    status             TEXT NOT NULL DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS agent_runs (
    id               TEXT PRIMARY KEY,
    session_id       TEXT NOT NULL,
    parent_run_id    TEXT,
    claude_agent_id  TEXT NOT NULL DEFAULT '__root__',
    agent_type       TEXT,
    source           TEXT NOT NULL DEFAULT 'session',
    started_at       REAL NOT NULL,
    ended_at         REAL,
    status           TEXT NOT NULL DEFAULT 'running',
    FOREIGN KEY (session_id) REFERENCES sessions(id),
    UNIQUE (session_id, claude_agent_id)
);

CREATE TABLE IF NOT EXISTS tool_events (
    id              TEXT PRIMARY KEY,
    run_id          TEXT NOT NULL,
    tool_use_id     TEXT UNIQUE,
    tool_name       TEXT NOT NULL,
    args_json       TEXT,
    result_summary  TEXT,
    started_at      REAL NOT NULL,
    ended_at        REAL,
    duration_ms     REAL,
    FOREIGN KEY (run_id) REFERENCES agent_runs(id)
);

CREATE TABLE IF NOT EXISTS file_edits (
    id            TEXT PRIMARY KEY,
    run_id        TEXT NOT NULL,
    tool_event_id TEXT,
    file_path     TEXT NOT NULL,
    edit_type     TEXT NOT NULL,
    before_hash   TEXT,
    after_hash    TEXT,
    diff_text     TEXT
);

CREATE TABLE IF NOT EXISTS discovered_agents (
    project_path  TEXT NOT NULL,
    agent_id      TEXT NOT NULL,
    source_type   TEXT NOT NULL,
    source_path   TEXT NOT NULL,
    spec_json     TEXT,
    last_seen     REAL NOT NULL,
    PRIMARY KEY (project_path, agent_id)
);

CREATE INDEX IF NOT EXISTS idx_runs_session   ON agent_runs(session_id);
CREATE INDEX IF NOT EXISTS idx_events_run     ON tool_events(run_id);
CREATE INDEX IF NOT EXISTS idx_events_use_id  ON tool_events(tool_use_id);
CREATE INDEX IF NOT EXISTS idx_edits_run      ON file_edits(run_id);
"""


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), timeout=5)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.executescript(_SCHEMA)


def ensure_session(claude_session_id: str, project_path: str) -> str:
    """Return internal session id, creating it (+ root agent_run) if needed."""
    now = time.time()
    with _connect() as conn:
        row = conn.execute(
            "SELECT id FROM sessions WHERE claude_session_id = ?",
            (claude_session_id,),
        ).fetchone()
        if row:
            return row["id"]

        session_id = f"sess_{int(now * 1000)}_{claude_session_id[:8]}"
        conn.execute(
            "INSERT INTO sessions (id, project_path, claude_session_id, started_at) VALUES (?,?,?,?)",
            (session_id, project_path, claude_session_id, now),
        )
        run_id = f"run_{session_id}___root__"
        conn.execute(
            "INSERT OR IGNORE INTO agent_runs "
            "(id, session_id, claude_agent_id, agent_type, source, started_at) "
            "VALUES (?,?,?,?,?,?)",
            (run_id, session_id, "__root__", "root", "session", now),
        )
        return session_id


def upsert_agent_run(
    session_id: str,
    claude_agent_id: str,
    agent_type: str | None,
) -> str:
    """Get or create an agent_run for (session, agent). Returns run_id."""
    now = time.time()
    with _connect() as conn:
        row = conn.execute(
            "SELECT id FROM agent_runs WHERE session_id = ? AND claude_agent_id = ?",
            (session_id, claude_agent_id),
        ).fetchone()
        if row:
            return row["id"]

        run_id = f"run_{session_id}_{claude_agent_id[:16]}"
        conn.execute(
            "INSERT OR IGNORE INTO agent_runs "
            "(id, session_id, claude_agent_id, agent_type, source, started_at) "
            "VALUES (?,?,?,?,?,?)",
            (run_id, session_id, claude_agent_id, agent_type, "subagent", now),
        )
        return run_id


def get_run_id(session_id: str, claude_agent_id: str) -> str:
    """Return run_id for (session, agent), creating root run if missing."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT id FROM agent_runs WHERE session_id = ? AND claude_agent_id = ?",
            (session_id, claude_agent_id),
        ).fetchone()
        if row:
            return row["id"]
    return upsert_agent_run(session_id, claude_agent_id, None)


def insert_pre_tool(
    run_id: str,
    tool_use_id: str,
    tool_name: str,
    args_json: str | None,
    ts: float,
) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO tool_events "
            "(id, run_id, tool_use_id, tool_name, args_json, started_at) "
            "VALUES (?,?,?,?,?,?)",
            (f"evt_{tool_use_id}", run_id, tool_use_id, tool_name, args_json, ts),
        )


def update_post_tool(
    tool_use_id: str,
    result_summary: str | None,
    now: float,
) -> None:
    with _connect() as conn:
        conn.execute(
            """UPDATE tool_events
               SET result_summary = ?,
                   ended_at       = ?,
                   duration_ms    = ROUND((? - started_at) * 1000, 2)
               WHERE tool_use_id = ?""",
            (result_summary, now, now, tool_use_id),
        )


def close_session(claude_session_id: str) -> None:
    now = time.time()
    with _connect() as conn:
        conn.execute(
            "UPDATE sessions SET ended_at=?, status='completed' WHERE claude_session_id=?",
            (now, claude_session_id),
        )
        conn.execute(
            """UPDATE agent_runs SET ended_at=?, status='completed'
               WHERE session_id=(SELECT id FROM sessions WHERE claude_session_id=?)
               AND ended_at IS NULL""",
            (now, claude_session_id),
        )


def list_sessions(project_path: str | None = None, limit: int = 20) -> list[dict]:
    with _connect() as conn:
        if project_path:
            rows = conn.execute(
                "SELECT * FROM sessions WHERE project_path=? ORDER BY started_at DESC LIMIT ?",
                (project_path, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM sessions ORDER BY started_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]


def list_events(session_id: str, limit: int = 100) -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            """SELECT te.id, te.tool_name, te.args_json, te.result_summary,
                      te.started_at, te.duration_ms, ar.claude_agent_id, ar.agent_type
               FROM tool_events te
               JOIN agent_runs ar ON te.run_id = ar.id
               WHERE ar.session_id = ?
               ORDER BY te.started_at DESC LIMIT ?""",
            (session_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]


def count_events(session_id: str) -> int:
    with _connect() as conn:
        row = conn.execute(
            """SELECT COUNT(*) AS n FROM tool_events te
               JOIN agent_runs ar ON te.run_id = ar.id
               WHERE ar.session_id = ?""",
            (session_id,),
        ).fetchone()
        return row["n"] if row else 0
