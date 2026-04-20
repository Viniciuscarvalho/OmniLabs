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
    p_rec = sub.add_parser("record", help="Record a hook event (internal, called by Claude Code hooks)")
    p_rec.add_argument("event_type", help="Hook event name (e.g. PreToolUse)")

    # hooks
    p_hooks = sub.add_parser("hooks", help="Manage Claude Code capture hooks")
    hs = p_hooks.add_subparsers(dest="hooks_cmd", metavar="<action>")
    p_hi = hs.add_parser("install", help="Install capture hooks")
    p_hi.add_argument("--project", action="store_true", help="Install in project .claude/settings.json")
    p_hu = hs.add_parser("uninstall", help="Remove hooks and restore backup")
    p_hu.add_argument("--project", action="store_true")
    hs.add_parser("status", help="Show hook installation status")

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

    # watch (stub — Phase 3)
    sub.add_parser("watch", help="Start observer + dashboard (Phase 3)")

    args = parser.parse_args()

    if args.command == "record":
        _cmd_record(args.event_type)
    elif args.command == "hooks":
        _cmd_hooks(args)
    elif args.command == "sessions":
        _cmd_sessions(args)
    elif args.command == "events":
        _cmd_events(args)
    elif args.command == "watch":
        _cmd_watch()
    else:
        parser.print_help()


def _cmd_record(event_type: str) -> None:
    from .observatory.recorder import main as record_main
    sys.argv = ["omnilabs", event_type]
    record_main()


def _cmd_hooks(args: argparse.Namespace) -> None:
    from .observatory.hooks import install, uninstall, status

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
                mark = "+" if active else "-"
                print(f"  [{mark}] {event}")
    else:
        print("Usage: omnilabs hooks <install|uninstall|status>")


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


def _cmd_watch() -> None:
    print("Dashboard coming in Phase 3.")
    print()
    print("Current capture status:")
    from .observatory.hooks import status
    for event, active in status(project=True).items():
        print(f"  {'[+]' if active else '[-]'} {event}")
    print()
    print("Start capturing: omnilabs hooks install --project")
    print("View sessions:   omnilabs sessions list")
