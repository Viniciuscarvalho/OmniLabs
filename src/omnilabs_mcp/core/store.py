"""Session store — in-memory storage for analysis sessions.

SEC-13 will add JSON file persistence for dashboard sync.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from .models import AgentResult, AgentStatus, AgentType, AnalysisSession


class SessionStore:
    """Manages analysis sessions in memory."""

    def __init__(self) -> None:
        self._sessions: dict[str, AnalysisSession] = {}
        self._current_session_id: str | None = None

    @property
    def current_session(self) -> AnalysisSession | None:
        if self._current_session_id:
            return self._sessions.get(self._current_session_id)
        return None

    def create_session(self, target_repo: str) -> AnalysisSession:
        session_id = uuid.uuid4().hex[:8]
        session = AnalysisSession(session_id=session_id, target_repo=target_repo)
        for agent_type in AgentType:
            session.agents[agent_type] = AgentResult(agent=agent_type)
        self._sessions[session_id] = session
        self._current_session_id = session_id
        return session

    def get_session(self, session_id: str) -> AnalysisSession | None:
        return self._sessions.get(session_id)

    def list_sessions(self) -> list[dict]:
        return [s.to_dict() for s in self._sessions.values()]

    def mark_running(self, session_id: str, agent: AgentType) -> None:
        session = self._sessions.get(session_id)
        if session and agent in session.agents:
            session.agents[agent].status = AgentStatus.RUNNING
            session.agents[agent].started_at = datetime.now(timezone.utc)

    def save_result(
        self,
        session_id: str,
        agent: AgentType,
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

    def mark_failed(self, session_id: str, agent: AgentType, error: str) -> None:
        session = self._sessions.get(session_id)
        if session and agent in session.agents:
            session.agents[agent].status = AgentStatus.FAILED
            session.agents[agent].completed_at = datetime.now(timezone.utc)
            session.agents[agent].error = error


# Global singleton
store = SessionStore()
