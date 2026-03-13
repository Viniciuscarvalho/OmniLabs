"""Tests for OmniLabs v0.3 — YAML-driven agent architecture."""

import textwrap
from pathlib import Path

from omnilabs_mcp.agents.spec import AgentSpec
from omnilabs_mcp.agents.registry import _parse_yaml, _load_yaml_agent, registry, AgentRegistry
from omnilabs_mcp.core.store import SessionStore


class TestAgentSpec:
    def test_valid_spec(self):
        spec = AgentSpec(
            id="test",
            name="Test Agent",
            icon="\U0001f9ea",
            focus="Testing things",
            key_outputs=["Report"],
            system_prompt="x" * 101,
        )
        assert spec.id == "test"

    def test_short_prompt_rejected(self):
        try:
            AgentSpec(id="bad", name="Bad", icon="\u274c", focus="x",
                      key_outputs=[], system_prompt="too short")
            assert False, "Should have raised"
        except ValueError:
            pass

    def test_catalog_entry(self):
        spec = AgentSpec(id="a", name="A", icon="\U0001f170\ufe0f", focus="f",
                         key_outputs=["o1"], system_prompt="x" * 101, tags=["core"])
        entry = spec.to_catalog_entry()
        assert entry["id"] == "a"
        assert "core" in entry["tags"]


class TestYamlParser:
    def test_simple_values(self):
        data = _parse_yaml('id: test\nname: "Test Agent"')
        assert data["id"] == "test"
        assert data["name"] == "Test Agent"

    def test_inline_list(self):
        data = _parse_yaml("tags: [core, engineering]")
        assert data["tags"] == ["core", "engineering"]

    def test_block_list(self):
        text = "key_outputs:\n  - First\n  - Second\n  - Third"
        data = _parse_yaml(text)
        assert data["key_outputs"] == ["First", "Second", "Third"]

    def test_multiline_block(self):
        text = "system_prompt: |\n  Line one.\n  Line two.\n  Line three."
        data = _parse_yaml(text)
        assert "Line one." in data["system_prompt"]
        assert "Line three." in data["system_prompt"]

    def test_comments_ignored(self):
        data = _parse_yaml("# comment\nid: test\n# another comment")
        assert data["id"] == "test"

    def test_load_yaml_agent(self, tmp_path):
        yaml_text = textwrap.dedent("""\
            id: test_agent
            name: Test Agent
            icon: "\U0001f9ea"
            focus: Testing the parser
            tags: [test]
            key_outputs:
              - Output one
              - Output two
            system_prompt: |
              You are a test agent. This prompt must be long enough to pass
              validation. It needs to be over one hundred characters total.
              So here is some more text to make it work properly for the test.
        """)
        path = tmp_path / "test_agent.yaml"
        path.write_text(yaml_text)
        spec = _load_yaml_agent(path)
        assert spec.id == "test_agent"
        assert spec.name == "Test Agent"
        assert len(spec.key_outputs) == 2
        assert "test agent" in spec.system_prompt.lower()


class TestRegistry:
    def test_builtin_agents_discovered(self):
        assert len(registry) >= 4
        assert "business" in registry
        assert "financial" in registry
        assert "technical" in registry
        assert "adversarial" in registry

    def test_all_agents_have_substantial_prompts(self):
        for spec in registry:
            assert len(spec.system_prompt) > 500, f"{spec.id} prompt too short"

    def test_all_agents_require_evidence(self):
        for spec in registry:
            prompt_lower = spec.system_prompt.lower()
            has_evidence = "evidence" in prompt_lower or "critical" in prompt_lower
            assert has_evidence, f"{spec.id} doesn't require evidence"

    def test_user_override(self):
        r = AgentRegistry()
        original = AgentSpec(id="x", name="Original", icon="\u0031\ufe0f\u20e3",
                             focus="f", key_outputs=[], system_prompt="a" * 101)
        override = AgentSpec(id="x", name="Override", icon="\u0032\ufe0f\u20e3",
                             focus="f", key_outputs=[], system_prompt="b" * 101)
        r.register(original)
        r.register(override)
        assert r.get("x").name == "Override"


class TestStore:
    def test_dynamic_agent_session(self):
        s = SessionStore()
        session = s.create_session("/tmp/repo", ["technical", "security", "custom"])
        assert len(session.agents) == 3
        assert "security" in session.agents
        assert "custom" in session.agents

    def test_full_lifecycle(self):
        s = SessionStore()
        session = s.create_session("/tmp/repo", ["technical"])
        sid = session.session_id

        s.mark_running(sid, "technical")
        assert session.agents["technical"].status.value == "running"

        s.save_result(sid, "technical", "Summary", "Full output")
        assert session.agents["technical"].status.value == "completed"
        assert session.agents["technical"].raw_output == "Full output"

    def test_failure(self):
        s = SessionStore()
        session = s.create_session("/tmp/repo", ["financial"])
        s.mark_failed(session.session_id, "financial", "Timeout")
        assert session.agents["financial"].status.value == "failed"
