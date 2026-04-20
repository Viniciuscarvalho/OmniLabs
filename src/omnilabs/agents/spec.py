"""Agent specification — the contract every OmniLabs agent must fulfill."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AgentSpec:
    """One YAML file = one AgentSpec = one agent."""

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
            raise ValueError(f"Agent '{self.id}' system_prompt too short.")

    @property
    def prompt_tokens_estimate(self) -> int:
        return len(self.system_prompt) // 4

    @property
    def cost_tier(self) -> str:
        t = self.prompt_tokens_estimate
        if t < 1000:
            return "light"
        elif t < 3000:
            return "medium"
        return "heavy"

    def to_catalog_entry(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "icon": self.icon,
            "focus": self.focus,
            "key_outputs": self.key_outputs,
            "tags": self.tags,
            "prompt_tokens": self.prompt_tokens_estimate,
            "cost_tier": self.cost_tier,
        }
