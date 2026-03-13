"""OmniLabs MCP Server v0.3 — YAML-driven extensible agents.

Adding a new agent = one YAML file.
  - Contributors: PR a .yaml into agents/builtin/
  - Users: drop a .yaml into ~/.omnilabs/agents/
"""

from __future__ import annotations

import json
import sys
from typing import Any

from fastmcp import FastMCP

from .agents.registry import registry
from .core.models import AgentStatus
from .core.store import store
from .dashboard.app import DASHBOARD_PORT, start_dashboard, write_agents_meta

mcp = FastMCP(
    name="OmniLabs",
    instructions=(
        f"{len(registry)} specialized AI agents for project analysis. "
        f"Agents: {', '.join(registry.ids())}. "
        "No API key needed. "
        f"Dashboard at http://localhost:{DASHBOARD_PORT}"
    ),
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOLS — Session lifecycle
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@mcp.tool()
def start_analysis(
    repo_path: str,
    agents: list[str] | None = None,
) -> dict[str, Any]:
    """Start a new OmniLabs analysis session.

    Args:
        repo_path: Path to the repository to analyze.
        agents: Which agents to run. Defaults to all registered agents.
                Use list_agents to see available options.

    Returns:
        Session info with selected agents and dashboard URL.
    """
    if agents:
        unknown = [a for a in agents if a not in registry]
        if unknown:
            return {"error": f"Unknown agents: {unknown}", "available": registry.ids()}
        agent_ids = agents
    else:
        agent_ids = registry.ids()

    session = store.create_session(repo_path, agent_ids)
    return {
        "session_id": session.session_id,
        "target_repo": repo_path,
        "agents": agent_ids,
        "dashboard": f"http://localhost:{DASHBOARD_PORT}",
        "next_step": "Call get_agent_prompt for each agent you want to run.",
    }


@mcp.tool()
def get_agent_prompt(agent: str, session_id: str | None = None) -> dict[str, Any]:
    """Get the specialized system prompt for an agent.

    You (Claude Code) ARE the agent. Use this prompt as your persona
    when analyzing the codebase. No API key needed.

    Args:
        agent: Agent ID (e.g. "technical", "security").
        session_id: Session ID. Defaults to current.
    """
    spec = registry.get(agent)
    if spec is None:
        return {"error": f"Unknown agent '{agent}'.", "available": registry.ids()}

    session = store.get_session(session_id) if session_id else store.current_session
    if session is None:
        return {"error": "No active session. Call start_analysis first."}

    store.mark_running(session.session_id, agent)
    return {
        "agent": spec.id,
        "name": spec.name,
        "session_id": session.session_id,
        "target_repo": session.target_repo,
        "system_prompt": spec.system_prompt,
        "instructions": (
            f"You are now the OmniLabs {spec.name} agent ({spec.icon}). "
            f"Read the entire codebase at {session.target_repo}, then follow "
            f"the system prompt above to produce your analysis. "
            f"Every finding MUST cite specific files and code as evidence. "
            f"When done, call save_agent_result with your output."
        ),
    }


@mcp.tool()
def save_agent_result(
    agent: str,
    analysis: str,
    summary: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Save completed analysis from an agent."""
    session = store.get_session(session_id) if session_id else store.current_session
    if session is None:
        return {"error": "No active session."}

    if summary is None:
        summary = analysis[:200] + "..." if len(analysis) > 200 else analysis

    store.save_result(session.session_id, agent, summary, analysis)
    r = session.agents.get(agent)
    return {
        "agent": agent,
        "status": "completed",
        "duration_seconds": r.duration_seconds if r else None,
        "dashboard": f"http://localhost:{DASHBOARD_PORT}",
    }


@mcp.tool()
def mark_agent_error(agent: str, error: str, session_id: str | None = None) -> dict[str, Any]:
    """Mark an agent as failed."""
    session = store.get_session(session_id) if session_id else store.current_session
    if session is None:
        return {"error": "No active session."}
    store.mark_failed(session.session_id, agent, error)
    return {"agent": agent, "status": "failed", "error": error}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOLS — Query
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@mcp.tool()
def list_agents(tag: str | None = None) -> list[dict]:
    """List all registered agents.

    Args:
        tag: Optional tag filter (e.g. "core", "engineering", "compliance").
    """
    agents = registry.all()
    if tag:
        agents = [a for a in agents if tag in a.tags]
    return [a.to_catalog_entry() for a in agents]


@mcp.tool()
def get_session_status(session_id: str | None = None) -> dict[str, Any]:
    """Check status of all agents in a session."""
    session = store.get_session(session_id) if session_id else store.current_session
    if session is None:
        return {"error": "No active session."}
    r = session.to_dict()
    r["dashboard"] = f"http://localhost:{DASHBOARD_PORT}"
    return r


@mcp.tool()
def get_agent_output(agent: str, session_id: str | None = None) -> dict[str, Any]:
    """Get full output from a completed agent."""
    session = store.get_session(session_id) if session_id else store.current_session
    if session is None:
        return {"error": "No active session."}

    r = session.agents.get(agent)
    if r is None:
        return {"error": f"'{agent}' not in session."}
    if r.status == AgentStatus.IDLE:
        return {"status": "idle", "message": f"'{agent}' hasn't run yet."}
    if r.status == AgentStatus.RUNNING:
        return {"status": "running", "message": f"'{agent}' is still analyzing."}

    return {
        "agent": agent,
        "status": r.status.value,
        "duration_seconds": r.duration_seconds,
        "output": r.raw_output,
        "error": r.error,
    }


@mcp.tool()
def list_sessions() -> list[dict]:
    """List all analysis sessions."""
    return store.list_sessions() or [{"message": "No sessions yet."}]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RESOURCES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@mcp.resource("omnilabs://agents/catalog")
def agents_catalog() -> str:
    """Full agent catalog — auto-generated from YAML definitions."""
    return json.dumps({
        "agents": [s.to_catalog_entry() for s in registry],
        "total": len(registry),
        "how_to_add": "Drop a .yaml file in agents/builtin/ (PR) or ~/.omnilabs/agents/ (local)",
    }, indent=2)


@mcp.resource("omnilabs://session/current")
def current_session_resource() -> str:
    session = store.current_session
    return session.to_json() if session else json.dumps({"message": "No active session."})


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PROMPTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@mcp.prompt()
def full_analysis(repo_path: str) -> str:
    """Run ALL registered agents on a project."""
    ids = ", ".join(registry.ids())
    return (
        f"Complete OmniLabs analysis on: {repo_path}\n\n"
        f"1. Call start_analysis.\n"
        f"2. For each agent ({ids}):\n"
        f"   a. get_agent_prompt -> read codebase -> produce analysis -> save_agent_result\n"
        f"3. Synthesize unified report with GO / CONDITIONAL GO / NO-GO.\n"
    )


@mcp.prompt()
def focused_analysis(repo_path: str, agents: str) -> str:
    """Run specific agents (comma-separated)."""
    return (
        f"Focused analysis on: {repo_path}\nAgents: {agents}\n\n"
        f"1. start_analysis with agents=[{agents}].\n"
        f"2. Run each -> save results -> synthesize.\n"
    )


@mcp.prompt()
def quick_health_check(repo_path: str) -> str:
    """Quick technical + adversarial check."""
    return (
        f"Quick health check on: {repo_path}\n\n"
        f"1. start_analysis with agents=['technical', 'adversarial'].\n"
        f"2. Run both -> summarize scores, risks, and actions.\n"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENTRYPOINT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def main():
    # Write agent metadata for dashboard
    meta = {spec.id: {"icon": spec.icon, "focus": spec.focus, "tags": spec.tags} for spec in registry}
    write_agents_meta(meta)

    # Start dashboard
    try:
        start_dashboard()
        print(f"OmniLabs dashboard: http://localhost:{DASHBOARD_PORT}", file=sys.stderr)
    except OSError:
        print(f"Dashboard port {DASHBOARD_PORT} in use, skipping.", file=sys.stderr)

    agents = ", ".join(f"{s.icon} {s.id}" for s in registry)
    print(f"Agents ({len(registry)}): {agents}", file=sys.stderr)

    mcp.run()


if __name__ == "__main__":
    main()
