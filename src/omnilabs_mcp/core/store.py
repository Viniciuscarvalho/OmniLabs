"""Session store — in-memory + JSON file for dashboard sync."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .models import AgentResult, AgentStatus, AnalysisSession

# Dashboard reads from this file
STATE_FILE = Path.home() / ".omnilabs" / "state.json"


class SessionStore:
    """Manages analysis sessions and syncs state to disk for the dashboard."""

    def __init__(self) -> None:
        self._sessions: dict[str, AnalysisSession] = {}
        self._current_session_id: str | None = None
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    @property
    def current_session(self) -> AnalysisSession | None:
        if self._current_session_id:
            return self._sessions.get(self._current_session_id)
        return None

    def create_session(self, target_repo: str, agent_ids: list[str]) -> AnalysisSession:
        session_id = uuid.uuid4().hex[:8]
        session = AnalysisSession(session_id=session_id, target_repo=target_repo)
        for agent_id in agent_ids:
            session.agents[agent_id] = AgentResult(agent=agent_id)
        self._sessions[session_id] = session
        self._current_session_id = session_id
        self._sync()
        return session

    def get_session(self, session_id: str) -> AnalysisSession | None:
        return self._sessions.get(session_id)

    def list_sessions(self) -> list[dict]:
        return [s.to_dict() for s in self._sessions.values()]

    def mark_running(self, session_id: str, agent: str) -> None:
        session = self._sessions.get(session_id)
        if session and agent in session.agents:
            session.agents[agent].status = AgentStatus.RUNNING
            session.agents[agent].started_at = datetime.now(timezone.utc)
            self._sync()

    def save_result(
        self,
        session_id: str,
        agent: str,
        summary: str,
        raw_output: str,
    ) -> None:
        session = self._sessions.get(session_id)
        if session and agent in session.agents:
            result = session.agents[agent]
            result.status = AgentStatus.COMPLETED
            result.completed_at = datetime.now(timezone.utc)
            result.summary = summary
            result.raw_output = raw_output
            self._sync()

    def mark_failed(self, session_id: str, agent: str, error: str) -> None:
        session = self._sessions.get(session_id)
        if session and agent in session.agents:
            session.agents[agent].status = AgentStatus.FAILED
            session.agents[agent].completed_at = datetime.now(timezone.utc)
            session.agents[agent].error = error
            self._sync()

    def _sync(self) -> None:
        """Write current state to JSON file for dashboard consumption."""
        try:
            state = {
                "current_session_id": self._current_session_id,
                "sessions": {sid: s.to_dict() for sid, s in self._sessions.items()},
            }
            STATE_FILE.write_text(json.dumps(state, indent=2, default=str))
        except Exception:
            pass  # Dashboard sync is best-effort


# Global singleton
store = SessionStore()
