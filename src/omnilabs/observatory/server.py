"""Local HTTP + SSE server for OmniLabs Observatory.

Serves the dashboard at http://localhost:3141 and exposes:
  GET /              → dashboard HTML
  GET /api/info      → {project_path, version}
  GET /api/sessions  → list of sessions
  GET /api/sessions/<id>/events  → tool events for a session
  GET /api/sessions/<id>/runs    → agent runs for a session
  GET /api/sessions/<id>/edits   → file edits for a session
  GET /api/discovered            → agents discovered for a project
  GET /api/live                  → SSE stream of new tool events
"""

from __future__ import annotations

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .store import (
    get_discovered,
    get_events_since,
    init_db,
    list_agent_runs,
    list_events,
    list_file_edits,
    list_sessions,
)

PORT = 3141
_DASHBOARD = Path(__file__).parent.parent / "dashboard" / "index.html"

# Set by start() so /api/info can return it
_project_path: str = ""


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass  # suppress access logs

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        qs = parse_qs(parsed.query)

        if path == "/":
            self._html()
        elif path == "/api/info":
            self._json({"project_path": _project_path, "version": "2.0"})
        elif path == "/api/sessions":
            self._json(list_sessions(limit=50))
        elif path == "/api/live":
            self._sse()
        elif path.startswith("/api/sessions/"):
            parts = path.split("/")  # ['','api','sessions','<id>','<sub>']
            if len(parts) >= 5:
                sid = parts[3]
                sub = parts[4] if len(parts) > 4 else ""
                limit = int(qs.get("limit", ["500"])[0])
                if sub == "events":
                    self._json(list_events(sid, limit=limit))
                elif sub == "runs":
                    self._json(list_agent_runs(sid))
                elif sub == "edits":
                    self._json(list_file_edits(sid))
                else:
                    self.send_error(404)
            else:
                self.send_error(404)
        elif path == "/api/discovered":
            project = qs.get("project", [_project_path])[0]
            self._json(get_discovered(project))
        else:
            self.send_error(404)

    def _html(self):
        body = _DASHBOARD.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, data):
        body = json.dumps(data, default=str).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _sse(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        # Backfill last 2 minutes of events on connect
        last_ts = time.time() - 120
        try:
            while True:
                events = get_events_since(last_ts)
                for evt in events:
                    payload = json.dumps(evt, default=str)
                    self.wfile.write(f"data: {payload}\n\n".encode())
                    last_ts = max(last_ts, evt["started_at"] + 0.001)
                self.wfile.flush()
                time.sleep(0.5)
        except (BrokenPipeError, ConnectionResetError):
            pass


def start(port: int = PORT, project_path: str = "", daemon: bool = True) -> HTTPServer:
    """Start the observatory HTTP server in a background thread."""
    global _project_path
    _project_path = project_path
    init_db()
    server = HTTPServer(("127.0.0.1", port), _Handler)
    t = threading.Thread(target=server.serve_forever, daemon=daemon)
    t.start()
    return server
