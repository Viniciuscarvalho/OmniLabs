"""OmniLabs CLI — omnilabs <command> [args]"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="omnilabs",
        description="OmniLabs — agent observatory for Claude Code",
    )
    sub = parser.add_subparsers(dest="command", metavar="<command>")

    # record — called by hooks
    p_rec = sub.add_parser("record", help="Record a hook event (called by Claude Code hooks)")
    p_rec.add_argument("event_type", help="Hook event name (e.g. PreToolUse)")

    # watch
    p_watch = sub.add_parser("watch", help="Start observer + dashboard at http://localhost:3141")
    p_watch.add_argument("--port", type=int, default=3141, metavar="PORT")
    p_watch.add_argument("--no-browser", action="store_true", help="Don't open browser automatically")

    # hooks
    p_hooks = sub.add_parser("hooks", help="Manage Claude Code capture hooks")
    hs = p_hooks.add_subparsers(dest="hooks_cmd", metavar="<action>")
    p_hi = hs.add_parser("install", help="Install capture hooks")
    p_hi.add_argument("--project", action="store_true", help="Install in project .claude/settings.json")
    p_hu = hs.add_parser("uninstall", help="Remove hooks and restore backup")
    p_hu.add_argument("--project", action="store_true")
    hs.add_parser("status", help="Show hook installation status")

    # agents
    p_agents = sub.add_parser("agents", help="Browse discovered agents in the project")
    ag = p_agents.add_subparsers(dest="agents_cmd", metavar="<action>")
    p_al = ag.add_parser("list", help="List all discovered agents/skills/packs")
    p_al.add_argument("--path", default=None, metavar="DIR", help="Project directory (default: cwd)")

    # pack
    p_pack = sub.add_parser("pack", help="Manage OmniLabs agent packs")
    pk = p_pack.add_subparsers(dest="pack_cmd", metavar="<action>")
    pk.add_parser("list", help="List available packs")
    p_pi = pk.add_parser("install", help="Install a pack into .claude/agents/")
    p_pi.add_argument("pack_name", help="Pack name (e.g. strategic-analysis)")
    p_pi.add_argument("--path", default=None, metavar="DIR", help="Project directory (default: cwd)")

    # sessions
    p_sess = sub.add_parser("sessions", help="Browse captured sessions")
    ss = p_sess.add_subparsers(dest="sessions_cmd", metavar="<action>")
    p_sl = ss.add_parser("list", help="List recent sessions")
    p_sl.add_argument("--project", action="store_true", help="Filter to current directory only")
    p_sl.add_argument("-n", type=int, default=20, metavar="N")

    # events
    p_evt = sub.add_parser("events", help="Browse captured tool events")
    es = p_evt.add_subparsers(dest="events_cmd", metavar="<action>")
    p_el = es.add_parser("list", help="List events for a session")
    p_el.add_argument("session_id", help="Session ID from 'sessions list'")
    p_el.add_argument("-n", type=int, default=50, metavar="N")

    # gc
    p_gc = sub.add_parser("gc", help="Prune old events and blobs")
    p_gc.add_argument("--older-than", default="30d", metavar="AGE",
                      help="Remove events older than this (e.g. 30d, 7d)")

    args = parser.parse_args()

    if args.command == "record":
        _cmd_record(args.event_type)
    elif args.command == "watch":
        _cmd_watch(args)
    elif args.command == "hooks":
        _cmd_hooks(args)
    elif args.command == "agents":
        _cmd_agents(args)
    elif args.command == "pack":
        _cmd_pack(args)
    elif args.command == "sessions":
        _cmd_sessions(args)
    elif args.command == "events":
        _cmd_events(args)
    elif args.command == "gc":
        _cmd_gc(args)
    else:
        parser.print_help()


def _cmd_record(event_type: str) -> None:
    from .observatory.recorder import main as record_main
    sys.argv = ["omnilabs", event_type]
    record_main()


def _cmd_watch(args: argparse.Namespace) -> None:
    import signal
    import webbrowser
    from .observatory import discovery, server
    from .observatory.hooks import status as hook_status

    project_path = os.getcwd()
    port = args.port

    # Warn if hooks not installed
    proj_status = hook_status(project=True)
    if not proj_status.get("PreToolUse"):
        print("Warning: capture hooks not installed for this project.")
        print("Run: omnilabs hooks install --project  (then restart Claude Code)")
        print()

    # Run discovery
    found = discovery.scan(project_path)
    discovery.save(found, project_path)
    if found:
        print(f"Discovered {len(found)} agents/skills in this project.")

    # Start server
    srv = server.start(port=port, project_path=project_path, daemon=True)
    url = f"http://localhost:{port}"
    print(f"Observatory running at {url}")

    if not getattr(args, "no_browser", False):
        try:
            webbrowser.open(url)
        except Exception:
            pass

    print("Press Ctrl+C to stop.")

    def _stop(sig, frame):
        print("\nStopping observatory…")
        srv.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    # Block the main thread
    import time
    while True:
        time.sleep(1)


def _cmd_hooks(args: argparse.Namespace) -> None:
    from .observatory.hooks import install, status, uninstall

    cmd = getattr(args, "hooks_cmd", None)
    project = getattr(args, "project", False)

    if cmd == "install":
        path = install(project=project)
        scope = "project" if project else "user"
        print(f"Hooks installed ({scope}): {path}")
        print("Restart Claude Code to activate capture.")
    elif cmd == "uninstall":
        path = uninstall(project=project)
        print(f"Hooks removed: {path}")
    elif cmd == "status":
        for label, proj in [("User settings", False), ("Project settings", True)]:
            installed = status(project=proj)
            print(f"\n{label}:")
            for event, active in installed.items():
                print(f"  {'[+]' if active else '[-]'} {event}")
    else:
        print("Usage: omnilabs hooks <install|uninstall|status>")


def _cmd_agents(args: argparse.Namespace) -> None:
    from .observatory import discovery

    if getattr(args, "agents_cmd", None) != "list":
        print("Usage: omnilabs agents list [--path DIR]")
        return

    project_path = getattr(args, "path", None) or os.getcwd()
    found = discovery.scan(project_path)

    if not found:
        print("No agents or skills discovered.")
        print("Make sure you're in a Claude Code project directory.")
        return

    # Group by source_type
    by_type: dict[str, list[dict]] = {}
    for a in found:
        by_type.setdefault(a["source_type"], []).append(a)

    type_labels = {
        "subagent":         "Project subagents (.claude/agents/)",
        "project-skill":    "Project skills (.claude/skills/)",
        "user-skill":       "User skills (~/.claude/skills/)",
        "omnilabs-pack":    "OmniLabs pack (strategic-analysis)",
    }

    total = 0
    for stype, agents in sorted(by_type.items()):
        label = type_labels.get(stype, stype)
        print(f"\n{label}  ({len(agents)})")
        for a in agents:
            print(f"  {a['agent_id']:<28}  {a['name']}")
        total += len(agents)

    print(f"\nTotal: {total} agents/skills")


def _cmd_pack(args: argparse.Namespace) -> None:
    cmd = getattr(args, "pack_cmd", None)

    if cmd == "list":
        _pack_list()
    elif cmd == "install":
        _pack_install(args.pack_name, getattr(args, "path", None) or os.getcwd())
    else:
        print("Usage: omnilabs pack <list|install> [pack-name]")


def _pack_list() -> None:
    from .agents.registry import BUILTIN_PACK_DIR
    from pathlib import Path

    print("Built-in packs:")
    pack_root = BUILTIN_PACK_DIR.parent
    for d in sorted(pack_root.iterdir()):
        if d.is_dir() and not d.name.startswith("_"):
            yamls = list(d.glob("*.yaml"))
            name = d.name.replace("_", "-")
            print(f"  {name:<30}  {len(yamls)} agents  ({d})")

    user_packs = Path.home() / ".omnilabs" / "packs"
    if user_packs.is_dir():
        print("\nUser packs (~/.omnilabs/packs/):")
        for d in sorted(user_packs.iterdir()):
            if d.is_dir():
                yamls = list(d.glob("*.yaml"))
                print(f"  {d.name:<30}  {len(yamls)} agents")


def _pack_install(pack_name: str, project_path: str) -> None:
    """Install a pack's agents as Claude Code subagents in .claude/agents/."""
    from pathlib import Path
    from .agents.registry import BUILTIN_PACK_DIR, _load_yaml_agent

    pack_slug = pack_name.replace("-", "_")
    pack_dir = BUILTIN_PACK_DIR.parent / pack_slug

    if not pack_dir.is_dir():
        # Try user packs
        pack_dir = Path.home() / ".omnilabs" / "packs" / pack_slug
    if not pack_dir.is_dir():
        pack_dir = Path.home() / ".omnilabs" / "packs" / pack_name

    if not pack_dir.is_dir():
        print(f"Pack not found: {pack_name}")
        print("Run 'omnilabs pack list' to see available packs.")
        return

    agents_dir = Path(project_path) / ".claude" / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)

    installed = []
    for yaml_path in sorted(pack_dir.glob("*.yaml")):
        try:
            spec = _load_yaml_agent(yaml_path)
        except Exception as e:
            print(f"  Skip {yaml_path.name}: {e}")
            continue

        md_path = agents_dir / f"{spec.id}.md"
        md_content = _spec_to_md(spec)
        md_path.write_text(md_content, encoding="utf-8")
        installed.append(spec.id)
        print(f"  Installed: {spec.icon} {spec.name}  →  {md_path}")

    if installed:
        print(f"\n{len(installed)} agents installed into {agents_dir}")
        print("They are now discoverable by the observatory.")
    else:
        print("No agents installed.")


def _spec_to_md(spec) -> str:
    """Convert an AgentSpec to Claude Code subagent markdown format."""
    tools = "Read, Grep, Glob, Bash"
    return f"""---
name: {spec.id}
description: |
  {spec.focus}
model: sonnet
color: purple
tools: {tools}
---

{spec.system_prompt}
"""


def _cmd_sessions(args: argparse.Namespace) -> None:
    from .observatory.store import init_db, list_sessions

    if getattr(args, "sessions_cmd", None) != "list":
        print("Usage: omnilabs sessions list [--project] [-n N]")
        return

    init_db()
    project_path = os.getcwd() if getattr(args, "project", False) else None
    sessions = list_sessions(project_path=project_path, limit=args.n)

    if not sessions:
        print("No sessions captured yet.")
        print("Install hooks first: omnilabs hooks install --project")
        return

    print(f"\n{'SESSION ID':<36}  {'PROJECT':<38}  {'STARTED':<20}  STATUS")
    print("-" * 104)
    for s in sessions:
        started = datetime.fromtimestamp(s["started_at"]).strftime("%Y-%m-%d %H:%M:%S")
        proj = s["project_path"]
        proj = ("..." + proj[-35:]) if len(proj) > 38 else proj
        sid = s["id"][:34]
        print(f"{sid:<36}  {proj:<38}  {started:<20}  {s['status']}")


def _cmd_events(args: argparse.Namespace) -> None:
    from .observatory.store import init_db, list_events

    if getattr(args, "events_cmd", None) != "list":
        print("Usage: omnilabs events list <session_id> [-n N]")
        return

    init_db()
    events = list_events(args.session_id, limit=args.n)

    if not events:
        print(f"No events found for session: {args.session_id}")
        return

    print(f"\n{'TOOL':<20}  {'AGENT':<16}  {'ARGS':<45}  {'TIME':<12}  DURATION")
    print("-" * 116)
    for e in events:
        t = datetime.fromtimestamp(e["started_at"]).strftime("%H:%M:%S.%f")[:-3]
        args_str = (e["args_json"] or "")[:43]
        dur = f"{e['duration_ms']:.0f}ms" if e["duration_ms"] else "—"
        agent = (e["agent_type"] or e["claude_agent_id"] or "root")[:14]
        print(f"{e['tool_name']:<20}  {agent:<16}  {args_str:<45}  {t:<12}  {dur}")


def _cmd_gc(args: argparse.Namespace) -> None:
    import time
    import re
    from .observatory.store import _connect, init_db

    age_str = getattr(args, "older_than", "30d")
    m = re.match(r'^(\d+)([dh])$', age_str)
    if not m:
        print(f"Invalid age format: {age_str}  (use e.g. 30d or 12h)")
        return

    n, unit = int(m.group(1)), m.group(2)
    seconds = n * (86400 if unit == "d" else 3600)
    cutoff = time.time() - seconds

    init_db()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT COUNT(*) FROM sessions WHERE started_at < ?", (cutoff,)
        ).fetchone()[0]
        conn.execute(
            """DELETE FROM tool_events WHERE run_id IN (
               SELECT ar.id FROM agent_runs ar
               JOIN sessions s ON ar.session_id=s.id WHERE s.started_at < ?)""",
            (cutoff,),
        )
        conn.execute(
            """DELETE FROM file_edits WHERE run_id IN (
               SELECT ar.id FROM agent_runs ar
               JOIN sessions s ON ar.session_id=s.id WHERE s.started_at < ?)""",
            (cutoff,),
        )
        conn.execute(
            """DELETE FROM agent_runs WHERE session_id IN (
               SELECT id FROM sessions WHERE started_at < ?)""",
            (cutoff,),
        )
        conn.execute("DELETE FROM sessions WHERE started_at < ?", (cutoff,))

    print(f"Removed {rows} sessions older than {age_str}.")
