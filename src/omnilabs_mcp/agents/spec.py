"""Agent specification — the contract every OmniLabs agent must fulfill.

To create a new agent: add a .yaml file in agents/builtin/ (for PRs)
or in ~/.omnilabs/agents/ (for personal/local agents).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AgentSpec:
    """Everything OmniLabs needs to know about an agent.

    One YAML file = one AgentSpec = one agent.
    """

    id: str
    name: str
    icon: str
    focus: str
    key_outputs: list[str]
    system_prompt: str
    tags: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.id.replace("_", "").replace("-", "").isalnum():
            raise ValueError(f"Agent id must be alphanumeric (with _ or -): got '{self.id}'")
        if len(self.system_prompt) < 100:
            raise ValueError(f"Agent '{self.id}' system_prompt too short — agents need detailed prompts.")

    def to_catalog_entry(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "icon": self.icon,
            "focus": self.focus,
            "key_outputs": self.key_outputs,
            "tags": self.tags,
        }
