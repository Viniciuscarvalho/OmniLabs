"""OmniLabs MCP Server v0.4 — Selective execution, token-aware.

Principle: you choose which agents run. Nothing runs by default.
The hub holds 18+ agents but you pick 1, 2, or 5 per task.

Flow:
  1. list_agents / recommend_agents → see what's available
  2. plan_analysis → preview token cost before committing
  3. run_agent → execute ONE agent at a time (you control the sequence)
  4. save_agent_result → store output, update dashboard
  5. Repeat 3-4 for each agent you want
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

# ──────────────────────────────────────────────
# Presets — named groups of agents
# ──────────────────────────────────────────────

PRESETS: dict[str, dict[str, Any]] = {
    "core": {
        "agents": ["business", "financial", "technical", "adversarial"],
        "description": "The 4 foundational OmniLabs agents",
    },
    "health-check": {
        "agents": ["technical", "adversarial"],
        "description": "Quick architecture + risk review",
    },
    "due-diligence": {
        "agents": ["business", "financial", "adversarial"],
        "description": "Investment-focused analysis",
    },
    "marketing": {
        "agents": [a for a in registry.ids() if registry.get(a) and "marketing" in registry.get(a).tags],
        "description": "All marketing specialist agents",
    },
    "gtm": {
        "agents": ["business", "gtm-strategist", "product-marketing-manager", "copywriter"],
        "description": "Go-to-market readiness",
    },
}

# Filter presets to only include agents that actually exist
for _pn, _pd in PRESETS.items():
    _pd["agents"] = [a for a in _pd["agents"] if a in registry]


mcp = FastMCP(
    "OmniLabs",
    instructions=(
        f"Hub of {len(registry)} specialized AI agents. "
        "You choose which agents to run — nothing runs by default. "
        "Use list_agents to browse, recommend_agents to get suggestions, "
        "plan_analysis to preview cost, run_agent to execute one at a time. "
        f"Dashboard: http://localhost:{DASHBOARD_PORT}"
    ),
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOLS — Discovery
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@mcp.tool()
def list_agents(tag: str | None = None) -> dict[str, Any]:
    """Browse all agents in the hub with focus, tags, and token cost.

    Args:
        tag: Filter by tag (e.g. "core", "marketing", "engineering").
    """
    agents = registry.all()
    if tag:
        agents = [a for a in agents if tag in a.tags]
    return {
        "total": len(agents),
        "agents": [a.to_catalog_entry() for a in agents],
        "available_tags": sorted({t for a in registry for t in a.tags}),
        "presets": {k: v["description"] for k, v in PRESETS.items() if v["agents"]},
    }


@mcp.tool()
def recommend_agents(task: str) -> dict[str, Any]:
    """Suggest which agents to run based on a task description.

    Args:
        task: What you want to do, e.g. "check production readiness",
              "improve marketing", "review for investors".
    """
    task_lower = task.lower()
    scored: list[tuple[int, dict]] = []

    patterns = {
        "investor": ["business", "financial", "adversarial"],
        "invest": ["business", "financial", "adversarial"],
        "due diligence": ["business", "financial", "adversarial"],
        "production": ["technical", "adversarial"],
        "deploy": ["technical"],
        "scale": ["technical", "financial"],
        "security": ["technical"],
        "marketing": [a.id for a in registry if "marketing" in a.tags],
        "gtm": ["business", "gtm-strategist", "product-marketing-manager"],
        "go to market": ["business", "gtm-strategist", "product-marketing-manager"],
        "launch": ["business", "gtm-strategist", "copywriter"],
        "seo": ["seo-strategist", "content-strategist"],
        "content": ["content-strategist", "copywriter"],
        "social": ["social-media-manager", "community-manager"],
        "email": ["email-marketing-specialist"],
        "cost": ["financial"],
        "architecture": ["technical"],
        "risk": ["adversarial"],
        "health": ["technical", "adversarial"],
    }

    for spec in registry:
        score = 0
        # Pattern matching
        for pattern, ids in patterns.items():
            if pattern in task_lower and spec.id in ids:
                score += 5
        # Keyword matching against focus and name
        for word in task_lower.split():
            if len(word) > 3:
                if word in spec.focus.lower():
                    score += 2
                if word in spec.name.lower():
                    score += 2
                for tag in spec.tags:
                    if word in tag:
                        score += 3

        if score > 0:
            scored.append((score, {
                "agent": spec.id,
                "icon": spec.icon,
                "name": spec.name,
                "cost_tier": spec.cost_tier,
                "prompt_tokens": spec.prompt_tokens_estimate,
            }))

    scored.sort(key=lambda x: x[0], reverse=True)
    recs = [item for _, item in scored]

    if not recs:
        recs = [
            {"agent": s.id, "icon": s.icon, "name": s.name,
             "cost_tier": s.cost_tier, "prompt_tokens": s.prompt_tokens_estimate}
            for s in [registry.get("technical"), registry.get("adversarial")]
            if s
        ]

    ids = [r["agent"] for r in recs]
    total = sum(r["prompt_tokens"] for r in recs)

    return {
        "task": task,
        "recommended": recs,
        "total_prompt_tokens": total,
        "next_step": f"plan_analysis(repo_path, agents={ids})",
    }


@mcp.tool()
def list_presets() -> dict[str, Any]:
    """Show named agent presets (shortcuts for common scenarios)."""
    result = {}
    for name, data in PRESETS.items():
        if not data["agents"]:
            continue
        total = sum(registry.get(a).prompt_tokens_estimate for a in data["agents"] if registry.get(a))
        result[name] = {
            "description": data["description"],
            "agents": data["agents"],
            "count": len(data["agents"]),
            "total_prompt_tokens": total,
        }
    return result


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOLS — Planning
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@mcp.tool()
def plan_analysis(
    repo_path: str,
    agents: list[str] | None = None,
    preset: str | None = None,
) -> dict[str, Any]:
    """Preview token cost BEFORE running anything.

    You must specify agents or a preset. Nothing runs by default.

    Args:
        repo_path: Path to the repository.
        agents: Explicit agent IDs to run.
        preset: Named preset (e.g. "core", "health-check", "marketing").
    """
    agent_ids = _resolve_agents(agents, preset)
    if isinstance(agent_ids, dict):
        return agent_ids  # error

    plan = []
    total = 0
    for aid in agent_ids:
        spec = registry.get(aid)
        t = spec.prompt_tokens_estimate
        total += t
        plan.append({"agent": aid, "icon": spec.icon, "cost_tier": spec.cost_tier, "prompt_tokens": t})

    return {
        "repo_path": repo_path,
        "agents": plan,
        "count": len(plan),
        "total_prompt_tokens": total,
        "note": "Prompt cost only. Codebase reading + output adds more.",
        "next_step": f"start_analysis('{repo_path}', agents={agent_ids})",
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOLS — Execution (one at a time)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@mcp.tool()
def start_analysis(
    repo_path: str,
    agents: list[str] | None = None,
    preset: str | None = None,
) -> dict[str, Any]:
    """Start a session with SPECIFIC agents. Nothing runs by default.

    Args:
        repo_path: Path to the repository.
        agents: Explicit agent IDs.
        preset: Named preset.
    """
    agent_ids = _resolve_agents(agents, preset)
    if isinstance(agent_ids, dict):
        return agent_ids

    session = store.create_session(repo_path, agent_ids)
    queue = [f"{registry.get(a).icon} {a}" if registry.get(a) else a for a in agent_ids]

    return {
        "session_id": session.session_id,
        "target_repo": repo_path,
        "queue": queue,
        "count": len(agent_ids),
        "dashboard": f"http://localhost:{DASHBOARD_PORT}",
        "next_step": f"run_agent('{agent_ids[0]}')",
    }


@mcp.tool()
def run_agent(agent: str, session_id: str | None = None) -> dict[str, Any]:
    """Run ONE agent. Returns its specialized prompt.

    You (Claude Code) adopt this persona, read the codebase,
    produce the analysis, then call save_agent_result.

    Args:
        agent: Agent ID to execute.
        session_id: Session. Defaults to current.
    """
    spec = registry.get(agent)
    if spec is None:
        return {"error": f"Unknown agent '{agent}'.", "available": registry.ids()}

    session = store.get_session(session_id) if session_id else store.current_session
    if session is None:
        return {"error": "No active session. Call start_analysis first."}

    store.mark_running(session.session_id, agent)
    remaining = [aid for aid, r in session.agents.items() if r.status.value == "idle" and aid != agent]

    return {
        "agent": spec.id,
        "name": spec.name,
        "icon": spec.icon,
        "session_id": session.session_id,
        "target_repo": session.target_repo,
        "prompt_tokens": spec.prompt_tokens_estimate,
        "system_prompt": spec.system_prompt,
        "instructions": (
            f"You are now the OmniLabs {spec.name} agent ({spec.icon}). "
            f"Read the entire codebase at {session.target_repo}, then follow "
            f"the system prompt above. "
            f"Every finding MUST cite specific files and code as evidence. "
            f"When done, call save_agent_result with your output."
        ),
        "remaining_queue": remaining or "Last agent.",
    }


@mcp.tool()
def save_agent_result(
    agent: str,
    analysis: str,
    summary: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Save completed analysis. Shows what's next in the queue."""
    session = store.get_session(session_id) if session_id else store.current_session
    if session is None:
        return {"error": "No active session."}

    if summary is None:
        summary = analysis[:200] + "..." if len(analysis) > 200 else analysis

    store.save_result(session.session_id, agent, summary, analysis)
    r = session.agents.get(agent)

    remaining = [aid for aid, ar in session.agents.items() if ar.status.value == "idle"]
    completed = [aid for aid, ar in session.agents.items() if ar.status.value == "completed"]

    result: dict[str, Any] = {
        "agent": agent,
        "status": "completed",
        "duration_seconds": r.duration_seconds if r else None,
        "completed": completed,
        "dashboard": f"http://localhost:{DASHBOARD_PORT}",
    }

    if remaining:
        result["remaining"] = remaining
        result["next_step"] = f"run_agent('{remaining[0]}')"
    else:
        result["all_done"] = True
        result["next_step"] = "All agents done. Synthesize a unified report."

    return result


@mcp.tool()
def mark_agent_error(agent: str, error: str, session_id: str | None = None) -> dict[str, Any]:
    """Mark agent as failed and skip to next."""
    session = store.get_session(session_id) if session_id else store.current_session
    if session is None:
        return {"error": "No active session."}
    store.mark_failed(session.session_id, agent, error)
    remaining = [aid for aid, ar in session.agents.items() if ar.status.value == "idle"]
    result: dict[str, Any] = {"agent": agent, "status": "failed", "error": error}
    if remaining:
        result["next_step"] = f"run_agent('{remaining[0]}')"
    return result


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOOLS — Query
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@mcp.tool()
def get_session_status(session_id: str | None = None) -> dict[str, Any]:
    """Check status of all agents in current session."""
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
    if not r:
        return {"error": f"'{agent}' not in session."}
    if r.status == AgentStatus.IDLE:
        return {"status": "idle"}
    if r.status == AgentStatus.RUNNING:
        return {"status": "running"}
    return {"agent": agent, "status": r.status.value, "duration_seconds": r.duration_seconds,
            "output": r.raw_output, "error": r.error}


@mcp.tool()
def list_sessions() -> list[dict]:
    """List all analysis sessions."""
    return store.list_sessions() or [{"message": "No sessions yet."}]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RESOURCES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@mcp.resource("omnilabs://agents/catalog")
def agents_catalog() -> str:
    return json.dumps({"agents": [s.to_catalog_entry() for s in registry],
                       "total": len(registry),
                       "presets": {k: v for k, v in PRESETS.items() if v["agents"]}}, indent=2)


@mcp.resource("omnilabs://session/current")
def current_session_resource() -> str:
    s = store.current_session
    return s.to_json() if s else json.dumps({"message": "No active session."})


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PROMPTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@mcp.prompt()
def analyze(repo_path: str, agents: str) -> str:
    """Run specific agents on a project (comma-separated)."""
    ids = [a.strip() for a in agents.split(",")]
    return (f"Analyze {repo_path} with: {agents}\n\n"
            f"1. plan_analysis('{repo_path}', agents={ids})\n"
            f"2. start_analysis('{repo_path}', agents={ids})\n"
            f"3. run_agent → analyze → save_agent_result (one at a time)\n"
            f"4. Synthesize unified report.\n")


@mcp.prompt()
def analyze_with_preset(repo_path: str, preset: str) -> str:
    """Run a preset group of agents."""
    return (f"Analyze {repo_path} with preset '{preset}'\n\n"
            f"1. plan_analysis('{repo_path}', preset='{preset}')\n"
            f"2. start_analysis('{repo_path}', preset='{preset}')\n"
            f"3. Run each agent one by one.\n")


@mcp.prompt()
def smart_analyze(repo_path: str, goal: str) -> str:
    """Let OmniLabs recommend agents based on your goal."""
    return (f"Analyze {repo_path}\nGoal: {goal}\n\n"
            f"1. recommend_agents('{goal}')\n"
            f"2. Review recommendations, select agents.\n"
            f"3. plan_analysis → start_analysis → run one at a time.\n")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HELPERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def _resolve_agents(agents: list[str] | None, preset: str | None) -> list[str] | dict:
    """Resolve agent list from explicit IDs or preset. Returns error dict on failure."""
    if agents:
        unknown = [a for a in agents if a not in registry]
        if unknown:
            return {"error": f"Unknown agents: {unknown}", "available": registry.ids()}
        return agents
    elif preset:
        if preset not in PRESETS or not PRESETS[preset]["agents"]:
            return {"error": f"Unknown preset '{preset}'.", "available": list(PRESETS.keys())}
        return PRESETS[preset]["agents"]
    else:
        return {
            "error": "You must specify which agents to run.",
            "options": {
                "agents": "agents=['technical', 'adversarial']",
                "preset": "preset='core' or preset='health-check'",
                "discover": "Run list_agents or recommend_agents first.",
            },
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENTRYPOINT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def main():
    meta = {s.id: {"icon": s.icon, "focus": s.focus, "tags": s.tags,
                    "cost_tier": s.cost_tier, "prompt_tokens": s.prompt_tokens_estimate}
            for s in registry}
    write_agents_meta(meta)
    try:
        start_dashboard()
        print(f"OmniLabs dashboard: http://localhost:{DASHBOARD_PORT}", file=sys.stderr)
    except OSError:
        print(f"Dashboard port {DASHBOARD_PORT} in use, skipping.", file=sys.stderr)
    agents_str = ", ".join(f"{s.icon} {s.id}" for s in registry)
    print(f"Hub ({len(registry)} agents): {agents_str}", file=sys.stderr)
    mcp.run()


if __name__ == "__main__":
    main()
