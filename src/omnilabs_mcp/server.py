"""OmniLabs MCP Server — No API key required.

Architecture: Claude Code IS the agent. This server provides:
  - Specialized prompts for each agent role
  - Session tracking and state management
  - A live dashboard at http://localhost:3141

Connect to Claude Code with:
    claude mcp add omnilabs -- uv run --directory /path/to/omnilabs python -m omnilabs_mcp

Then just ask: "Analyze ~/projects/my-app with OmniLabs"
"""

from __future__ import annotations

import json
import sys
from typing import Any

from fastmcp import FastMCP

from .agents.prompts import AGENT_PROMPTS
from .core.models import AgentStatus, AgentType
from .core.store import store
from .dashboard.app import DASHBOARD_PORT, start_dashboard

mcp = FastMCP(
    name="OmniLabs",
    instructions=(
        "4 specialized AI agents for comprehensive project analysis. "
        "No API key needed — Claude Code is the executor. "
        "Live dashboard at http://localhost:3141"
    ),
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOLS — Session lifecycle
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@mcp.tool()
def start_analysis(repo_path: str) -> dict[str, Any]:
    """Start a new OmniLabs analysis session for a repository.

    Creates a session and returns the list of available agents.
    Call get_agent_prompt next for each agent you want to run.

    Args:
        repo_path: Absolute path to the repository to analyze.

    Returns:
        Session info with available agents and dashboard URL.
    """
    session = store.create_session(repo_path)
    return {
        "session_id": session.session_id,
        "target_repo": repo_path,
        "agents": [a.value for a in AgentType],
        "dashboard": f"http://localhost:{DASHBOARD_PORT}",
        "next_step": "Call get_agent_prompt for each agent you want to run.",
    }


@mcp.tool()
def get_agent_prompt(
    agent: str,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Get the specialized system prompt for an agent.

    Returns the full expert prompt that YOU (Claude Code) should use
    as your persona/instructions when analyzing the codebase.
    Read the entire codebase, then follow this prompt to produce
    the analysis. No API key needed — you are the agent.

    Args:
        agent: One of: business, financial, technical, adversarial.
        session_id: Session ID. Defaults to current session.

    Returns:
        The system prompt and instructions for this agent role.
    """
    session = store.get_session(session_id) if session_id else store.current_session
    if session is None:
        return {"error": "No active session. Call start_analysis first."}

    agent_type = AgentType(agent.lower())
    store.mark_running(session.session_id, agent_type)

    return {
        "agent": agent_type.value,
        "session_id": session.session_id,
        "target_repo": session.target_repo,
        "system_prompt": AGENT_PROMPTS[agent_type],
        "instructions": (
            f"You are now the OmniLabs {agent_type.value} agent. "
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
    """Save the completed analysis from an agent.

    Call this after you've completed the agent analysis to store
    the results and update the dashboard.

    Args:
        agent: Which agent produced this analysis.
        analysis: The full analysis output.
        summary: Optional short summary (first ~200 chars used if omitted).
        session_id: Session ID. Defaults to current session.

    Returns:
        Confirmation with duration and dashboard link.
    """
    session = store.get_session(session_id) if session_id else store.current_session
    if session is None:
        return {"error": "No active session."}

    agent_type = AgentType(agent.lower())

    if summary is None:
        summary = analysis[:200] + "..." if len(analysis) > 200 else analysis

    store.save_result(
        session_id=session.session_id,
        agent=agent_type,
        summary=summary,
        raw_output=analysis,
    )

    result = session.agents[agent_type]
    return {
        "agent": agent_type.value,
        "status": "completed",
        "duration_seconds": result.duration_seconds,
        "dashboard": f"http://localhost:{DASHBOARD_PORT}",
    }


@mcp.tool()
def mark_agent_error(
    agent: str,
    error: str,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Mark an agent as failed with an error message.

    Args:
        agent: Which agent failed.
        error: Error description.
        session_id: Session ID. Defaults to current session.
    """
    session = store.get_session(session_id) if session_id else store.current_session
    if session is None:
        return {"error": "No active session."}

    agent_type = AgentType(agent.lower())
    store.mark_failed(session.session_id, agent_type, error)
    return {"agent": agent_type.value, "status": "failed", "error": error}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOLS — Query results
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@mcp.tool()
def get_session_status(session_id: str | None = None) -> dict[str, Any]:
    """Check the status of all agents in a session.

    Args:
        session_id: Session to check. Defaults to current session.

    Returns:
        Status of each agent with dashboard link.
    """
    session = store.get_session(session_id) if session_id else store.current_session
    if session is None:
        return {"error": "No active session. Call start_analysis first."}

    result = session.to_dict()
    result["dashboard"] = f"http://localhost:{DASHBOARD_PORT}"
    return result


@mcp.tool()
def get_agent_output(
    agent: str,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Get the full analysis output from a completed agent.

    Args:
        agent: One of: business, financial, technical, adversarial.
        session_id: Session to query. Defaults to current session.

    Returns:
        Complete analysis text from the agent.
    """
    session = store.get_session(session_id) if session_id else store.current_session
    if session is None:
        return {"error": "No active session."}

    agent_type = AgentType(agent.lower())
    result = session.agents.get(agent_type)

    if result is None:
        return {"error": f"Agent '{agent}' not found."}
    if result.status == AgentStatus.IDLE:
        return {"status": "idle", "message": f"Agent '{agent}' hasn't been run yet."}
    if result.status == AgentStatus.RUNNING:
        return {"status": "running", "message": f"Agent '{agent}' is still analyzing."}

    return {
        "agent": agent_type.value,
        "status": result.status.value,
        "duration_seconds": result.duration_seconds,
        "output": result.raw_output,
        "error": result.error,
    }


@mcp.tool()
def list_sessions() -> list[dict]:
    """List all analysis sessions."""
    sessions = store.list_sessions()
    if not sessions:
        return [{"message": "No sessions yet. Use start_analysis to begin."}]
    return sessions


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RESOURCES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@mcp.resource("omnilabs://agents/catalog")
def agents_catalog() -> str:
    """Catalog of all available OmniLabs agents."""
    catalog = {
        "agents": [
            {
                "id": "business",
                "name": "Business & Product Analysis",
                "focus": "Product-market fit, competitive landscape, GTM readiness",
                "key_outputs": [
                    "Business viability score (1-10)",
                    "TAM/SAM/SOM",
                    "Competitive moat",
                ],
            },
            {
                "id": "financial",
                "name": "Financial & Cost Analysis",
                "focus": "TCO modeling, unit economics, infrastructure cost at scale",
                "key_outputs": [
                    "TCO at 1K/10K/100K/1M users",
                    "Break-even analysis",
                    "Cost optimization",
                ],
            },
            {
                "id": "technical",
                "name": "Technical Architecture Review",
                "focus": "6-dimension scoring: scalability, reliability, maintainability, security, observability, operability",
                "key_outputs": [
                    "6-dimension scores",
                    "Tech debt inventory",
                    "Production readiness verdict",
                ],
            },
            {
                "id": "adversarial",
                "name": "Devil's Advocate Challenge",
                "focus": "Assumption deconstruction, pre-mortem, competitor counterattack",
                "key_outputs": [
                    "Failure post-mortem",
                    "Assumption risk matrix",
                    "Uncomfortable questions",
                ],
            },
        ],
        "dashboard": f"http://localhost:{DASHBOARD_PORT}",
        "note": "No API key required — Claude Code executes each agent role directly.",
    }
    return json.dumps(catalog, indent=2)


@mcp.resource("omnilabs://session/current")
def current_session_resource() -> str:
    """Current analysis session status."""
    session = store.current_session
    if session is None:
        return json.dumps({"message": "No active session."})
    return session.to_json()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PROMPTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@mcp.prompt()
def full_analysis(repo_path: str) -> str:
    """Run a comprehensive 4-agent analysis on a project."""
    return (
        f"Run a complete OmniLabs analysis on: {repo_path}\n\n"
        f"1. Call start_analysis with the repo path.\n"
        f"2. For each agent (business, financial, technical, adversarial):\n"
        f"   a. Call get_agent_prompt to get the specialized instructions.\n"
        f"   b. Read the entire codebase.\n"
        f"   c. Adopt that agent's persona and produce the analysis.\n"
        f"   d. Call save_agent_result with your output.\n"
        f"3. After all 4 agents complete, synthesize a unified report:\n"
        f"   - Top 3 critical findings across all agents\n"
        f"   - Where agents agree vs. disagree\n"
        f"   - GO / CONDITIONAL GO / NO-GO recommendation\n"
        f"   - Top 5 action items in priority order\n"
        f"\nThe dashboard is live at http://localhost:{DASHBOARD_PORT}\n"
    )


@mcp.prompt()
def quick_health_check(repo_path: str) -> str:
    """Quick technical + adversarial health check."""
    return (
        f"Quick health check on: {repo_path}\n\n"
        f"1. Call start_analysis.\n"
        f"2. Run only 'technical' and 'adversarial' agents.\n"
        f"3. Summarize: architecture scores, top 3 risks, urgent action items.\n"
    )


@mcp.prompt()
def investment_due_diligence(repo_path: str) -> str:
    """Investment-focused analysis with business + financial agents."""
    return (
        f"Investment due diligence on: {repo_path}\n\n"
        f"1. Call start_analysis.\n"
        f"2. Run 'business' and 'financial' agents.\n"
        f"3. Synthesize into an investment memo.\n"
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENTRYPOINT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def main():
    """Run the OmniLabs MCP server with live dashboard."""
    try:
        start_dashboard()
        print(f"OmniLabs dashboard: http://localhost:{DASHBOARD_PORT}", file=sys.stderr)
    except OSError:
        print(f"Dashboard port {DASHBOARD_PORT} in use, skipping.", file=sys.stderr)

    mcp.run()


if __name__ == "__main__":
    main()
