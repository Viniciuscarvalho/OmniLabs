"""Core data models for OmniLabs sessions and agents."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentResult(BaseModel):
    agent: str
    status: AgentStatus = AgentStatus.IDLE
    started_at: datetime | None = None
    completed_at: datetime | None = None
    summary: str | None = None
    raw_output: str | None = None
    error: str | None = None

    @property
    def duration_seconds(self) -> float | None:
        if self.started_at and self.completed_at:
            return round((self.completed_at - self.started_at).total_seconds(), 1)
        return None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "duration_seconds": self.duration_seconds,
            "has_output": self.raw_output is not None,
            "error": self.error,
        }


class AnalysisSession(BaseModel):
    session_id: str
    target_repo: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    agents: dict[str, AgentResult] = Field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "target_repo": self.target_repo,
            "created_at": self.created_at.isoformat(),
            "agents": {name: r.to_dict() for name, r in self.agents.items()},
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
